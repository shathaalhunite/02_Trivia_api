
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
from flask import Flask, jsonify,render_template
from models import setup_db, Question, Category
from flask_cors import CORS
from logging import DEBUG, Formatter, FileHandler
import logging

QUESTIONS_PER_PAGE = 10
Category_PER_PAGE = 10
def create_app(test_config=None):

  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)
  CORS(app, resources={'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return response

  @app.route('/questions')
  def getQuestions():
   page = request.args.get('page', 1, type=int)
   start =  (page - 1) * QUESTIONS_PER_PAGE
   end = start + QUESTIONS_PER_PAGE
   questions = Question.query.all()
   formatted_questions = [question.format() for question in questions]
   if (len(formatted_questions) == 0):
          abort(404)
   categories = Category.query.all()
   categories_dict = {}
   for category in categories:
       categories_dict[category.id] = category.type
   return jsonify({
    'success': True,
    'questions':formatted_questions[start:end],
    'total_questions':len(formatted_questions),
    'categories': categories_dict
           })

  @app.route('/categories')
  def getCategory():
    categories = Category.query.all()
    categorie = {}
    for category in categories:
        categorie[category.id] = category.type
    if (len(categorie) == 0):
            abort(404)
    return jsonify({
    'success': True,
    'categories':categorie
      })
   
  @app.route('/question/<int:id>', methods=['DELETE'])
  def deleteQuestion(id):
    question = Question.query.filter_by(id=id).one_or_none()
    if question is None:
        abort(500)
    question.delete()
    return jsonify({
    'success': True,
    'deleted': id
      })
   
  @app.route('/questions', methods=['POST'])
  def searchTerm_question():
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * Category_PER_PAGE
    end = start + Category_PER_PAGE
    body = request.get_json()
    search_term = body.get('searchTerm')
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    if (len(questions) == 0):
        abort(404)
    formatted_questions= [question.format() for question in questions]
    return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(Question.query.all())
            })
 
  @app.route('/questions/add', methods=['POST'])
  def add_question():
    body = request.get_json()
    questions=Question(
      question=body.get('question'),
      answer=body.get('answer'),
      difficulty=body.get('difficulty'),
      category=body.get('category'))
    if ((body.get('question') is None) or (body.get('answer') is None) or (body.get('difficulty') is None) or (body.get('category') is None)):
        abort(422)
    questions.insert()
    return jsonify({
                    'success': True,
                    'created': questions.id,
                    'total_questions': len(Question.query.all())
                })
 
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    category =Category.query.filter_by(id=category_id).one_or_none()
    if (category is None):
        abort(404)
    questions =Question.query.filter_by(category=category.id).all()
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * Category_PER_PAGE
    end = start + Category_PER_PAGE
    formatted_questions = [question.format() for question in questions]
    return jsonify({
    'success': True,
    'questions': formatted_questions[start:end],
    'total_questions': len(Question.query.all()),
    'current_category': category.type
       })
  @app.route('/quizzes', methods=['POST'])
  def quiz_question():
    
        body = request.get_json()
        previous = body.get('previous_questions')
        category = body.get('quiz_category')
        print(category)
        if (category['id'] == 0):
             questions = Question.query.all()
        else:
             questions = Question.query.filter_by(category=category['id']).all()  
            
        if ((category is None) or (previous is None)):
              abort(400)
        def used(question):
            used = False
            for q in previous:
                if (q == question.id):
                    used = True
            return used
        question = questions[random.randrange(0, len(questions), 1)]
        while (used(question)):
            question = questions[random.randrange(0, len(questions), 1)]
            total = len(questions)
            if (len(previous) == total):
                return jsonify({
                    'success': True
                })    
        return jsonify({
            'success': True,
            'question': question.format()
        })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found_error(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(500)
  def server_error(error):
   return jsonify({
        "success": False, 
        "error": 500,
        "message": "Server Error"
        }), 500

  @app.errorhandler(422)
  def Not_found(error):
   return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable Entity"
        }), 422


  if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
    Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

  return app

    