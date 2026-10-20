import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import SERVICES, create_app
from werkzeug.security import generate_password_hash

class WebsiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.temp.name) / 'test.sqlite3')
        self.app = create_app({'TESTING':True, 'SECRET_KEY':'test-only-secret', 'DATABASE':self.database})
        self.client = self.app.test_client()
        with sqlite3.connect(self.database) as db:
            db.execute('INSERT INTO admin(username,password_hash) VALUES (?,?)', ('testadmin',generate_password_hash('test-password-only-123')))

    def tearDown(self):
        self.temp.cleanup()

    def token(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code,200)
        return re.search(r'name="csrf_token" value="([^"]+)"',response.text).group(1)

    def enquiry(self, **changes):
        data = dict(csrf_token=self.token('/contact'),name='Test Client',email='test@example.com',phone='+92 301 0000000',service='Chatbot development',budget='Not sure yet',message='I would like a chatbot for customer support.',consent='yes',website='')
        data.update(changes)
        return self.client.post('/contact',data=data)

    def login(self):
        return self.client.post('/admin/login',data={'csrf_token':self.token('/admin/login'),'username':'testadmin','password':'test-password-only-123'})

    def test_pages_and_assets(self):
        for path in ('/','/ankaboot-ai','/contact','/privacy','/admin/login'):
            response = self.client.get(path)
            self.assertEqual(response.status_code,200,path)
            self.assertIn('Content-Security-Policy',response.headers)
            for asset in re.findall(r'(?:src|href)="(/static/[^\"]+)"',response.text):
                with self.client.get(asset) as asset_response:
                    self.assertEqual(asset_response.status_code,200,asset)
        home = self.client.get('/').text
        self.assertIn('AI that earns its place.', home)
        self.assertIn('href="/ankaboot-ai"', home)
        self.assertIn('img/onedown-mark.svg', home)
        self.assertIn('AI solutions', SERVICES)
        self.assertIn('Digital marketing', SERVICES)
        contact = self.client.get('/contact?service=AI+solutions').text
        self.assertIn('<option selected>AI solutions</option>', contact)
        self.assertIn('services-showreel.mp4', home)
        marketing_contact = self.client.get('/contact?service=Digital+marketing').text
        self.assertIn('<option selected>Digital marketing</option>', marketing_contact)
        self.assertEqual(self.client.get('/not-a-page').status_code,404)

    def test_contact_persistence(self):
        self.assertEqual(self.enquiry(service='AI solutions').status_code,302)
        with sqlite3.connect(self.database) as db:
            row = db.execute('SELECT name,service,status FROM enquiries').fetchone()
            self.assertEqual(row,('Test Client','AI solutions','New'))
        self.assertIn('Your enquiry has been saved',self.client.get('/contact').text)

    def test_invalid_fields_do_not_save(self):
        self.assertEqual(self.enquiry(email='bad',message='short',service='fake',consent='').status_code,400)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM enquiries').fetchone()[0],0)

    def test_csrf_is_required(self):
        self.assertEqual(self.client.post('/contact',data={'name':'Test'}).status_code,400)
        self.assertEqual(self.client.post('/admin/login',data={'username':'testadmin'}).status_code,400)

    def test_admin_access_and_status(self):
        self.enquiry()
        self.assertEqual(self.client.get('/admin').status_code,302)
        self.assertEqual(self.login().status_code,302)
        token = self.token('/admin')
        response = self.client.get('/admin')
        self.assertIn('Test Client',response.text)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        response = self.client.post('/admin/enquiries/1/status',data={'csrf_token':token,'status':'In progress'})
        self.assertEqual(response.status_code,302)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT status FROM enquiries').fetchone()[0],'In progress')
        self.assertEqual(self.client.post('/admin/enquiries/1/status',data={'csrf_token':token,'status':'Invalid'}).status_code,400)
        self.assertEqual(self.client.post('/admin/logout',data={'csrf_token':token}).status_code,302)
        self.assertEqual(self.client.get('/admin').status_code,302)

    def test_stored_html_escaped_and_search(self):
        self.enquiry(name='<script>alert(1)</script>',message='<script>alert(2)</script> This is a test message.')
        self.login()
        response = self.client.get('/admin?q=alert')
        self.assertIn('&lt;script&gt;',response.text)
        self.assertNotIn('<script>alert',response.text)
        self.assertIn('No enquiries here yet',self.client.get('/admin?q=doesnotexist').text)

    def test_throttles_and_wrong_password(self):
        token = self.token('/admin/login')
        for _ in range(5):
            response = self.client.post('/admin/login',data={'csrf_token':token,'username':'testadmin','password':'wrong'})
            self.assertIn('Incorrect username or password',response.text)
        self.assertEqual(self.client.post('/admin/login',data={'csrf_token':token}).status_code,429)
        self.assertEqual(self.client.get('/admin').status_code,302)
        for _ in range(5): self.assertEqual(self.enquiry().status_code,302)
        self.assertEqual(self.enquiry().status_code,429)

    def test_honeypot(self):
        self.assertEqual(self.enquiry(website='spam.example').status_code,400)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM enquiries').fetchone()[0],0)

    def test_admin_pagination(self):
        with sqlite3.connect(self.database) as db:
            db.executemany('INSERT INTO enquiries(name,email,phone,service,budget,message) VALUES (?,?,?,?,?,?)', [(f'Client {i}','test@example.com','','Custom software','Not sure yet','A project to discuss.') for i in range(22)])
        self.login()
        first=self.client.get('/admin').text
        second=self.client.get('/admin?page=2').text
        self.assertEqual(first.count('<article class="glass enquiry'),20)
        self.assertEqual(second.count('<article class="glass enquiry'),2)

if __name__ == '__main__':
    unittest.main()
