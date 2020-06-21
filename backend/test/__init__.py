import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from database import setup_db, Answer, Question, db
from instance.config import SQLALCHEMY_DATABASE_URI


class SalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_uri = 'postgresql://admin:secret@localhost:5432/sal_test'
        setup_db(self.app, self.database_uri, True)
        # dummy data
        self.question = Question('test', 'Is sal the best QA engine')
        self.question.insert()
        self.answer = Answer('test', 'Yes it is', self.question.id)
        self.answer.insert()

    def tearDown(self):
        # clean up the database after each test
        db.session.query(Answer).delete()
        db.session.query(Question).delete()
        db.session.commit()

    def test_404_get_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_get_questions(self):
        no_of_questions = len(Question.query.all())
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['no_of_questions'], no_of_questions)

    def test_404_get_question(self):
        res = self.client().get('/questions/232482')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_get_question(self):
        question_id = self.question.id
        res = self.client().get('/questions/' + str(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['id'], question_id)

    def test_400_post_question(self):
        res = self.client().post('/questions',
                                 data={},
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_post_question(self):
        res = self.client().post('/questions',
                                 data=json.dumps({
                                     'user_id': 'test',
                                     'content': 'Is this great or what'
                                 }),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created']['content'], 'Is this great or what')

    def test_400_patch_question(self):
        question_id = self.question.id
        res = self.client().patch('/questions/' + str(question_id),
                                  content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_patch_question(self):
        question_id = self.question.id
        answer_id = self.answer.id
        res = self.client().patch('/questions/' + str(question_id),
                                  data=json.dumps({
                                      'answer': answer_id
                                  }),
                                  content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['best_answer_id'], answer_id)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_delete_question(self):
        question_id = self.question.id
        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['del_id'], question_id)

    def test_404_get_answers(self):
        question_id = self.question.id
        res = self.client().get('/questions/'+str(question_id)+'/answers?page=100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_get_answers(self):
        question_id = self.question.id
        no_of_answers = len(self.question.answers)
        res = self.client().get('/questions/'+str(question_id)+'/answers')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['no_of_answers'], no_of_answers)

    def test_get_latest_answer(self):
        question_id = self.question.id
        res = self.client().get('/questions/'+str(question_id)+'/answers/latest')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['answer'])

    def test_404_get_answer(self):
        res = self.client().get('/answers/10420')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_get_answer(self):
        answer_id = self.answer.id
        res = self.client().get('/answers/'+str(answer_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['answer']['content'], self.answer.content)

    def test_400_post_answer(self):
        question_id = self.question.id
        res = self.client().post('/questions/' + str(question_id) + '/answers',
                                 data=json.dumps({
                                     'user_id': 'test'
                                 }),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_post_answer(self):
        question_id = self.question.id
        res = self.client().post('/questions/'+str(question_id)+'/answers',
                                 data=json.dumps({
                                     'user_id': 'test',
                                     'content': 'It\'s Awesome'
                                 }),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created']['question_id'], question_id)

    def test_404_delete_answer(self):
        res = self.client().delete('/answers/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_delete_answer(self):
        answer_id = self.answer.id
        res = self.client().delete('/answers/'+str(answer_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['del_id'], answer_id)
