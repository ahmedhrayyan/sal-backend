import imghdr
import redis
import re
from typing import BinaryIO
from flask import Flask, jsonify, request, abort, render_template
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt, current_user
from flask_mail import Mail, Message
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pyuploadcare import Uploadcare
import db.schemas as schemas
from config import ProductionConfig
from db import setup_db
from db.models import Answer, Notification, Permission, Question, User, Role


def parse_integrity_error(message: str) -> str:
    """ Format SQLAlchemy Integrity error """
    # Select unique field key & value from error message (they usually exist in parentheses)
    unique_field = re.findall("\((\w+)\)", message)  # regexp ta capture whatever in parentheses in a string
    if len(unique_field) == 2:
        return f'Account with {unique_field[0]} ({unique_field[1]}) already exists'
    else:
        # just return the error message if our regex was not able to select unique key field & value
        # happens because different databases have different message formats
        return message


def validate_image(stream: BinaryIO):
    """ Return correct image extension """
    # check file format
    header = stream.read(512)
    stream.seek(0)
    extension = imghdr.what(None, header)
    # jpeg normally uses jpg file extension
    return extension if extension != "jpeg" else "jpg"


def paginate(items: list, page: int = 1, per_page: int = 20):
    """ Return a list of paginated items and a dict contains metadata """
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    meta = {
        'total': len(items),
        'current_page': page,
        'per_page': per_page
    }
    return items[start_index:end_index], meta


def requires_permission(required_permission: str) -> bool:
    """ In a protected endpoint, check if a specific permission exists in the current user """
    permissions = get_jwt().get('permissions')
    return permissions is not None and required_permission in permissions


