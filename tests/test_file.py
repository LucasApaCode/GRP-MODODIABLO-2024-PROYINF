import unittest
import os
from app import app, db
from io import BytesIO
from models import User

class FileUploadTestCase(unittest.TestCase):
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

    def login(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertIn(b'Bienvenido', response.data)
        return response
    
    def test_upload_non_dcm_file(self):
        self.login()
        with open('test_files/test.txt', 'rb') as f:
            data = {
                'file': (BytesIO(f.read()), 'test.txt')
            }
            response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Tipo de archivo no permitido. Por favor, sube un archivo .dcm', response.data)

    def test_upload_dcm_file(self):
        self.login()

        with open('test_files/test.dcm', 'rb') as f:
            data = {
                'file': (BytesIO(f.read()), 'test.dcm')
            }
            response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Archivo DICOM subido y procesado correctamente.', response.data)


    def test_upload_non_dcm_file(self):
        self.login()
        with open('test_files/test.txt', 'rb') as f:
            data = {
                'file': (BytesIO(f.read()), 'test.txt')
            }
            response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Tipo de archivo no permitido. Por favor, sube un archivo .dcm', response.data)

if __name__ == '__main__':
    unittest.main()
