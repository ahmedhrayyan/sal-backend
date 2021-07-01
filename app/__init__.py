from os import path, mkdir
from uuid import uuid4
from flask import Flask, jsonify, request, abort, _request_ctx_stack, send_from_directory
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
from db import setup_db
from db.models import Answer, Notification, Question, User, Role
from jose import jwt
from auth import AuthError, gen_token, requires_auth, requires_permission
from sqlalchemy.exc import IntegrityError
import imghdr
import re
from markdown import markdown
import bleach
from config import ProductionConfig


def validate_image(stream):
    # check file format
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    # jpeg normally uses jpg file extension
    return format if format != "jpeg" else "jpg"


def paginate(query, page=1, page_size=20):
    offset = (page - 1) * page_size
    return query.limit(page_size).offset(offset)


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


def create_app(config=ProductionConfig):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    setup_db(app)
    SECRET_KEY = app.config['SECRET_KEY']

    @app.route("/")
    def index():
        return jsonify({
            "name": "Sal backend",
            "message": "Hello World!"
        })

    @app.route("/api/upload", methods=['POST'])
    @requires_auth(SECRET_KEY)
    def upload():
        if 'file' not in request.files:
            abort(400, "No file founded")
        file = request.files['file']
        if file.filename == '':
            abort(400, 'No selected file')
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in app.config['ALLOWED_EXTENSIONS'] or \
                file_ext != validate_image(file.stream):
            abort(422, 'You can only upload PNG and JPG file formats')

        # generate unique filename
        filename = uuid4().hex + "." + file_ext

        # Create upload folder if it doesnot exist
        if not path.isdir(app.config['UPLOAD_FOLDER']):
            mkdir(app.config['UPLOAD_FOLDER'])

        file.save(path.join(app.config['UPLOAD_FOLDER'], filename))

        return jsonify({
            'success': True,
            'path': filename
        })

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        # check if the file exists
        if not path.isfile(path.join(app.config['UPLOAD_FOLDER'], filename)):
            abort(404, "File not found!")

        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route("/api/register", methods=['POST'])
    def register():
        data = request.get_json() or {}
        required_fields = ['first_name', 'last_name',
                           'email', 'username', 'password']
        # abort if any required field doesnot exist in request body
        for field in required_fields:
            if field not in data:
                abort(422, '%s is required' % field)

        first_name = str(data['first_name']).lower().strip()
        last_name = str(data['last_name']).lower().strip()
        email = str(data['email']).lower().strip()
        username = str(data['username']).lower().strip()
        password = str(data['password']).lower()
        phone = data.get('phone', None)
        job = data.get('job', None)

        # validating data
        if re.match(app.config['EMAIL_PATTERN'], email) is None:
            abort(422, 'Email is not valid')
        if len(password) < 8:
            abort(422, 'Password have to be at least 8 characters in length')
        if phone and re.match(app.config['PHONE_PATTERN'], phone) is None:
            abort(422, 'Phone is not valid')
        if len(username) < 4:
            abort(422, 'Username have to be at least 4 characters in length')
        if job:
            str(job).lower().strip()

        default_role = Role.query.filter_by(name="general").one_or_none().id

        new_user = User(first_name, last_name, email,
                        username, password, default_role, job, phone)

        try:
            new_user.insert()
        except IntegrityError:
            # Integrity error means a unique value already exist in a different record
            if User.query.filter_by(email=data['email']).one_or_none():
                msg = 'Email is allready in use'
            elif User.query.filter_by(username=data['username']).one_or_none():
                msg = "Username is allready in use"
            else:
                msg = "Phone is allready in use"
            abort(422, msg)

        return jsonify({
            'success': True,
            'token': gen_token(SECRET_KEY, new_user),
        })

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        if 'username' not in data or 'password' not in data:
            abort(422, 'username and password expected in request body')

        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).one_or_none()
        if not user or not user.checkpw(str(password)):
            abort(422, 'username or password is not correct')

        return jsonify({
            'success': True,
            'token': gen_token(SECRET_KEY, user),
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

    @app.route('/api/questions/<question_id>/accepted_answer', methods=['PATCH'])
    @requires_auth(SECRET_KEY)
    def alter_accepted_answer(question_id):
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
        question.accepted_answer = answer_id

        try:
            question.update()
        except Exception:
            abort(422)

        return jsonify({
            'success': True,
            'patched': question.format()
        })

    @app.route('/api/questions', methods=['POST'])
    @requires_auth(SECRET_KEY)
    def post_question():
        data = request.get_json() or []
        if 'content' not in data:
            abort(400, 'content expected in request body')

        # sanitize input
        content = bleach.clean(data['content'])
        # supporting markdown
        content = markdown(content)
        user_id = _request_ctx_stack.top.current_user['sub']
        new_question = Question(user_id, content)
        try:
            new_question.insert()
        except Exception:
            abort(422)

        return jsonify({
            'success': True,
            'created': new_question.format()
        })

    @app.route('/api/questions/<question_id>', methods=['DELETE'])
    @requires_auth(SECRET_KEY)
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
    @requires_auth(SECRET_KEY)
    def post_answer(question_id):
        data = request.get_json() or []
        if 'content' not in data:
            abort(400, 'content expected in request body')
        question = Question.query.get(question_id)
        if question == None:
            abort(404, 'question not found')
        # sanitize input
        content = bleach.clean(data['content'])
        # supporting markdown
        content = markdown(content)
        user_id = _request_ctx_stack.top.current_user['sub']
        new_answer = Answer(user_id, content, question_id)
        try:
            new_answer.insert()
        except Exception:
            abort(422)
        return jsonify({
            'success': True,
            'created': new_answer.format()
        })

    @app.route('/api/answers/<answer_id>', methods=['DELETE'])
    @requires_auth(SECRET_KEY)
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
            'question_id': question.id  # the answer question id
        })

    @app.route('/api/load-own-data')
    @requires_auth(SECRET_KEY)
    def load_own_data():
        sub = _request_ctx_stack.top.curr_user['sub']
        user = User.query.filter_by(username=sub).one()
        unread_notifications = Notification.query.filter_by(
            user_id=user.id, read=False).count()

        return jsonify({
            'success': True,
            'data': user.format(),
            'unread_notifications': unread_notifications
        })

    @app.route('/api/users/<user_id>')
    def show_user(user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            abort(422, 'User id must be a number')

        user = User.query.get(user_id)
        if not user:
            abort(404, 'User not found')

        return jsonify({
            'success': True,
            'data': user.format()
        })

    @app.route('/api/users/<user_id>/notifications')
    def get_user_notifications(user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            abort(422, 'User id must be a number')

        user = User.query.get(user_id)
        if not user:
            abort(404, 'User not found')

        page = request.args.get('page', 1, int)
        query = Notification.query.filter_by(user_id=user_id)
        total = query.count()
        notifications = paginate(query, page).all()

        return jsonify({
            'success': True,
            'data': [notification.format() for notification in notifications],
            'page': page,
            'total': total
        })

    @app.route('/api/users/<user_id>/questions')
    def get_user_questions(user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            abort(422, 'User id must be a number')

        user = User.query.get(user_id)
        if not user:
            abort(404, 'User not found')

        page = request.args.get('page', 1, int)
        query = Question.query.filter_by(user_id=user_id)
        total = query.count()
        questions = paginate(query, page).all()

        return jsonify({
            'success': True,
            'data': [questions.format() for questions in questions],
            'page': page,
            'total': total
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
            'error': error.code
        }), error.code

    return app
