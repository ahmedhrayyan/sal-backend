from auth import get_jwt_sub
from sqlalchemy.orm import backref
from db import db
from flask import request
from sqlalchemy import Column, Integer, ForeignKey, DateTime, VARCHAR, LargeBinary, exc, Text, Boolean
from datetime import datetime
import bcrypt


class BaseModel:
    """ Helper class witch add basic methods to sub models """

    def __init__(self, **kwargs):
        pass

    def update(self):
        """ updating element in db  """
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        """ delete item from db """
        try:
            db.session.delete(self)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def insert(self):
        """ insert item into db """
        try:
            db.session.add(self)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise e


class QuestionVote(db.Model):
    __tablename__ = "questions_votes"
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    vote = Column(Boolean, nullable=False)

    question = db.relationship('Question', backref=backref(
        "votes", cascade="all, delete-orphan", lazy="dynamic"))
    user = db.relationship('User', backref=backref(
        "questions_votes", cascade="all, delete-orphan", lazy="dynamic"))


class AnswerVote(db.Model):
    __tablename__ = "answers_votes"
    answer_id = Column(Integer, ForeignKey('answers.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    vote = Column(Boolean, nullable=False)

    answer = db.relationship('Answer', backref=backref(
        "votes", cascade="all, delete-orphan", lazy="dynamic"))
    user = db.relationship('User', backref=backref(
        "answers_votes", cascade="all, delete-orphan", lazy="dynamic"))


class User(db.Model, BaseModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(VARCHAR(20), nullable=False)
    last_name = Column(VARCHAR(20), nullable=False)
    email = Column(VARCHAR(60), nullable=False, unique=True)
    username = Column(VARCHAR(20), nullable=False, unique=True)
    _password = Column(LargeBinary, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    email_confirmed = Column(Boolean, default=False, nullable=False)
    job = Column(VARCHAR(50), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(VARCHAR(50), nullable=True, unique=True)
    avatar = Column(Text, nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)
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

    def format(self):
        # prepend uploads endpoint to self.avatar
        avatar = self.avatar
        if avatar:
            try:
                # will fail if called outside an endpoint
                avatar = request.root_url + 'uploads/' + avatar
            except RuntimeError:
                pass

        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': '%s %s' % (self.first_name, self.last_name),
            'username': self.username,
            'job': self.job,
            'bio': self.bio,
            'avatar': avatar,
            'questions_count': len(self.questions),
            'answers_count': len(self.answers),
            'created_at': self.created_at
        }


class Question(db.Model, BaseModel):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)
    accepted_answer = Column(Integer, ForeignKey(
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


class Answer(db.Model, BaseModel):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)

    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)

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
                             Column('role_id', Integer,
                                    ForeignKey('roles.id'), nullable=False),
                             Column('permission_id', Integer, ForeignKey('permissions.id'), nullable=False))


class Role(db.Model, BaseModel):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(20), nullable=False, unique=True)
    permissions = db.relationship(
        'Permission', secondary=roles_permissions, backref='roles', lazy=True)

    def __init__(self, name: str):
        self.name = name

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Permission(db.Model, BaseModel):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(40), nullable=False, unique=True)

    def __init__(self, name: str):
        self.name = name

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Notification(db.Model, BaseModel):
    """ Notification model """

    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)
