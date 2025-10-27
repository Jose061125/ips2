import sys
import os

# Asegurar que la raíz del proyecto esté en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import db, User

app = create_app({
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-key'
})

with app.app_context():
    db.create_all()
    u = User(username='testuser')
    u.set_password('testpass')
    db.session.add(u)
    db.session.commit()

    client = app.test_client()
    resp_get = client.get('/auth/login')
    print('GET /auth/login status:', resp_get.status_code)
    print(resp_get.data.decode()[:1000])

    resp_post = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    print('POST /auth/login status:', resp_post.status_code)
    print(resp_post.data.decode()[:1000])