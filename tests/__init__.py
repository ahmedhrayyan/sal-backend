import unittest
from flask_jwt_extended import create_access_token
from app import create_app
from db.models import Question, Answer, User, Role, Notification
from config import TestingConfig
from io import BytesIO
from db import db


class SalTestCase(unittest.TestCase):
    """ This class represents Sal test case """

    def setUp(self):
        """ Executes before each test. Inti the app and define test variables """
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client

        # seed data
        self.role = Role(name='general')
        self.role.insert()
        self.user = User(first_name='Ahmed', last_name='Hamed', email='ahmedhrayyan@outlook.com',
                         username='ahmedhrayyan', password='secret', role_id=self.role.id)
        self.user.insert()
        self.question = Question(user_id=self.user.id, content='Is sal the best QA engine')
        self.question.insert()
        self.answer = Answer(user_id=self.user.id, question_id=self.question.id, content='Yes it is')
        self.answer.insert()
        self.notification = Notification(user_id=self.user.id, content='test', url='/test')
        self.notification.insert()

        # generate token
        # push an application context as generate_token function needs it
        # ref: https://flask.palletsprojects.com/en/2.0.x/appcontext/#lifetime-of-the-context
        self.app.app_context().push()
        self.token = create_access_token(identity=self.user.id)

    def tearDown(self):
        """ Executes after each test """
        db.session.remove()
        db.drop_all()

    def test_422_upload(self):
        res = self.client().post('api/upload',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 data={'file': (BytesIO(b'IMAGE DATA'), 'file.jpg')})  # fake data
        json_data = res.get_json()
        self.assertEqual(res.status_code, 422)
        self.assertIsInstance(json_data.get('message'), str)

    def test_422_register(self):
        res = self.client().post('/api/register',
                                 json={
                                     'first_name': 'ahmed',
                                     'last_name': 'hamed',
                                     'email': 'test@test.com',
                                     'username': self.user.username,  # username already exists
                                     'password': '12345678'
                                 })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 422)
        self.assertIsInstance(json_data.get('message'), str)

    def test_register(self):
        res = self.client().post('/api/register',
                                 json={
                                     'first_name': 'ahmed',
                                     'last_name': 'hamed',
                                     'email': 'test@test.com',
                                     'username': 'test',
                                     'password': '12345678'
                                 })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('token'), str)

    def test_patch_profile(self):
        res = self.client().patch('/api/profile',
                                  headers={
                                      'Authorization': 'Bearer %s' % self.token},
                                  json={'job': 'test'})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('job'), 'test')

    def test_422_login(self):
        res = self.client().post('/api/login',
                                 json={
                                     'username': 'ahmedhrayyan',
                                     'password': 'top_secret'
                                 })
        self.assertEqual(res.status_code, 422)

    def test_login(self):
        res = self.client().post('/api/login',
                                 json={
                                     'username': 'ahmedhrayyan',
                                     'password': 'secret'
                                 })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('token'), str)

    def test_401_get_profile(self):
        res = self.client().get('/api/profile')
        self.assertEqual(res.status_code, 401)

    def test_get_profile(self):
        res = self.client().get('/api/profile',
                                headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('username'), self.user.username)

    def test_get_notifications(self):
        res = self.client().get('/api/notifications',
                                headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(json_data.get('unread_count'), 0)

    def test_get_questions(self):
        res = self.client().get('/api/questions')
        self.assertEqual(res.status_code, 200)

    def test_404_show_question(self):
        res = self.client().get('/api/questions/232482')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_show_question(self):
        res = self.client().get('/api/questions/%i' % self.question.id)
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(self.question.id, json_data['data'].get('id'))

    def test_get_question_answers(self):
        res = self.client().get('/api/questions/%i/answers' % self.question.id)
        self.assertEqual(res.status_code, 200)

    def test_400_post_question(self):
        res = self.client().post('/api/questions',
                                 headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertIsInstance(json_data.get('message'), str)

    def test_post_question(self):
        content = 'Is this great or what'
        res = self.client().post('/api/questions',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'user_id': self.user.id, 'content': content})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(content, json_data['data'].get('content'))

    def test_patch_question(self):
        res = self.client().patch('/api/questions/%i' % self.question.id,
                                  headers={
                                      'Authorization': 'Bearer %s' % self.token},
                                  json={'accepted_answer': self.answer.id})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(self.answer.id, json_data['data'].get('accepted_answer'))

    def test_400_vote_question(self):
        res = self.client().post('/api/questions/%i/vote' % self.question.id,
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'vote': 5})
        self.assertEqual(res.status_code, 400)

    def test_vote_question(self):
        res = self.client().post('/api/questions/%i/vote' % self.question.id,
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'vote': 1})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('viewer_vote'), True)

    def test_unvote_question(self):
        res = self.client().post('/api/questions/%i/vote' % self.question.id,
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'vote': 0})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('viewer_vote'), None)

    def test_404_delete_question(self):
        res = self.client().delete('/api/questions/10000',
                                   headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_delete_question(self):
        res = self.client().delete('/api/questions/%i' % self.question.id,
                                   headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.question.id, json_data.get('deleted_id'))

    def test_404_show_answer(self):
        res = self.client().get('/api/answers/10420')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_show_answer(self):
        res = self.client().get('/api/answers/%i' % self.answer.id)
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(self.answer.id, json_data['data'].get('id'))

    def test_400_post_answer(self):
        res = self.client().post('/api/answers',
                                 headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertIsInstance(json_data.get('message'), str)

    def test_post_answer(self):
        content = 'answer'
        res = self.client().post('/api/answers',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'user_id': self.user.id,
                                       'question_id': self.question.id,
                                       'content': content})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertIn(content, json_data['data'].get('content'))

    def test_patch_answer(self):
        content = 'new answer'
        res = self.client().patch('/api/answers/%i' % self.answer.id,
                                  headers={
                                      'Authorization': 'Bearer %s' % self.token},
                                  json={'content': content})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertIn(content, json_data['data'].get('content'))

    def test_400_vote_answer(self):
        res = self.client().post('/api/answers/%i/vote' % self.answer.id,
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'vote': 5})
        self.assertEqual(res.status_code, 400)

    def test_vote_answer(self):
        res = self.client().post('/api/answers/%i/vote' % self.answer.id,
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'vote': 1})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('viewer_vote'), True)

    def test_unvote_answer(self):
        res = self.client().post('/api/answers/%i/vote' % self.answer.id,
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'vote': 0})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('viewer_vote'), None)

    def test_404_delete_answer(self):
        res = self.client().delete('/api/answers/10000',
                                   headers={'Authorization': 'Bearer %s' % self.token}, )
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_delete_answer(self):
        res = self.client().delete('/api/answers/%i' % self.answer.id,
                                   headers={'Authorization': 'Bearer %s' % self.token})
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.answer.id, json_data.get('deleted_id'))

    def test_404_set_notification_read(self):
        res = self.client().post('/api/notifications/10000/set-read',
                                 headers={'Authorization': 'Bearer %s' % self.token}, )
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_200_set_notification_read(self):
        res = self.client().post('/api/notifications/%i/set-read' % self.notification.id,
                                 headers={'Authorization': 'Bearer %s' % self.token}, )
        self.assertEqual(res.status_code, 200)

    def test_404_show_user(self):
        res = self.client().get('/api/users/x')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_show_user(self):
        res = self.client().get('/api/users/%s' % self.user.username)
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json_data.get('data'), dict)
        self.assertEqual(json_data['data'].get('username'), self.user.username)

    def test_404_get_user_questions(self):
        res = self.client().get('/api/users/x/questions')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(json_data.get('message'), str)

    def test_get_user_questions(self):
        res = self.client().get('/api/users/%s/questions' % self.user.username)
        self.assertEqual(res.status_code, 200)

    def test_report_question(self):
        res = self.client().post('/api/report/question',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'question_id': self.question.id})
        self.assertEqual(res.status_code, 200)

    def test_report_answer(self):
        res = self.client().post('/api/report/answer',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token},
                                 json={'answer_id': self.answer.id})
        self.assertEqual(res.status_code, 200)
