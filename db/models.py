from sqlalchemy.orm import backref
from db import db
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import bcrypt


class BaseModel:
    """ Helper class witch add basic methods to sub models """

    def __init__(self, **kwargs):
        # required: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application
        super(BaseModel, self).__init__(**kwargs)

    def update(self, **kwargs):
        """ update element in db  """

        # update fields using python dict
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        """ delete item from db """
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def insert(self):
        """ insert item into db """
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e


class QuestionVote(db.Model):
    __tablename__ = "questions_votes"
    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id'), primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    vote = sa.Column(sa.Boolean, nullable=False)

    question = db.relationship('Question', backref=backref(
        "votes", cascade="all, delete-orphan", lazy="dynamic"))
    user = db.relationship('User', backref=backref(
        "questions_votes", cascade="all, delete-orphan", lazy="dynamic"))


class AnswerVote(db.Model):
    __tablename__ = "answers_votes"
    answer_id = sa.Column(sa.Integer, sa.ForeignKey('answers.id'), primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    vote = sa.Column(sa.Boolean, nullable=False)

    answer = db.relationship('Answer', backref=backref(
        "votes", cascade="all, delete-orphan", lazy="dynamic"))
    user = db.relationship('User', backref=backref(
        "answers_votes", cascade="all, delete-orphan", lazy="dynamic"))


class User(BaseModel, db.Model):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.VARCHAR(20), nullable=False)
    last_name = sa.Column(sa.VARCHAR(20), nullable=False)
    email = sa.Column(sa.VARCHAR(60), nullable=False, unique=True)
    username = sa.Column(sa.VARCHAR(20), nullable=False, unique=True)
    _password = sa.Column(sa.LargeBinary, nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey('roles.id'), nullable=False)
    email_confirmed = sa.Column(sa.Boolean, default=False, nullable=False)
    job = sa.Column(sa.VARCHAR(50), nullable=True)
    bio = sa.Column(sa.Text, nullable=True)
    phone = sa.Column(sa.VARCHAR(50), nullable=True, unique=True)
    avatar = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow, nullable=False)
    questions = db.relationship(
        'Question', backref='user', order_by='desc(Question.created_at)', lazy=True, cascade='all')
    answers = db.relationship(
        'Answer', backref='user', order_by='desc(Answer.created_at)', lazy=True, cascade='all')
    notifications = db.relationship(
        'Notification', order_by='desc(Notification.created_at)', lazy="dynamic", cascade='all')

    @property
    def password(self):
        return "***"

    @password.setter
    def password(self, value):
        self._password = bcrypt.hashpw(bytes(value, 'utf-8'), bcrypt.gensalt(12))

    def checkpw(self, password: str):
        """ Check if the provided password is equal to user password """
        return bcrypt.checkpw(bytes(password, 'utf-8'), self._password)


class Question(BaseModel, db.Model):
    __tablename__ = 'questions'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow, nullable=False)
    accepted_answer = sa.Column(sa.Integer, sa.ForeignKey(
        'answers.id', use_alter=True, ondelete="SET NULL"), nullable=True)
    answers = db.relationship('Answer', backref='question',
                              order_by='desc(Answer.created_at)', lazy=True, foreign_keys='Answer.question_id',
                              cascade='all')

    def vote(self, user: User, vote: bool):
        """ upvote or downvote a question """
        if self.has_voted(user):
            # update the vote itself if the user has already voted
            vote_obj = self.votes.filter_by(user=user).first()
            vote_obj.vote = vote
        else:
            # working with the association pattern as detailed in the docs
            # ref: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
            vote = QuestionVote(vote=vote)
            vote.user = user
            self.votes.append(vote)
        # update in either cases
        self.update()

    def remove_vote(self, user: User):
        """ remove user vote """
        self.votes.filter_by(user=user).delete()
        self.update()

    def get_user_vote(self, user: User):
        """ Returns user vote for the question. None if the user has not voted """
        if self.has_voted(user):
            return self.votes.filter_by(user=user).first().vote
        else:
            return None

    def has_voted(self, user: User) -> bool:
        """ Check weather a user has voted the question """
        return self.votes.filter_by(user=user).first() is not None


class Answer(BaseModel, db.Model):
    __tablename__ = 'answers'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow, nullable=False)

    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id'), nullable=False)

    def vote(self, user: User, vote: bool):
        """ upvote or down-vote a question """
        if self.has_voted(user):
            # update the vote itself if the user has already voted
            vote_obj = self.votes.filter_by(user=user).first()
            vote_obj.vote = vote
        else:
            # working with the association pattern as detailed in the docs
            # ref: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
            vote = AnswerVote(vote=vote)
            vote.user = user
            self.votes.append(vote)
        # update in either cases
        self.update()

    def remove_vote(self, user: User):
        """ remove user vote """
        self.votes.filter_by(user=user).delete()
        self.update()

    def get_user_vote(self, user: User):
        """ Returns user vote for the question. None if the user has not voted """
        if self.has_voted(user):
            return self.votes.filter_by(user=user).first().vote
        else:
            return None

    def has_voted(self, user: User) -> bool:
        """ Check weather the user has voted the question """
        return self.votes.filter_by(user=user).first() is not None


roles_permissions = db.Table('roles_permissions',
                             sa.Column('role_id', sa.Integer,
                                       sa.ForeignKey('roles.id'), nullable=False),
                             sa.Column('permission_id', sa.Integer, sa.ForeignKey('permissions.id'), nullable=False))


class Role(BaseModel, db.Model):
    __tablename__ = 'roles'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.VARCHAR(20), nullable=False, unique=True)
    permissions = db.relationship(
        'Permission', secondary=roles_permissions, backref='roles', lazy=True)


class Permission(BaseModel, db.Model):
    __tablename__ = 'permissions'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.VARCHAR(40), nullable=False, unique=True)


class Notification(BaseModel, db.Model):
    """ Notification model """

    __tablename__ = 'notifications'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    url = sa.Column(sa.Text, nullable=False)
    is_read = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow, nullable=False)
