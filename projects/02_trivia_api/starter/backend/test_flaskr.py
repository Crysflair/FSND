import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        # FIXME: WHat does that mean?
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_question_list(self):
        """Test successful calls for question list"""
        # all
        res = self.client().get('/questions?page=1&current_category=null&search_term=')
        self.assertEqual(res.status_code, 200)

        # search (exist)
        res = self.client().get('/questions?page=1&current_category=null&search_term=a')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.get_json()["total_questions"],0)
        for q in res.get_json()["questions"]:
            self.assertIn("a", q['question'])

        # search (not exist)
        res = self.client().get('/questions?page=1&current_category=null&search_term=totasakilametzu')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["total_questions"], 0)

        # category
        res = self.client().get('/questions?page=1&current_category=4&search_term=')
        self.assertEqual(res.status_code, 200)
        for q in res.get_json()["questions"]:
            self.assertEqual(4, q['category'])

    def test_question_list_error(self):
        """Test unsuccessful calls for question list"""
        # wrong url
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 422)
        # wrong parameter
        res = self.client().get('/questions?page=1&current_category=best&search_term=')
        self.assertEqual(res.status_code, 422)

    def test_category_list(self):
        """Test successful calls for category list"""
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_category_list_error(self):
        """Test successful calls for category list"""
        # wrong method
        res = self.client().post('/categories', data={"some":"thing"})
        self.assertEqual(res.status_code, 404)
        # wrong url
        res = self.client().get('/categories/')
        self.assertEqual(res.status_code, 404)

    def test_question_delete(self):
        res = self.client().get('/questions?page=1&current_category=null&search_term=')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.get_json()["total_questions"], 0)
        idx = res.get_json()["questions"][0]['id']
        # delete successfully
        res = self.client().delete('/questions/{}'.format(idx))
        self.assertEqual(res.status_code, 200)
        # already deleted. cannot find that question
        res = self.client().delete('/questions/{}'.format(idx))
        self.assertEqual(res.status_code, 404)

    def test_question_create(self):
        res = self.client().post(
            '/questions', json={
                "question": "test question",
                "answer": "test answer",
                "difficulty": 3,
                "category": 1
            }
        )
        self.assertEqual(res.status_code, 201)

    def test_question_create_error(self):
        # if params are wrong
        res = self.client().post(
            '/questions', json={
                "q": "test question",
                "difficulty": 3,
                "category": 1
            }
        )
        self.assertEqual(res.status_code, 422)
        # if values are of wrong types.
        res = self.client().post(
            '/questions', json={
                "question": "test question",
                "answer": "test answer",
                "difficulty": "3",
                "category": "science"
            }
        )
        self.assertEqual(res.status_code, 422)

    def test_quiz_get_next(self):
        previous_questions = []
        for _ in range(100):
            res = self.client().post(
                '/quizzes', json={
                    'previous_questions': previous_questions,
                    "category": 1
                }
            )
            self.assertEqual(res.status_code, 200)
            if res.get_json()["question"] is None:
                break
            res_id = res.get_json()["question"]["id"]
            self.assertNotIn(res_id, previous_questions)
            previous_questions.append(res_id)




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()