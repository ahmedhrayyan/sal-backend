from flask import Flask, jsonify, request, abort, _request_ctx_stack
from flask_cors import CORS, cross_origin
from database import setup_db, Answer, Question
from auth import init_auth0, AuthError, requires_auth, requires_permission

def get_paginated_items(req, items, items_per_page=10):
    page = req.args.get('page', 1, int)
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    return items[start_index:end_index]

def get_formated_questions(questions):
    formated_questions = []
    for question in questions:
        formated = question.format()
        formated.update({
            'no_of_answers': len(question.answers),
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
    auth0 = init_auth0()

    @app.route('/questions', methods=['GET'])
    @requires_auth
    def get_questions():
        all_questions = Question.query.order_by(Question.created_at).all()
        questions = get_paginated_items(request, all_questions)
        formated_questions = get_formated_questions(questions)
        if len(questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': formated_questions,
            'no_of_questions': len(all_questions)
        })

    @app.route('/questions/<question_id>', methods=['GET'])
    @requires_auth
    def get_question(question_id):
        question = Question.query.get(question_id)
        formated_question = question.format()
        formated_question.update({
            'no_of_answers': len(question.answers)
        })
        if question == None:
            abort(404)
        return jsonify({
            'success': True,
            'question': formated_question
        })

    @app.route('/questions/<question_id>', methods=['PATCH'])
    @requires_auth
    def select_best_answer(question_id):
        data = request.get_json()
        if 'answer' not in data:
            abort(400, 'answer expected in request body')
        answer_id = data.get('answer')
        question = Question.query.get(question_id)
        if question == None:
            abort(404, 'question not found')
        if _request_ctx_stack.top.current_user['sub'] != question.user_id:
            if requires_permission('update:questions'):
                raise AuthError('You don\'t have '
                'the authority to delete other users answers', 403)
            answer = Answer.query.get(answer_id)
        if answer not in question.answers:
            abort(400, 'the provided answer is not valid')
        question.best_answer_id = answer_id
        try:
            question.update()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'best_answer_id': int(answer_id)
        })

    @app.route('/questions', methods=['POST'])
    @requires_auth
    def post_question():
        data = request.get_json()
        if 'content' not in data:
            abort(400, 'content expected in request body')
        user_id = _request_ctx_stack.top.current_user['sub']
        new_question = Question(user_id, data['content'])
        try:
            new_question.insert()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'created': new_question.format()
        })

    @app.route('/questions/<question_id>', methods=['DELETE'])
    @requires_auth
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(404)
        if _request_ctx_stack.top.current_user['sub'] != question.user_id:
            if not requires_permission('delete:questions'):
                raise AuthError('You don\'t have '
                'the authority to delete other users questions', 403)
        try:
            question.delete()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'del_id': int(question_id)
        })

    @app.route('/questions/<question_id>/answers', methods=['GET'])
    @requires_auth
    def get_answers(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(404)
        all_answers = question.answers
        answers = get_paginated_items(request, all_answers)
        if len(answers) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'answers': [answer.format() for answer in answers],
            'no_of_answers': len(all_answers)
        })

    @app.route('/questions/<question_id>/answers/latest', methods=['GET'])
    @requires_auth
    def get_latest_answer(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(404)
        answers = question.answers
        if len(answers) == 0:
            abort(404, 'no answers for this question')
        return jsonify({
            'success': True,
            'answer': answers[0].format()
        })

    @app.route('/answers/<answer_id>', methods=['GET'])
    @requires_auth
    def get_answer(answer_id):
        answer = Answer.query.get(answer_id)
        if answer == None:
            abort(404)
        return jsonify({
            'success': True,
            'answer': answer.format()
        })

    @app.route('/questions/<question_id>/answers', methods=['POST'])
    @requires_auth
    def post_answer(question_id):
        data = request.get_json()
        if 'content' not in data:
            abort(400, 'content expected in request body')
        question = Question.query.get(question_id)
        if question == None:
            abort(404, 'question not found')
        user_id = _request_ctx_stack.top.current_user['sub']
        new_answer = Answer(user_id, data['content'], question_id)
        try:
            new_answer.insert()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'created': new_answer.format()
        })

    @app.route('/answers/<answer_id>', methods=['DELETE'])
    @requires_auth
    def delete_answer(answer_id):
        answer = Answer.query.get(answer_id)
        if answer == None:
            abort(404)
        if _request_ctx_stack.top.current_user['sub'] != answer.user_id:
            if not requires_permission('delete:answers'):
                raise AuthError('You don\'t have '
                'the authority to delete other users answers', 403)
        try:
            answer.delete()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'del_id': int(answer_id)
        })

    # get users public data
    @app.route('/users/<user_id>')
    @requires_auth
    def index(user_id):
        # response is a dict object
        public_fields = ['name', 'picture', 'user_metadata']
        response = auth0.get_user(user_id, public_fields)
        # check for errors
        if response.get('error') is not None:
            abort(response['statusCode'], response['message'])
        return jsonify({
            'success': True,
            'user': response
        })

    # handling errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'error': 404
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'error': 400
        }), 400

    @app.errorhandler(422)
    def un_processable(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'error': 422
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'error': 405
        }), 405

    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': error.status_code
        }), error.status_code

    return app
