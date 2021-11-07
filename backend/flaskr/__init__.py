import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from sqlalchemy.dialects import postgresql

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
  
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    response.headers.add(
        "Access-Control-Allow-Origin", "*"
    )
    return response

  def getCategories():
    selection = Category.query.all()
    cats = {}
    for cat in selection:
        cats[cat.id] = cat.type 
    return cats 
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def categories():
    cats = getCategories()
    return jsonify({
        'categories':cats
        })
        

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def questions():
    selection = Question.query.all()
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    if( start > len(selection)+1):
        abort(404)

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    
    cats = getCategories()
    return jsonify({
        'questions':current_questions,
        'totalQuestions': len(selection),
        'categories': cats,
        'current_category': 'History'
        })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def deleteQuestion(id):
    question = Question.query.get(id)
    if question == None:
        abort(404)
    question.delete()
    return jsonify({
            'success': True,
            'id': id
            })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def postQuestion():
    if not request.json:
        abort(400)
    body = request.json
    if ('question' not in body) or ('answer' not in body) or ('category' not in body) or ('difficulty' not in body):
        abort(422)
    question = Question(
        question = body['question'],
        answer = body['answer'],
        category = body['category'],
        difficulty = body['difficulty']
        )
    question.insert()
    
    return jsonify({
            'success': True,
            'id': question.id
            })
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def queryQuestions():
    if not request.json:
        abort(400)
    body = request.json
    if 'searchTerm' in body:
        searchTerm = body['searchTerm']
        selections = Question.query.filter(Question.question.contains(searchTerm)).all()
        questions = [question.format() for question in selections]
        return jsonify({
            'questions': questions,
            'totalQuestions': len(questions),
            'currentCategory': None
            })
    else:
        abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cid>/questions', methods=['GET'])
  def getQuestionsByCategory(cid):

    category = Category.query.get(cid)
    if category == None:
        abort(404)
    selection = Question.query.filter(Question.category == cid).all()
    questions = [q.format() for q in selection]
    return jsonify({
          'questions': questions,
          'totalQuestions': len(questions),
          'currentCategory': category.type

          })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def nextQuiz():
    if not request.json:
        abort(400)
    req = request.json
    if ('quiz_category' not in req)  or ('previous_questions' not in req):
        abort(422)
    cid = req['quiz_category']['id']
    olds= req['previous_questions']
    query = Question.query
    if (cid == 0):
        selection = query.filter(~Question.id.in_(olds)).order_by(func.random()).first()
    else : 
        selection = query.filter(Question.category == cid).filter(~Question.id.in_(olds)).order_by(func.random()).first()

    if selection != None:
        return jsonify({
            'question': selection.format()
            })
    else:
        return jsonify({
            'question': {}
            })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "Cannot process the request. Check Value of each field"}),
            422,
    )

  @app.errorhandler(404)
  def badsyntax(error):
    return (
        jsonify({"success": False, "error": 404, "message": "Can not find resource."}),
            404,
    )

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request: expecting json body"}), 400

  
  return app

    