def create_app(config=ProductionConfig):
    """ create and configure the app """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    CORS(app)
    mail = Mail(app)
    jwt = JWTManager(app)
    uploadcare = Uploadcare(public_key=config.UCARE_PUBLIC_KEY, secret_key=config.UCARE_SECRET_KEY)

    setup_db(app)

    jwt_redis_blocklist = redis.from_url(config.REDIS_URL, decode_responses=True)

    def create_notification(user_id: int, content: str, url: str):
        notification = Notification(user_id=user_id, content=content, url=url)
        try:
            notification.insert()
        except SQLAlchemyError as error:
            # just log errors in case of creating notification error
            app.logger.exception(error)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    # -------------- ENDPOINTS ------------------- #

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.post("/api/upload")
    @jwt_required()
    def upload():
        if 'file' not in request.files:
            abort(400, "No file founded")
        file = request.files['file']

        if file.filename == '':
            abort(400, 'No selected file')
        file_ext = validate_image(file.stream)
        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            abort(422, 'You cannot upload %s files' % file_ext)
        # set name on uploadcare cdn
        file.name = file.filename

        ucare_file = uploadcare.upload(file)

        return jsonify({
            'success': True,
            'url': ucare_file.cdn_url
        })

    @app.post('/api/login')
    def login():
        data = schemas.login_schema.load(request.json)

        user = User.query.filter_by(username=data['username']).one_or_none()
        if not user or not user.checkpw(data['password']):
            abort(422, 'username or password is not correct')

        role = Role.query.get(user.role_id)
        permissions = [permission.name for permission in role.permissions]

        return jsonify({
            'success': True,
            'token': create_access_token(identity=user.id, additional_claims={'permissions': permissions}),
        })

    @app.post("/api/register")
    def register():
        new_user = schemas.user_schema.load(request.json)

        try:
            new_user.insert()
        except IntegrityError as e:
            abort(422, parse_integrity_error(str(e.orig)))

        return jsonify({
            'success': True,
            'token': create_access_token(identity=new_user.id, additional_claims={'permissions': []}),
        })

    @app.delete('/api/logout')
    @jwt_required()
    def logout():
        jti = get_jwt()['jti']
        jwt_redis_blocklist.set(jti, "", ex=config.JWT_ACCESS_TOKEN_EXPIRES)
        return jsonify({
            'success': True,
            'message': "Access token revoked"
        })

    @app.get('/api/profile')
    @jwt_required()
    def show_profile():
        return jsonify({
            'success': True,
            'data': schemas.user_schema.dump(current_user)
        })

    @app.patch("/api/profile")
    @jwt_required()
    def patch_profile():
        data = schemas.UserSchema(exclude=['password']).load(request.json, partial=True)

        try:
            current_user.update(**data)
        except IntegrityError as e:
            abort(422, parse_integrity_error(str(e.orig)))

        return jsonify({
            'success': True,
            'data': schemas.user_schema.dump(current_user)
        })

    @app.get('/api/notifications')
    @jwt_required()
    def get_notifications():
        notifications, meta = paginate(
            current_user.notifications.all(), request.args.get('page', 1, int))
        unread_count = current_user.notifications.filter_by(is_read=False).count()

        return jsonify({
            'success': True,
            'data': schemas.notification_schema.dump(notifications, many=True),
            'unread_count': unread_count,
            'meta': meta
        })

    @app.post('/api/notifications/<int:notification_id>/set-read')
    @jwt_required()
    def set_notification_as_read(notification_id):
        notification: Notification = Notification.query.get(notification_id)
        if not notification:
            abort(404, "notification not found")
        if notification.user_id != current_user.id:
            raise abort(403, 'You can\'t mutate others notifications')

        notification.is_read = True
        notification.update()

        unread_count = current_user.notifications.filter_by(is_read=False).count()

        return jsonify({
            'success': True,
            'data': {'id': notification.id, 'is_read': True},
            'unread_count': unread_count,
        })

    @app.get('/api/questions')
    @jwt_required(optional=True)
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
            'data': schemas.question_schema.dump(questions, many=True),
            'meta': meta,
            'search_term': search_term
        })

    @app.get('/api/questions/<int:question_id>')
    @jwt_required(optional=True)
    def show_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        return jsonify({
            'success': True,
            'data': schemas.question_schema.dump(question)
        })

    @app.get('/api/questions/<int:question_id>/answers')
    @jwt_required(optional=True)
    def get_question_answers(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'Question not found')

        answers, meta = paginate(
            question.answers, request.args.get('page', 1, int), 4)
        return jsonify({
            'success': True,
            'data': schemas.answer_schema.dump(answers, many=True),
            'meta': meta
        })

    @app.post('/api/questions')
    @jwt_required()
    def post_question():
        # excluding accepted_answer field from the schema (the question has no answers yet to accept one)
        new_question = schemas.QuestionSchema(exclude=["accepted_answer"]).load(request.json)
        new_question.insert()

        return jsonify({
            'success': True,
            'data': schemas.question_schema.dump(new_question)
        })

    @app.patch('/api/questions/<int:question_id>')
    @jwt_required()
    def patch_question(question_id):
        data = schemas.question_schema.load(request.json, partial=True)

        # check if the target question exists
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'question not found')

        # check if current user owns the target question
        if current_user.id != question.user_id:
            raise abort(403, 'You can\'t update others questions')

        # validate accepted_answer as it needs custom validation
        if 'accepted_answer' in data:
            answer = Answer.query.get(data['accepted_answer'])
            # the answer must not be None and should belong to the question
            if answer is None or answer.question_id != question_id:
                raise ValidationError({'accepted_answer': ["Not valid."]})

        question.update(**data)

        return jsonify({
            'success': True,
            'data': schemas.question_schema.dump(question)
        })

    @app.post('/api/questions/<int:question_id>/vote')
    @jwt_required()
    def vote_question(question_id):
        data = schemas.vote_schema.load(request.json)

        # check if the target question exists
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'question not found')

        if data['vote'] == 0:
            question.remove_vote(current_user)
        else:
            question.vote(current_user, True if data['vote'] == 1 else False)
            # notification
            content = 'Your question has new %s "%s"' % (
                'upvote' if data['vote'] == 1 else 'downvote', question.content)
            url = '/questions/%i' % question_id
            create_notification(question.user_id, content, url)

        return jsonify({
            'success': True,
            'data': schemas.QuestionSchema(only=('id', 'upvotes', 'downvotes', 'viewer_vote')).dump(question)
        })

    @app.delete('/api/questions/<int:question_id>')
    @jwt_required()
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)

        # check if the current user owns the target question
        if current_user.id != question.user_id:
            if not requires_permission('delete:questions'):
                abort(403, 'You don\'t have '
                           'the authority to delete other users questions')

        question.delete()
        return jsonify({
            'success': True,
            'deleted_id': int(question_id)
        })

    @app.get('/api/answers/<int:answer_id>')
    @jwt_required(optional=True)
    def show_answer(answer_id):
        answer = Answer.query.get(answer_id)
        if answer is None:
            abort(404)
        return jsonify({
            'success': True,
            'data': schemas.answer_schema.dump(answer)
        })

    @app.post('/api/answers')
    @jwt_required()
    def post_answer():
        new_answer = schemas.answer_schema.load(request.json)
        new_answer.insert()

        # notification
        content = 'Your question has new answer "%s"' % new_answer.question.content
        url = '/questions/%i' % new_answer.question_id
        create_notification(new_answer.question.user_id, content, url)

        return jsonify({
            'success': True,
            'data': schemas.answer_schema.dump(new_answer)
        })

    @app.patch('/api/answers/<int:answer_id>')
    @jwt_required()
    def patch_answer(answer_id):
        data = schemas.AnswerSchema(exclude=["question_id"]).load(request.json, partial=True)

        # check if the target answer exists
        answer = Answer.query.get(answer_id)
        if not answer:
            abort(404, "answer not found!")

        # check if current user owns the target answer
        if current_user.id != answer.user_id:
            raise abort(403, 'You can\'t update others answers')

        answer.update(**data)

        return jsonify({
            'success': True,
            'data': schemas.answer_schema.dump(answer)
        })

    @app.post('/api/answers/<int:answer_id>/vote')
    @jwt_required()
    def vote_answer(answer_id):
        data = schemas.vote_schema.load(request.json)

        answer = Answer.query.get(answer_id)

        # check if the target answer exists
        if answer is None:
            abort(404, 'answer not found')

        if data['vote'] == 0:
            answer.remove_vote(current_user)
        else:
            answer.vote(current_user, True if data['vote'] == 1 else False)
            # notification
            content = 'Your answer has new %s "%s"' % (
                'upvote' if data['vote'] == 1 else 'downvote', answer.content)
            url = '/questions/%i?answer_id=%i' % (
                answer.question_id, answer_id)
            create_notification(answer.user_id, content, url)

        return jsonify({
            'success': True,
            'data': schemas.AnswerSchema(only=('id', 'upvotes', 'downvotes', 'viewer_vote')).dump(answer)
        })

    @app.delete('/api/answers/<int:answer_id>')
    @jwt_required()
    def delete_answer(answer_id):
        answer = Answer.query.get(answer_id)

        # check if the target answer exists
        if answer is None:
            abort(404)
        # check if the current user owns the target answer
        if current_user.id != answer.user_id:
            if not requires_permission('delete:answers'):
                raise abort(403, 'You don\'t have '
                                 'the authority to delete other users answers')
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
            'data': schemas.user_schema.dump(user)
        })

    @app.get('/api/users/<username>/questions')
    @jwt_required(optional=True)
    def get_user_questions(username):
        user = User.query.filter_by(username=username).one_or_none()
        if not user:
            abort(404, 'User not found')

        questions, meta = paginate(
            user.questions, request.args.get('page', 1, int))

        return jsonify({
            'success': True,
            'data': schemas.question_schema.dump(questions, many=True),
            'meta': meta
        })

    @app.post('/api/report/question')
    @jwt_required()
    def report_question():
        data = schemas.report_q_schema.load(request.json)

        question = Question.query.get(data['question_id'])
        if question is None:
            abort(404, 'question not found!')

        msg = Message('Reporting question')
        # email admin (my self)
        msg.add_recipient(app.config.get('MAIL_DEFAULT_SENDER'))
        msg.body = 'user "%s" has reported question "%i"' % (
            current_user.username, data['question_id'])
        msg.html = 'user <code>"%s"</code> has reported question <code>"%i"</code>' % (
            current_user.username, data['question_id'])

        mail.send(msg)

        return jsonify({
            'success': True
        })

    @app.post('/api/report/answer')
    @jwt_required()
    def report_answer():
        data = schemas.report_a_schema.load(request.json)

        answer = Answer.query.get(data['answer_id'])
        if answer is None:
            abort(404, 'question not found!')

        msg = Message('Reporting question')
        # email admin (my self)
        msg.add_recipient(app.config.get('MAIL_DEFAULT_SENDER'))
        msg.body = 'user "%s" has reported question "%i"' % (
            current_user.username, data['answer_id'])
        msg.html = 'user <code>"%s"</code> has reported question <code>"%i"</code>' % (
            current_user.username, data['answer_id'])

        mail.send(msg)

        return jsonify({
            'success': True
        })

    # -------------- HANDLING ERRORS ------------------- #

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({'success': False, 'message': error_string}), 401

    @app.errorhandler(ValidationError)
    def marshmallow_error_handler(error):
        return jsonify({
            'success': False,
            'message': 'The given data was invalid.',
            'errors': error.messages,
        }), 400

    @app.errorhandler(Exception)
    def default_error_handler(error):
        # log error outside testing environment, useful for debugging
        if app.config['TESTING'] is not True:
            app.logger.exception(error)

        code = getattr(error, 'code', 500)
        message = getattr(error, 'description', "Something went wrong")

        return jsonify({
            'success': False,
            'message': message
        }), code if isinstance(code, int) else 500

    # -------------- COMMANDS ------------------- #

    @app.cli.command('db_seed')
    def db_seed():
        # permissions
        delete_users = Permission(name='delete:users')
        delete_answers = Permission(name='delete:answers')
        delete_questions = Permission(name='delete:questions')
        # roles
        general = Role(name='general')
        super_admin = Role(name='super_admin')
        super_admin.permissions.extend(
            [delete_users, delete_answers, delete_questions])
        general.insert()
        super_admin.insert()

    return app
