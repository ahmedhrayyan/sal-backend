import imghdr
from os import path, mkdir
from typing import BinaryIO
from uuid import uuid4
from flask import Flask, jsonify, request, abort, send_from_directory, render_template
from werkzeug.exceptions import NotFound
from flask_cors import CORS
from flask_mail import Mail, Message
from marshmallow import ValidationError, fields
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from auth import AuthError, generate_token, requires_auth, requires_permission, get_jwt_sub
from config import ProductionConfig
from db import setup_db
from db.models import Answer, Notification, Permission, Question, User, Role
import db.schemas as schemas


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


def create_app(config=ProductionConfig):
    """ create and configure the app """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    CORS(app)
    mail = Mail(app)

    setup_db(app)

    def create_notification(user_id: int, content: str, url: str):
        notification = Notification(user_id=user_id, content=content, url=url)
        try:
            notification.insert()
        except SQLAlchemyError as error:
            # just log errors in case of creating notification error
            app.logger.exception(error)

    # -------------- ENDPOINTS ------------------- #

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

        # Create upload folder if it doesn't exist
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
        except NotFound:
            abort(404, "File not found")

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
            'token': generate_token(user.username, permissions),
        })

    @app.post("/api/register")
    def register():
        new_user = schemas.user_schema.load(request.json)

        try:
            new_user.insert()
        except IntegrityError as e:
            abort(422, e.orig.diag.message_detail)

        return jsonify({
            'success': True,
            'token': generate_token(new_user.username),
        })

    @app.get('/api/profile')
    @requires_auth()
    def show_profile():
        user = User.query.filter_by(username=get_jwt_sub()).first()
        return jsonify({
            'success': True,
            'data': schemas.user_schema.dump(user)
        })

    @app.patch("/api/profile")
    @requires_auth()
    def patch_profile():
        data = schemas.UserSchema(exclude=['password']).load(request.json, partial=True)
        user = User.query.filter_by(username=get_jwt_sub()).first()

        try:
            user.update(**data)
        except IntegrityError as e:
            abort(422, e.orig.diag.message_detail)

        return jsonify({
            'success': True,
            'data': schemas.user_schema.dump(user)
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
            'data': schemas.notification_schema.dump(notifications, many=True),
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
            'data': schemas.question_schema.dump(questions, many=True),
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
            'data': schemas.question_schema.dump(question)
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
            'data': schemas.answer_schema.dump(answers, many=True),
            'meta': meta
        })

    @app.post('/api/questions')
    @requires_auth()
    def post_question():
        # excluding accepted_answer field from the schema (the question has no answers yet to accept one)
        new_question = schemas.QuestionSchema(exclude=["accepted_answer"]).load(request.json)
        new_question.insert()

        return jsonify({
            'success': True,
            'data': schemas.question_schema.dump(new_question)
        })

    @app.patch('/api/questions/<int:question_id>')
    @requires_auth()
    def patch_question(question_id):
        data = schemas.question_schema.load(request.json, partial=True)

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

        question.update(**data)

        return jsonify({
            'success': True,
            'data': schemas.question_schema.dump(question)
        })

    @app.post('/api/questions/<int:question_id>/vote')
    @requires_auth()
    def vote_question(question_id):
        data = schemas.vote_schema.load(request.json)

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
            create_notification(question.user_id, content, url)

        return jsonify({
            'success': True,
            'data': schemas.QuestionSchema(only=('id', 'upvotes', 'downvotes', 'viewer_vote')).dump(question)
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
            'data': schemas.answer_schema.dump(answer)
        })

    @app.post('/api/answers')
    @requires_auth()
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
    @requires_auth()
    def patch_answer(answer_id):
        data = schemas.AnswerSchema(exclude=["question_id"]).load(request.json, partial=True)

        # check if the target answer exists
        answer = Answer.query.get(answer_id)
        if not answer:
            abort(404, "answer not found!")

        user = User.query.filter_by(username=get_jwt_sub()).first()
        # check if current user owns the target answer
        if user.id != answer.user_id:
            raise AuthError('You can\'t update others answers', 403)

        answer.update(**data)

        return jsonify({
            'success': True,
            'data': schemas.answer_schema.dump(answer)
        })

    @app.post('/api/answers/<int:answer_id>/vote')
    @requires_auth()
    def vote_answer(answer_id):
        data = schemas.vote_schema.load(request.json)

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
            create_notification(answer.user_id, content, url)

        return jsonify({
            'success': True,
            'data': schemas.AnswerSchema(only=('id', 'upvotes', 'downvotes', 'viewer_vote')).dump(answer)
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
            'data': schemas.question_schema.dump(questions, many=True),
            'meta': meta
        })

    @app.post('/api/report/question')
    @requires_auth()
    def report_question():
        username = get_jwt_sub()
        data = schemas.report_q_schema.load(request.json)

        question = Question.query.get(data['question_id'])
        if question is None:
            abort(404, 'question not found!')

        msg = Message('Reporting question')
        # email admin (my self)
        msg.add_recipient(app.config.get('MAIL_DEFAULT_SENDER'))
        msg.body = 'user "%s" has reported question "%i"' % (
            username, data['question_id'])
        msg.html = 'user <code>"%s"</code> has reported question <code>"%i"</code>' % (
            username, data['question_id'])

        mail.send(msg)

        return jsonify({
            'success': True
        })

    @app.post('/api/report/answer')
    @requires_auth()
    def report_answer():
        username = get_jwt_sub()
        data = schemas.report_a_schema.load(request.json)

        answer = Answer.query.get(data['answer_id'])
        if answer is None:
            abort(404, 'question not found!')

        msg = Message('Reporting question')
        # email admin (my self)
        msg.add_recipient(app.config.get('MAIL_DEFAULT_SENDER'))
        msg.body = 'user "%s" has reported question "%i"' % (
            username, data['answer_id'])
        msg.html = 'user <code>"%s"</code> has reported question <code>"%i"</code>' % (
            username, data['answer_id'])

        mail.send(msg)

        return jsonify({
            'success': True
        })

    # -------------- HANDLING ERRORS ------------------- #

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
        delete_users = Permission('delete:users')
        delete_answers = Permission('delete:answers')
        delete_questions = Permission('delete:questions')
        # roles
        general = Role('general')
        super_admin = Role('super_admin')
        super_admin.permissions.extend(
            [delete_users, delete_answers, delete_questions])
        general.insert()
        super_admin.insert()

    return app
