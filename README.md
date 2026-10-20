# OneDown Solution + Ankaboot.ai

A responsive, glass-style software-house website built with HTML, CSS, Bootstrap 5 and Flask. Includes the supplied blue/red OneDown logo, a new cyan/violet SVG identity for Ankaboot.ai, animated product illustrations, a working contact form and a private admin inbox.

## Quick start — Windows

Install Python 3.12+ if it is not installed. During installation, enable **Add Python to PATH**. Extract this ZIP, open the `onedown-solution` folder in a terminal (PowerShell or Command Prompt), then run:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe setup.py
.venv\Scripts\python.exe -m flask --app app:create_app create-admin
.venv\Scripts\python.exe -m flask --app app:create_app run
```

If `python` is not recognized either, install or repair Python from [python.org](https://www.python.org/downloads/windows/) with **Add Python to PATH** enabled, close and reopen the terminal, and try again. You do not need to activate the virtual environment when using the commands above.

When prompted, choose your admin username and a password of at least 12 characters. There is no default password. Password typing is hidden. You must create the administrator before you can sign in.

Open **http://127.0.0.1:5000** for the site and **http://127.0.0.1:5000/admin** for the inbox. Keep the terminal running; press Ctrl+C to stop.

For future runs, use `.venv\Scripts\python.exe -m flask --app app:create_app run` from the project folder. Alternatively double-click `start-windows.bat` after completing setup.

## macOS / Linux

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python setup.py
python -m flask --app app:create_app create-admin
python -m flask --app app:create_app run
```

## Pages and behavior

| Route | Purpose |
| --- | --- |
| `/` | OneDown home: web, mobile, custom software and business systems |
| `/ankaboot-ai` | Dedicated AI division: chatbots, ML, computer vision, data science |
| `/contact` | Validated enquiry form, service preselection and confirmation |
| `/privacy` | What this build collects and how to request deletion |
| `/admin/login` | Administrator authentication |
| `/admin` | Enquiry details, search, status filters, pagination and status updates |

The contact form **stores submissions in SQLite**; it does not send email notifications. Check the admin inbox to see new enquiries. Call and WhatsApp links use **Muhammad Khalid, 03012949584**, internationally formatted as +923012949584.

The AI use-case tabs are illustrative descriptions, not a connected chatbot or live AI model. No invented client lists, testimonials or performance claims are included.

## Administrator tasks

- Sign in at `/admin`, read all submitted fields and update the status to **New**, **In progress** or **Closed**.
- Search by name, email or message; filter by status. Each page holds 20 results.
- Times are stored and displayed in UTC.
- To reset a password, run `python -m flask --app app:create_app create-admin` using the same username.
- Sessions expire after two hours. Password reset does not immediately revoke other active sessions. Rotate `SECRET_KEY` and restart the app to invalidate all sessions if needed.
- To remove a contact record following a deletion request, back up the database, then use a SQLite administration tool to delete the selected enquiry by its exact `id`. The web inbox intentionally has no destructive bulk-delete button.

## Files to edit

- `templates/home.html`: main website content and service offerings.
- `templates/ai.html`: Ankaboot.ai content and example tabs.
- `templates/contact.html`, `templates/base.html`: contact text and links.
- `static/css/style.css`, `static/css/layout.css`: styling, responsive layouts, the homepage video hero and animations. Main colour variables are at the top.
- `static/img/onedown-logo.png`: original supplied logo, retained unchanged.
- `static/img/onedown-mark.svg`: new OneDown brand mark in sea-green, white and coral.
- `static/img/ankaboot-logo.svg`: new editable vector logo; neural-web geometry with an A motif and cyan/violet palette.
- `static/video/services-showreel.mp4`: looping homepage background video, with service labels overlaid in the hero.
- `app.py`: routes, validation, database and authentication.
- `static/vendor/`: bundled Bootstrap CSS and JS; no CDN request needed at runtime.

Animations respect `prefers-reduced-motion`. The layout uses Bootstrap's grid and navigation, with custom glass surfaces. Fonts use a local system stack. The site can run without external font, image or Bootstrap requests.

## Upload the source to GitHub

Create an empty repository in your GitHub account. From this project folder run:

```sh
git init
git add .
git commit -m "Build OneDown Solution and Ankaboot.ai website"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the placeholder username and repository name with yours. The `.gitignore` excludes `.env`, the database, virtual environments and caches. Verify those exclusions before pushing. No GitHub repository was created or uploaded as part of this download.

**GitHub Pages cannot run Flask or the admin inbox.** GitHub stores the source; deployment needs a Python-capable server with persistent disk storage.

## Production deployment

1. Use a Python host/server with a persistent filesystem for `instance/`. An ephemeral filesystem will lose your enquiries and admin account on redeployment.
2. Install `requirements.txt`. Generate a unique long `SECRET_KEY` with `python setup.py` or supply it as a hosting environment variable. Never publish it.
3. Set `APP_ENV=production` only when the site is served over HTTPS. This enables secure session cookies and HSTS. Keep `APP_ENV=development` for local HTTP.
4. Create the admin account on the deployed database using the CLI command above.
5. Run the app using Waitress, not Flask's development server:

```sh
waitress-serve --host=127.0.0.1 --port=8000 --call app:create_app
```

Put an HTTPS reverse proxy in front of port 8000. A container host may require `--host=0.0.0.0` and its assigned port instead; restrict direct server access appropriately.

6. Back up the SQLite database using SQLite's backup API or with the app stopped (WAL mode is enabled). Restrict filesystem access to `.env` and `instance/`.
7. Rate limits use the socket peer IP and ignore forwarding headers. Behind a reverse proxy, limits are shared by that proxy address. Configure trusted-proxy handling deliberately for your exact topology before public launch; never trust arbitrary `X-Forwarded-For` headers. Consider edge spam protection for a public campaign.
8. Review the privacy text and choose an enquiry retention policy for your business before public launch.

This initial SQLite build is intended for one application instance. For horizontal scaling or high traffic, migrate persistence and rate limiting to shared services.

## Tests

```sh
python -m unittest discover -s tests -v
```

Tests cover page rendering and static assets, form persistence and validation, CSRF enforcement, authenticated access, status updates, escaped enquiry text, search, rate limits, honeypot and pagination. Test data lives in temporary databases and is never shipped.

## Security included

Password hashing; no default credentials; CSRF on POST forms; parameterized SQL; autoescaped output; authenticated admin routes; login and contact throttling; HttpOnly/SameSite cookies; secure cookies in production; request size cap; security headers; no-store admin responses. Production hardening still depends on HTTPS, deployment configuration, backups and updates.

## Verification scope

The application is tested with Flask's test client. Browser screenshots and live deployment were not verified in this environment. Check the pages in Chrome/Firefox and on your phone before public launch.

## Third-party notices

Bootstrap 5.3.3 is distributed under the MIT license; see `static/vendor/BOOTSTRAP-LICENSE.txt`. The homepage background video is [Pexels video 3141208](https://www.pexels.com/video/3141208/), used under the [Pexels license](https://www.pexels.com/license/). Python dependencies retain their respective upstream licenses. The original OneDown logo is supplied by the owner. The new Ankaboot.ai identity is a design concept; no trademark or domain availability check was performed.
