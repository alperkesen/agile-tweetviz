import os
import unittest
from TweetViz import app, db
from flask_recaptcha import ReCaptcha
from flask import session
from TweetViz.models import User
from werkzeug.security import generate_password_hash

TEST_DB = 'test.db'

class AuthTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(app.config['BASEDIR'], TEST_DB)
        
        self.app = app.test_client()

        db.drop_all()
        db.create_all()

        new_user = User(username="test123", password=generate_password_hash("test123", method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        self.assertEqual(app.debug, False)

    def tearDown(self):
        pass

    def test_register_user(self):
        response = self.app.post('/register',
                                 data=dict(username="johndoe",
                                           password="123456"),
                                 follow_redirects=True)
        self.assertIn(b"You can login now with you credentials", response.data)
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        response = self.app.post('/login',
                                 data=dict(username="test123",
                                           password="test123"),
                                 follow_redirects=True)
        self.assertIn(b"Welcome", response.data)
        self.assertEqual(response.status_code, 200)
 
if __name__ == "__main__":
    unittest.main()
