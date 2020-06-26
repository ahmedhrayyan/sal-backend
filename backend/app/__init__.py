from flask import Flask, jsonify, request, abort, _request_ctx_stack
from flask_cors import CORS, cross_origin
from backend.database import setup_db, Answer, Question
from backend.auth import (init_auth0, Auth0Error, AuthError,
                  requires_auth, requires_permission)


def get_paginated_items(req, items, items_per_page=20):
    page = req.args.get('page', 1, int)
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    # include next_path in paginated items
    if len(items) - page * items_per_page > 0:
        next_path = request.path + f'?page={page+1}'
    else:
        next_path = None
    return [items[start_index:end_index], next_path]


def get_formated_questions(questions):
    formated_questions = []
    for question in questions:
        formated = question.format()
        formated_questions.append(formated)
    return formated_questions


def create_app(test_env=False):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,
        static_folder='../../frontend/build',
        static_url_path='/')
    if test_env is False:
        # load config file if it exists
        app.config.from_pyfile('config.py', silent=True)
        setup_db(app)
        auth0 = init_auth0()

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route('/api/search', methods=['POST'])
    def search():
        data = request.get_json() or []
        if 'search' not in data:
            abort(400, 'search expected in request body')
        search_term = '%' + data['search'] + '%'
        all_questions = Question.query.filter(
            Question.content.ilike(search_term)
        ).order_by(Question.created_at.desc()).all()
        questions, next_path = get_paginated_items(request, all_questions)
        formated_questions = get_formated_questions(questions)
        if len(questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': formated_questions,
            'no_of_questions': len(all_questions),
            'next_path': next_path,
            'search_term': data['search']
        })

    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.order_by(
            Question.created_at.desc()).all()
        questions, next_path = get_paginated_items(request, all_questions)
        formated_questions = get_formated_questions(questions)
        if len(questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': formated_questions,
            'no_of_questions': len(all_questions),
            'next_path': next_path

        })

    @app.route('/api/questions/<question_id>', methods=['GET'])
    def get_question(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(404)
        return jsonify({
            'success': True,
            'question': question.format()
        })

    @app.route('/api/questions/<question_id>', methods=['PATCH'])
    @requires_auth
    def select_best_answer(question_id):
        data = request.get_json() or []
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
        question.best_answer = answer_id
        try:
            question.update()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'patched': question.format()
        })

    @app.route('/api/questions', methods=['POST'])
    @requires_auth
    def post_question():
        data = request.get_json() or []
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

    @app.route('/api/questions/<question_id>', methods=['DELETE'])
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

    @app.route('/api/questions/<question_id>/answers', methods=['GET'])
    def get_answers(question_id):
        question = Question.query.get(question_id)
        if question == None:
            abort(404)
        all_answers = question.answers
        answers, next_path = get_paginated_items(request, all_answers)
        if len(answers) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'answers': [answer.format() for answer in answers],
            'no_of_answers': len(all_answers),
            'next_path': next_path
        })

    @app.route('/api/answers/<answer_id>', methods=['GET'])
    def get_answer(answer_id):
        answer = Answer.query.get(answer_id)
        if answer == None:
            abort(404)
        return jsonify({
            'success': True,
            'answer': answer.format()
        })

    @app.route('/api/questions/<question_id>/answers', methods=['POST'])
    @requires_auth
    def post_answer(question_id):
        data = request.get_json() or []
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

    @app.route('/api/answers/<answer_id>', methods=['DELETE'])
    @requires_auth
    def delete_answer(answer_id):
        answer = Answer.query.get(answer_id)
        if answer == None:
            abort(404)
        if _request_ctx_stack.top.current_user['sub'] != answer.user_id:
            if not requires_permission('delete:answers'):
                raise AuthError('You don\'t have '
                                'the authority to delete other users answers', 403)

        question = Question.query.get(answer.question_id)
        try:
            answer.delete()
            # unset question best_answer if it was the deleted answer
            if question.best_answer == answer.id:
                question.best_answer = None
                question.update()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'del_id': int(answer_id),
            'question_id': question.id # the answer question id
        })

    # get users public data
    @app.route('/api/users/<user_id>')
    def get_public_user(user_id):
        # response is a dict object
        public_fields = ['user_id', 'name', 'picture', 'user_metadata']
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
        # Invalid called to an api
        if request.path.startswith('/api') or request.method != 'GET':
            return jsonify({
                'success': False,
                'message': error.description,
                'error': 404
            }), 404

        # otherwise, Make react router handle 404
        return app.send_static_file('index.html')


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

    @app.errorhandler(Auth0Error)
    def handle_auth_error(error):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': error.status_code
        }), error.status_code

    @app.errorhandler(500)
    def handle_auth_error(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'error': 500
        }), 500

    return app
