from os import path, mkdir
from typing import BinaryIO
from uuid import uuid4
from flask import Flask, jsonify, request, abort, send_from_directory, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
from marshmallow import ValidationError

from db import setup_db
from db.models import Answer, Notification, Permission, Question, User, Role
from db.schemas import notification_schema, answer_schema, AnswerSchema, question_schema, QuestionSchema, vote_schema
from auth import AuthError, generate_token, requires_auth, requires_permission, get_jwt_sub
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import imghdr
import re
import bleach
from config import ProductionConfig


def validate_image(stream: BinaryIO):
    ''' Return correct image extension '''
    # check file format
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    # jpeg normally uses jpg file extension
    return format if format != "jpeg" else "jpg"


def paginate(items: list, page: int = 1, per_page: int = 20):
    ''' Return a list of paginated items and a dict contains meta data '''
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    meta = {
        'total': len(items),
        'current_page': page,
        'per_page': per_page
    }
    return items[start_index:end_index], meta


def create_app(config=ProductionConfig):
    ''' create and configure the app '''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    CORS(app)
    mail = Mail(app)

    setup_db(app)

    ### ENDPOINTS ###

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.post("/api/upload")
    @requires_auth()
    def upload():
        if 'file' not in request.files:
            abort(400, "No file founded")
        file = request.files['file']
        if file.filename == '':
            abort(400, 'No selected file')
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            abort(422, 'You cannot upload %s files' % file_ext)
        if file_ext != validate_image(file.stream):
            abort(422, 'Fake data was uploaded')

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

    @app.get("/uploads/<filename>")
    def uploaded_file(filename):
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        except Exception:
            abort(404, "File not found")

    @app.post('/api/login')
    def login():
        data = request.get_json() or {}
        if 'username' not in data or 'password' not in data:
            abort(400, 'username and password expected in request body')

        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).one_or_none()
        if not user or not user.checkpw(str(password)):
            abort(422, 'username or password is not correct')

        role = Role.query.get(user.role_id)
        permissions = [permission.name for permission in role.permissions]

        return jsonify({
            'success': True,
            'token': generate_token(user.username, permissions),
        })

    @app.post("/api/register")
    def register():
        data = request.get_json() or {}
        required_fields = ['first_name', 'last_name',
                           'email', 'username', 'password']
        # abort if any required field doesnot exist in request body
        for field in required_fields:
            if field not in data:
                abort(400, '%s is required' % field)

        first_name = str(data['first_name']).lower().strip()
        last_name = str(data['last_name']).lower().strip()
        email = str(data['email']).lower().strip()
        username = str(data['username']).lower().strip()
        password = str(data['password']).lower()

        # validating data
        if re.match(app.config['EMAIL_PATTERN'], email) is None:
            abort(422, 'Email is not valid')
        if len(username) < 4:
            abort(422, 'Username have to be at least 4 characters in length')
        if len(password) < 8:
            abort(422, 'Password have to be at least 8 characters in length')

        default_role = Role.query.filter_by(name="general").one_or_none().id

        new_user = User(first_name, last_name, email,
                        username, password, default_role)

        try:
            new_user.insert()
        except IntegrityError:
            # Integrity error means a unique value already exist in a different record
            if User.query.filter_by(email=email).one_or_none():
                msg = 'Email is already in use'
            else:
                msg = "Username is already in use"
            abort(422, msg)

        return jsonify({
            'success': True,
            'token': generate_token(new_user.username),
        })

    @app.get('/api/profile')
    @requires_auth()
    def show_profile():
        user = User.query.filter_by(username=get_jwt_sub()).first()
        profile = user.format()
        # include confidential data like id, email and phone
        profile.update(id=user.id, email=user.email, phone=user.phone)
        return jsonify({
            'success': True,
            'data': profile
        })

    @app.patch("/api/profile")
    @requires_auth()
    def patch_profile():
        data = request.get_json() or {}
        user = User.query.filter_by(username=get_jwt_sub()).first()
        # updating user data
        if 'first_name' in data:
            user.first_name = str(data['first_name']).lower().strip()
        if 'last_name' in data:
            user.last_name = str(data['last_name']).lower().strip()
        if 'email' in data:
            email = str(data['email']).lower().strip()
            if re.match(app.config['EMAIL_PATTERN'], email) is None:
                abort(422, 'Email is not valid')
            user.email = email
        # if 'username' in data:
        #     username = str(data['username']).lower().strip()
        #     if len(username) < 4:
        #         abort(422, 'Username have to be at least 4 characters in length')
        #     user.username = username
        if 'password' in data:
            password = str(data['password']).lower().strip()
            if len(password) < 8:
                abort(422, 'Password have to be at least 8 characters in length')
            # passwords have to be hashed first
            user.set_pw(password)
        if 'phone' in data:
            phone = data['phone']
            if phone and re.match(app.config['PHONE_PATTERN'], phone) is None:
                abort(422, 'Phone is not valid')
            user.phone = phone
        if 'job' in data:
            user.job = str(data['job']).lower().strip()
        if 'bio' in data:
            user.bio = str(data['bio']).lower().strip()
        if 'avatar' in data:
            if not path.isfile(path.join(app.config['UPLOAD_FOLDER'], data['avatar'])):
                abort(422, "Avatar is not valid")
            user.avatar = data['avatar']

        try:
            user.update()
        except IntegrityError:
            # Integrity error means a unique value already exist in a different record
            if 'email' in data and User.query.filter_by(email=data['email']).one_or_none():
                msg = 'Email is already in use'
            elif 'username' in data and User.query.filter_by(username=data['username']).one_or_none():
                msg = "Username is already in use"
            else:
                msg = "Phone is already in use"
            abort(422, msg)
        except Exception:
            abort(422)

        profile = user.format()
        # include confidential data like id, email and phone
        profile.update(id=user.id, email=user.email, phone=user.phone)
        return jsonify({
            'success': True,
            'data': profile
        })

    @app.get('/api/notifications')
    @requires_auth()
    def get_notifications():
        user = User.query.filter_by(username=get_jwt_sub()).first()
        notifications, meta = paginate(
            user.notifications.all(), request.args.get('page', 1, int))
        unread_count = user.notifications.filter_by(is_read=False).count()

        return jsonify({
            'success': True,
            'data': notification_schema.dump(notifications, many=True),
            'unread_count': unread_count,
            'meta': meta
        })

    @app.post('/api/notifications/<int:notification_id>/set-read')
    @requires_auth()
    def set_notification_as_read(notification_id):
        user = User.query.filter_by(username=get_jwt_sub()).first()
        notification: Notification = Notification.query.get(notification_id)
        if not notification:
            abort(404, "notification not found")
        if notification.user_id != user.id:
            raise AuthError('You can\'t mutate others notifications', 403)

        notification.is_read = True
        notification.update()

        unread_count = user.notifications.filter_by(is_read=False).count()

        return jsonify({
            'success': True,
            'data': {'id': notification.id, 'is_read': True},
            'unread_count': unread_count,
        })

    @app.get('/api/questions')
    @requires_auth(optional=True)
    def get_questions():
        search_term = request.args.get('searchTerm', '', str)
        query = Question.query.order_by(Question.created_at.desc())

        if search_term:
            all_questions = query.filter(
                Question.content.ilike(f'%{search_term}%')).all()
        else:
            all_questions = query.all()

        questions, meta = paginate(
            all_questions, request.args.get('page', 1, int))

        return jsonify({
            'success': True,
            'data': question_schema.dump(questions, many=True),
            'meta': meta,
            'search_term': search_term
        })

    @app.get('/api/questions/<int:question_id>')
    @requires_auth(optional=True)
    def show_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        return jsonify({
            'success': True,
            'data': question_schema.dump(question)
        })

    @app.get('/api/questions/<int:question_id>/answers')
    @requires_auth(optional=True)
    def get_question_answers(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'Question not found')

        answers, meta = paginate(
            question.answers, request.args.get('page', 1, int), 4)
        return jsonify({
            'success': True,
            'data': answer_schema.dump(answers, many=True),
            'meta': meta
        })

    @app.post('/api/questions')
    @requires_auth()
    def post_question():
        # excluding accepted_answer field from the schema (the question has no answers yet to accept one)
        new_question = QuestionSchema(exclude=["accepted_answer"]).load(request.json)
        new_question.insert()

        return jsonify({
            'success': True,
            'data': question_schema.dump(new_question)
        })

    @app.patch('/api/questions/<int:question_id>')
    @requires_auth()
    def patch_question(question_id):
        data = question_schema.load(request.json, partial=True)

        # check if the target question exists
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'question not found')

        user = User.query.filter_by(username=get_jwt_sub()).first()
        # check if current user owns the target question
        if user.id != question.user_id:
            raise AuthError('You can\'t update others questions', 403)

        # validate accepted_answer as it needs custom validation
        if 'accepted_answer' in data:
            answer = Answer.query.get(data['accepted_answer'])
            # the answer must not be None and should belong to the question
            if answer is None or answer.question_id != question_id:
                raise ValidationError({'accepted_answer': ["Not valid."]})

        question.query.update(values=data)
        question.update()

        return jsonify({
            'success': True,
            'data': question_schema.dump(question)
        })

    @app.post('/api/questions/<int:question_id>/vote')
    @requires_auth()
    def vote_question(question_id):
        data = vote_schema.load(request.json)

        # check if the target question exists
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'question not found')

        user = User.query.filter_by(username=get_jwt_sub()).first()
        if data['vote'] == 0:
            question.remove_vote(user)
        else:
            question.vote(user, True if data['vote'] == 1 else False)
            # notification
            content = 'Your question has new %s "%s"' % (
                'upvote' if data['vote'] == 1 else 'downvote', question.content)
            url = '/questions/%i' % question_id
            notification = Notification(user_id=question.user_id, content=content, url=url)
            notification.insert()

        return jsonify({
            'success': True,
            'data': QuestionSchema(only=('id', 'upvotes', 'downvotes', 'viewer_vote')).dump(question)
        })

    @app.delete('/api/questions/<int:question_id>')
    @requires_auth()
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)

        user = User.query.filter_by(username=get_jwt_sub()).first()
        # check if the current user owns the target question
        if user.id != question.user_id:
            if not requires_permission('delete:questions'):
                raise AuthError('You don\'t have '
                                'the authority to delete other users questions', 403)

        question.delete()
        return jsonify({
            'success': True,
            'deleted_id': int(question_id)
        })

    @app.get('/api/answers/<int:answer_id>')
    @requires_auth(optional=True)
    def show_answer(answer_id):
        answer = Answer.query.get(answer_id)
        if answer is None:
            abort(404)
        return jsonify({
            'success': True,
            'data': answer_schema.dump(answer)
        })

    @app.post('/api/answers')
    @requires_auth()
    def post_answer():
        new_answer = answer_schema.load(request.json)
        new_answer.insert()

        # notification
        content = 'Your question has new answer "%s"' % new_answer.question.content
        url = '/questions/%i' % new_answer.question_id
        notification = Notification(user_id=new_answer.question.user_id, content=content, url=url)
        notification.insert()

        return jsonify({
            'success': True,
            'data': answer_schema.dump(new_answer)
        })

    @app.patch('/api/answers/<int:answer_id>')
    @requires_auth()
    def patch_answer(answer_id):
        data = AnswerSchema(exclude=["question_id"]).load(request.json, partial=True)

        # check if the target answer exists
        answer = Answer.query.get(answer_id)
        if not answer:
            abort(404, "answer not found!")

        user = User.query.filter_by(username=get_jwt_sub()).first()
        # check if current user owns the target answer
        if user.id != answer.user_id:
            raise AuthError('You can\'t update others answers', 403)

        answer.query.update(values=data)
        answer.update()

        return jsonify({
            'success': True,
            'data': answer_schema.dump(answer)
        })

    @app.post('/api/answers/<int:answer_id>/vote')
    @requires_auth()
    def vote_answer(answer_id):
        data = vote_schema.load(request.json)

        answer = Answer.query.get(answer_id)

        # check if the target answer exists
        if answer is None:
            abort(404, 'answer not found')

        user = User.query.filter_by(username=get_jwt_sub()).first()
        if data['vote'] == 0:
            answer.remove_vote(user)
        else:
            answer.vote(user, True if data['vote'] == 1 else False)
            # notification
            content = 'Your answer has new %s "%s"' % (
                'upvote' if data['vote'] == 1 else 'downvote', answer.content)
            url = '/questions/%i?answer_id=%i' % (
                answer.question_id, answer_id)
            notification = Notification(user_id=answer.user_id, content=content, url=url)
            notification.insert()

        return jsonify({
            'success': True,
            'data': AnswerSchema(only=('id', 'upvotes', 'downvotes', 'viewer_vote')).dump(answer)
        })

    @app.delete('/api/answers/<int:answer_id>')
    @requires_auth()
    def delete_answer(answer_id):
        answer = Answer.query.get(answer_id)

        # check if the target answer exists
        if answer is None:
            abort(404)
        user = User.query.filter_by(username=get_jwt_sub()).first()
        # check if the current user owns the target answer
        if user.id != answer.user_id:
            if not requires_permission('delete:answers'):
                raise AuthError('You don\'t have '
                                'the authority to delete other users answers', 403)
        answer.delete()
        return jsonify({
            'success': True,
            'deleted_id': int(answer_id)
        })

    @app.get('/api/users/<username>')
    def show_user(username):
        user = User.query.filter_by(username=username).one_or_none()
        if not user:
            abort(404, 'User not found')

        return jsonify({
            'success': True,
            'data': user.format()
        })

    @app.get('/api/users/<username>/questions')
    @requires_auth(optional=True)
    def get_user_questions(username):
        user = User.query.filter_by(username=username).one_or_none()
        if not user:
            abort(404, 'User not found')

        questions, meta = paginate(
            user.questions, request.args.get('page', 1, int))

        return jsonify({
            'success': True,
            'data': question_schema.dump(questions, many=True),
            'meta': meta
        })

    @app.post('/api/report/question')
    @requires_auth()
    def report_question():
        username = get_jwt_sub()
        question_id = request.get_json().get('question_id')
        if question_id is None:
            abort(400, 'question_id expted in request body')
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'question not found!')

        msg = Message('Reporting question')
        # email admin (my self)
        msg.add_recipient(app.config.get('MAIL_DEFAULT_SENDER'))
        msg.body = 'user "%s" has reported question "%i"' % (
            username, question_id)
        msg.html = 'user <code>"%s"</code> has reported question <code>"%i"</code>' % (
            username, question_id)
        try:
            mail.send(msg)
        except Exception as e:
            abort(422, e)
        return jsonify({
            'success': True
        })

    @app.post('/api/report/answer')
    @requires_auth()
    def report_answer():
        username = get_jwt_sub()
        answer_id = request.get_json().get('answer_id')
        if answer_id is None:
            abort(400, 'answer_id expted in request body')
        answer = Answer.query.get(answer_id)
        if answer is None:
            abort(404, 'answer not found!')

        msg = Message('Reporting answer')
        # email admin (my self)
        msg.add_recipient(app.config.get('MAIL_DEFAULT_SENDER'))
        msg.body = 'user "%s" has reported answer "%i"' % (
            username, answer_id)
        msg.html = 'user <code>"%s"</code> has reported answer <code>"%i"</code>' % (
            username, answer_id)
        mail.send(msg)
        return jsonify({
            'success': True
        })

    ### HANDLING ERRORS ###

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

    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'error': 413
        }), 413

    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': error.code
        }), error.code

    @app.errorhandler(ValidationError)
    def marshmallow_error_handler(error):
        return jsonify({
            'success': False,
            'message': 'The given data was invalid.',
            'errors': error.messages,
        }), 400

    ### COMMANDS ###

    @app.cli.command('db_seed')
    def db_seed():
        # permissions
        delete_users = Permission('delete:users')
        delete_answers = Permission('delete:answers')
        delete_questions = Permission('delete:questions')
        # roles
        general = Role('general')
        superamdin = Role('superadmin')
        superamdin.permissions.extend(
            [delete_users, delete_answers, delete_questions])
        general.insert()
        superamdin.insert()

    return app
