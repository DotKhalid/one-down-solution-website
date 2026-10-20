"""One-time configuration. Does not overwrite an existing .env."""
from pathlib import Path
import secrets
p = Path(__file__).resolve().parent / '.env'
if not p.exists():
    p.write_text('SECRET_KEY='+secrets.token_hex(32)+'\nAPP_ENV=development\n')
    try: p.chmod(0o600)
    except OSError: pass
    print('Configuration created. Next: python -m flask --app app:create_app create-admin')
else:
    print('.env already exists; retained without changes.')
