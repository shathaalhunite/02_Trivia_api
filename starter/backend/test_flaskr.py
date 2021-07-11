import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from psycopg2.extensions import register_adapter, AsIs
from pydantic.networks import IPv4Address, IPv6Address
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path ="postgres://{}:{}@{}/{}".format('postgres','Shosho11','localhost:5432', self.database_name)
        self.new_question = {
            'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?',
            'answer': 'Tom Cruise',
            'difficulty': 4,
            'category': '5'
        }
        setup_db(self.app, self.database_path)
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_request_invalid_page(self):
        response = self.client().get('/questions?page=200')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
  

    def test_404_if_question_does_not_exist(self):
        response = self.client().delete('/question/1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Server Error')

    def test_delete_question(self):
        #Make sure add the question=1 
        response = self.client().delete('/question/10')
        data = json.loads(response.data)
        question = Question.query.filter(Question.id == 10).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # self.assertEqual(data['deleted'], 1)
        self.assertEqual(question, None)

    def test_create_new_question(self):
        questionsBefore = len(Question.query.all())
        response = self.client().post('/questions/add', json=self.new_question)
        data = json.loads(response.data)
        questionsAfter = len(Question.query.all())
        question = Question.query.filter_by(id=data['created']).all()
        self.assertIsNotNone(question)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(questionsAfter, questionsBefore + 1)

    def test_422_if_question_creation_fails(self):
        response = self.client().post('/questions/add', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_search_questions(self):
        response = self.client().post('/questions', json={'searchTerm': 'What is the largest lake in Africa?'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_if_search_questions_fails(self):
        response = self.client().post('/questions',json={'searchTerm': '123'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_404_if_questions_by_category_fails(self):
        response = self.client().get('/categories/25/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_play_quiz_game(self):
       quiz = {'previous_questions': [],'quiz_category': {'type': 'Geography', 'id': 3}}
       res = self.client().post('/quizzes', json=quiz)
       data = json.loads(res.data)
       self.assertEqual(res.status_code, 200)
       self.assertEqual(data['success'], True)

    def test_400_play_quiz_fails(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Server Error')


if __name__ == "__main__":
     unittest.main()