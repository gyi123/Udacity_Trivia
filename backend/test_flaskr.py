import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://postgres:password@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.new_question = {"question": "What is 3 + 5?", "answer": "5", "difficulty": 1, "category": 1}
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def testQuestions(self):
        resp = self.client().get('/questions?page=1')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        
        self.assertTrue(data['current_category'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data['categories']))
        
    def test_404_sent_requesting_beyond_valid_page(self):
        resp = self.client().get('/questions?page=100')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 404)  
              
    def testCategories(self):
        resp = self.client().get('/categories')
        data = json.loads(resp.data)
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(data['categories']))
        
    def testPostAndDeleteQuestion(self):
        resp = self.client().post('/questions', json=self.new_question)
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        resp = self.client().delete('/questions/'+str(data['id']))
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_400_PostQuestion(self):
        resp = self.client().post('/questions')
        self.assertEqual(resp.status_code, 400)
        
    def test_422_PostQuestion(self):
        resp = self.client().post('/questions', json={'question': 'test'})
        self.assertEqual(resp.status_code, 422)
        
    def test_404_DeleteQuestion(self):
        resp = self.client().delete('/questions/-1')
        self.assertEqual(resp.status_code, 404)
        
    def test_400_SearchQuestions(self):
        resp = self.client().post('/questions/search')
        self.assertEqual(resp.status_code, 400)
        
    def test_422_SearchQuestions(self):
        resp = self.client().post('/questions/search', json={'no_searchTerm': 'test'})
        self.assertEqual(resp.status_code, 422)
        
    def testSearchQuestions(self):
        resp = self.client().post('/questions/search', json={'searchTerm': 'Hanks'})
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(data['questions']))
        
    def test_404_GetQuestionsByCategory(self):
        resp = self.client().get('/categories/-1/questions')
        self.assertEqual(resp.status_code, 404)
 
    def testGetQuestionsByCategory(self):
        resp = self.client().get('/categories/1/questions')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(data['questions']))
        
    def test_400_quizzes(self):
        resp = self.client().post('/quizzes')
        self.assertEqual(resp.status_code, 400)

    def test_422_missing_Category_quizzes(self):
        resp = self.client().post('/quizzes', json={'previous_questions':[1]})
        self.assertEqual(resp.status_code, 422)
        
    def test_422_missing_previousQuestions_quizzes(self):
        resp = self.client().post('/quizzes', json={'quiz_category': 1})
        self.assertEqual(resp.status_code, 422)
        
    def test_Qizzes_In_All(self):
        resp = self.client().post('/quizzes', json={'quiz_category': {
                                                        'type': 'click',
                                                        'id': 0},
                                                    'previous_questions':[]
                                                    })
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(data['question']))
        
    def test_Qizzes_In_One(self):
        resp = self.client().post('/quizzes', json={'quiz_category': {
                                                        'type': 'click',
                                                        'id': 2},
                                                    'previous_questions':[]
                                                    })
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(data['question']))
        
    def test_Next_Qizzes(self):
        jsonReq = {'quiz_category': {
                        'type': 'click',
                        'id': 2},
                    'previous_questions':[]
                   }
        resp = self.client().post('/quizzes', json=jsonReq)
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(data['question']))
        prevQuestionId = data['question']['id']
        jsonReq['previous_questions'].append(prevQuestionId)
        resp = self.client().post('/quizzes', json=jsonReq)
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        newQuestionId = data['question']['id']
        self.assertNotEqual(prevQuestionId, newQuestionId, "New Question Id is the same as old")
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()