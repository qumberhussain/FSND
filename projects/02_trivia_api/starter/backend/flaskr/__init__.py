import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the
  sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @DONE:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def categories():
        categories = Category.query.all()
        cattype = []
        for category in categories:
            cattype.append({"category": category.type, "id": category.id})
        return jsonify({
            "success": True,
            "categories": cattype
        })

    '''
  @DONE:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the
  screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection)
        })

    '''
  @DONE: Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the
  question will be removed.
  This removal will persist in the database and when you refresh
  the page.
  '''
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True
            })

        except:
            abort(422)

    '''
  @DONE:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        form = request.get_json()
        question = form.get('question', None)
        answer = form.get('answer', None)
        difficulty = form.get('difficulty', None)
        category = form.get('category', None)

        if not question:
            abort(422)

        try:
            question = Question(question=question, answer=answer,
                                difficulty=difficulty, category=category)
            question.insert()

            return jsonify({
                'success': True
            })
        except:
            abort(422)
    '''
  @DONE:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/search', methods=['POST'])
    def search():
        form = request.get_json()
        searchTerm = form.get('searchTerm', None)
        query = Question.query.filter(
            Question.question.ilike('%' + searchTerm + '%')).all()
        if query is None:
            return
        return jsonify({
            "success": True,
            "questions": [question.format() for question in query],
            "total_questions": len(query)
        })

    '''
  @DONE:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
        valid_categories = Question.query.filter(
            Question.category == category_id).all()
        print(valid_categories)
        if not valid_categories:
            abort(404)
            return jsonify({
                'success': False,
            })
        else:
            try:
                selectionQ = Question.query.filter(
                    Question.category == category_id).all()
                selectionC = Category.query.filter(
                    Category.id == category_id).all()
                questions = [question.format() for question in selectionQ]
                cat = [category.format() for category in selectionC]
                print(cat)
                return jsonify({
                    'success': True,
                    'questions': questions,
                    'total_questions': len(questions),
                    'current_category': cat
                })
            except:
                abort(422)

    '''
  @DONE:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def play():
        data = request.get_json()
        category = data.get('quiz_category')
        previousQuestions = data.get('previous_questions')
        if category['id'] == 0:
            question = Question.query.filter(
                Question.id.notin_(previousQuestions)).limit(1).first()
        else:
            question = Question.query.filter_by(
                category=category['id']).filter(
                Question.id.notin_(previousQuestions)).order_by(func.random())\
                .limit(1).first()
        if question is not None:
            question = question.format()
        return jsonify({
            'success': True,
            'question': question
        })

    '''
  @DONE:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "action unprocessable"
        }), 404

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 404

    return app
