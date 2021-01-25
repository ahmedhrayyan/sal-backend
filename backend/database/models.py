from sqlalchemy.sql.sqltypes import Boolean
from backend.database import db
from sqlalchemy import Column, Integer,  ForeignKey, DateTime, VARCHAR, Binary, exc, Text
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
    answers = db.relationship('Answer',
                              backref='question',
                              order_by='desc(Answer.created_at)',
                              lazy=True,
                              foreign_keys='Answer.question_id',
                              cascade="all")
    best_answer = db.Column(Integer, nullable=True)

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

    def format(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at,
            'best_answer': self.best_answer,
            'answers': [answer.id for answer in self.answers]
        }


class Answer(db.Model, BaseModel):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)

    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)

    def __init__(self, user_id, content, question_id):
        self.user_id = user_id
        self.content = content
        self.question_id = question_id

    def format(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'question_id': self.question_id,
            'created_at': self.created_at
        }


class User(db.Model, BaseModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(VARCHAR(20), nullable=False)
    last_name = Column(VARCHAR(20), nullable=False)
    email = Column(VARCHAR(60), nullable=False, unique=True)
    username = Column(VARCHAR(20), nullable=False, unique=True)
    password = Column(Binary, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    email_confirmed = Column(Boolean, default=False, nullable=False)
    job = Column(VARCHAR(50), nullable=True)
    phone = Column(VARCHAR(50), nullable=True, unique=True)
    avatar = Column(Text, nullable=True)
    created_at = Column(DateTime(), default=datetime.utcnow, nullable=False)
    notifications = db.relationship('Notification',
                                    order_by='desc(Notification.created_at)',
                                    lazy=True,
                                    cascade="all")

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

    def checkpw(self, password):
        return bcrypt.checkpw(bytes(password, 'utf-8'), self.password)

    def set_pw(self, password):
        self.password = bcrypt.hashpw(
            bytes(password, 'utf-8'), bcrypt.gensalt(12))

    def format(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username,
            'phone': self.phone,
            'job': self.job,
            'avatar': self.avatar,
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
            'permissions': [permission.id for permission in self.permissions]
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

    def __init__(self, user_id, body):
        self.user_id = user_id
        self.body = body

    def format(self):
        return {
            'id': self.id,
            'body': self.body,
            'created_at': self.created_at
        }
