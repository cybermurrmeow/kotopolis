import os
from pathlib import Path
import subprocess
import sys


def test_login_rate_limit_in_separate_process():
    environment = dict(os.environ)
    environment.update(
        SECRET_KEY="limit-test-only",
        DATABASE_URL="sqlite:///:memory:",
        RATELIMIT_ENABLED="true",
        RATELIMIT_STORAGE_URI="memory://",
        COOKIE_SECURE="false",
    )
    code = """
from app import app
from models import db
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
with app.app_context():
    db.create_all()
client = app.test_client()
statuses = [client.post('/login', data={'username_or_email': 'missing', 'password': 'Wrong123'}).status_code for _ in range(11)]
assert statuses == [200] * 10 + [429], statuses
print('Single-process login rate limit passed')
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "rate limit passed" in result.stdout
