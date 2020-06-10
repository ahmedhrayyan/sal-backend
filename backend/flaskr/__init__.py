from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
from database import setup_db, Answer, Question

def get_paginated_items(req, items, items_per_page=10):
    page = req.args.get('page', 1, int)
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    return items[start_index:end_index]

def get_formated_quetsions(questions):
    formated_questions = []
    for question in questions:
        formated = question.format()
        best_answer = None
        if (question.best_answer_id != None):
            best_answer = Answer.query.get(best_answer).format()
        else:
            # this could be None (no answers)
            best_answer = Answer.query.order_by(Answer.created_at).first()

        formated.update({
            'no_of_answers': len(question.answers),
            'best_answer': best_answer.format() if best_answer else None
        })

        formated_questions.append(formated)

    return formated_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load config file if it exists
        app.config.from_pyfile('config.py', silent=True)
    setup_db(app)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.order_by(Question.created_at).all()
        questions = get_paginated_items(request, all_questions)
        formated_questions = get_formated_quetsions(questions)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'no_of_questions': len(all_questions)
        })

    @app.route('/questions/<question_id>', methods=['GET'])
    def get_question(question_id):
        question = Question.query.get(question_id)

        if question == None:
            abort(404)

        return jsonify({
            'success': True,
            'question': question.format()
        })


    # handling errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'not found',
            'error': 404
        }), 404

    return app
