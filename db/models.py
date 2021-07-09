from db import db
from flask import request
from sqlalchemy import Column, Integer,  ForeignKey, DateTime, VARCHAR, LargeBinary, exc, Text, Boolean
from datetime import datetime
import bcrypt


class BaseModel:
    def update(self):
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise e


class Question(db.Model, BaseModel):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)
    accepted_answer = Column(Integer, ForeignKey(
        'answers.id', use_alter=True), nullable=True)
    answers = db.relationship('Answer', backref='question',
                              order_by='desc(Answer.created_at)', lazy=True, foreign_keys='Answer.question_id', cascade='all')

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

    def format(self):
        # query showing list of question's answers
        query = Answer.query.filter_by(question_id=self.id)
        # prime answer will be either the either the accepted or the latest answer
        if (self.accepted_answer):
            prime_answer = Answer.query.get(self.accepted_answer)
        else:
            prime_answer = query.order_by(Answer.created_at.desc()).first()

        return {
            'id': self.id,
            'user': self.user.format(),
            'content': self.content,
            'created_at': self.created_at,
            'accepted_answer': self.accepted_answer,
            'answers_count': query.count(),
            'prime_answer': prime_answer and prime_answer.format()
        }


class Answer(db.Model, BaseModel):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)

    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)

    def __init__(self, user_id: int, question_id: int, content: str):
        self.user_id = user_id
        self.content = content
        self.question_id = question_id

    def format(self):
        return {
            'id': self.id,
            'user': self.user.format(),
            'question_id': self.question_id,
            'content': self.content,
            'created_at': self.created_at
        }


class User(db.Model, BaseModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(VARCHAR(20), nullable=False)
    last_name = Column(VARCHAR(20), nullable=False)
    email = Column(VARCHAR(60), nullable=False, unique=True)
    username = Column(VARCHAR(20), nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    email_confirmed = Column(Boolean, default=False, nullable=False)
    job = Column(VARCHAR(50), nullable=True)
    phone = Column(VARCHAR(50), nullable=True, unique=True)
    avatar = Column(Text, nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)
    questions = db.relationship(
        'Question', backref='user', order_by='desc(Question.created_at)', lazy=True, cascade='all')
    answers = db.relationship(
        'Answer', backref='user', order_by='desc(Answer.created_at)', lazy=True, cascade='all')
    notifications = db.relationship(
        'Notification', order_by='desc(Notification.created_at)', lazy=True, cascade='all')

    def __init__(self, first_name, last_name, email, username, password, role_id, job=None, phone=None, avatar=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = bcrypt.hashpw(
            bytes(password, 'utf-8'), bcrypt.gensalt(12))
        self.job = job
        self.role_id = role_id
        self.phone = phone
        self.avatar = avatar

    def checkpw(self, password: str):
        return bcrypt.checkpw(bytes(password, 'utf-8'), self.password)

    def set_pw(self, password: str):
        self.password = bcrypt.hashpw(
            bytes(password, 'utf-8'), bcrypt.gensalt(12))

    def format(self):
        # prepend uploads endpoint to self.avatar
        avatar = self.avatar
        if (avatar):
            try:
                # will fail if called outside an endpoint
                avatar = request.root_url + 'uploads/' + avatar
            except RuntimeError:
                pass

        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username,
            'phone': self.phone,
            'job': self.job,
            'avatar': avatar,
            'created_at': self.created_at
        }


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

    def __init__(self, name):
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

    def __init__(self, name):
        self.name = name

    def format(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Notification(db.Model, BaseModel):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

    def format(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at
        }
