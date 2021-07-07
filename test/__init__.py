from auth import gen_token
from os import remove
import unittest
from app import create_app
from db import db
from db.models import Question, Answer, User, Role
from config import TestingConfig


class SalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client
        # seed data
        self.role = Role('general')
        self.role.insert()
        self.user = User('Ahmed', 'Hamed', 'ahmedhrayyan@outlook.com',
                         'ahmedhrayyan', 'secret', self.role.id)
        self.user.insert()
        self.question = Question(self.user.id, 'Is sal the best QA engine')
        self.question.insert()
        self.answer = Answer(self.user.id, self.question.id, 'Yes it is')
        self.answer.insert()
        self.token = gen_token(self.app.config['SECRET_KEY'], self.user)

    def tearDown(self):
        # remove genrated test db
        try:
            remove('test.db')
        except OSError:
            pass

    def test_get_questions(self):
        res = self.client().get('/api/questions')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])

    def test_404_get_question(self):
        res = self.client().get('/api/questions/232482')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json_data['success'])
        self.assertTrue(json_data['message'])

    def test_get_question(self):
        res = self.client().get('/api/questions/%i' % self.question.id)
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertEqual(self.question.id, json_data['data']['id'])

    def test_400_post_question(self):
        res = self.client().post('/api/questions',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token
                                 })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(json_data['success'])
        self.assertTrue(json_data['message'])

    def test_post_question(self):
        content = 'Is this great or what'
        res = self.client().post('/api/questions',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token
                                 },
                                 json={
                                     'user_id': self.user.id,
                                     'content': content
                                 })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertIn(content, json_data['data']['content'])

    def test_patch_question(self):
        res = self.client().patch('/api/questions/%i' % self.question.id,
                                  headers={
                                      'Authorization': 'Bearer %s' % self.token
                                  },
                                  json={
                                      'accepted_answer': self.answer.id
                                  })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertEqual(self.answer.id, json_data['data']['accepted_answer'])

    def test_404_delete_question(self):
        res = self.client().delete('/api/questions/10000',
                                   headers={
                                       'Authorization': 'Bearer %s' % self.token
                                   },
                                   )
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json_data['success'])
        self.assertTrue(json_data['message'])

    def test_delete_question(self):
        res = self.client().delete('/api/questions/%i' % self.question.id,
                                   headers={
                                       'Authorization': 'Bearer %s' % self.token
                                   },
                                   )
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertEqual(self.question.id, json_data['deleted_id'])

    def test_404_get_answer(self):
        res = self.client().get('/api/answers/10420')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json_data['success'])
        self.assertTrue(json_data['message'])

    def test_get_answer(self):
        res = self.client().get('/api/answers/%i' % self.answer.id)
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertEqual(self.answer.id, json_data['data']['id'])

    def test_400_post_answer(self):
        res = self.client().post('/api/answers',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token
                                 },
                                 content_type='application/json')
        json_data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(json_data['success'])
        self.assertTrue(json_data['message'])

    def test_post_answer(self):
        content = 'answer'
        res = self.client().post('/api/answers',
                                 headers={
                                     'Authorization': 'Bearer %s' % self.token
                                 },
                                 json={
                                     'user_id': self.user.id,
                                     'question_id': self.question.id,
                                     'content': content
                                 })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertIn(content, json_data['data']['content'])

    def test_patch_answer(self):
        content = 'new answer'
        res = self.client().patch('/api/answers/%i' % self.answer.id,
                                  headers={
                                      'Authorization': 'Bearer %s' % self.token
                                  },
                                  json={
                                      'content': content
                                  })
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertIn(content, json_data['data']['content'])

    def test_404_delete_answer(self):
        res = self.client().delete('/api/answers/10000',
                                   headers={
                                       'Authorization': 'Bearer %s' % self.token
                                   },
                                   )
        json_data = res.get_json()
        self.assertEqual(res.status_code, 404)
        self.assertFalse(json_data['success'])
        self.assertTrue(json_data['message'])

    def test_delete_answer(self):
        res = self.client().delete('/api/answers/%i' % self.answer.id,
                                   headers={
                                       'Authorization': 'Bearer %s' % self.token
                                   },
                                   )
        json_data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertEqual(self.answer.id, json_data['deleted_id'])
