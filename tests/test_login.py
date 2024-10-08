import unittest
import os
from app import app, db
from models import User



class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        cls.client = app.test_client()

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        with app.app_context():
            db.create_all()
            test_user = User(username='testuser', email='test@example.com', role='specialist')
            test_user.set_password('password')
            db.session.add(test_user)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                os.rmdir(app.config['UPLOAD_FOLDER'])
    
    def test_login_no_existe(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertIn('inválidos'.encode('utf-8'), response.data)
        return response


    def test_login_password_incorrecto(self):
        response = self.client.post('/login', data={
            'username': 'testuserr',
            'password': 'passwordd'
        }, follow_redirects=True)
        self.assertIn('inválidos'.encode('utf-8'), response.data)
        return response
        


# ...

if __name__ == "__main__":
    unittest.main()
