from marshmallow import Schema, fields, validates, ValidationError, validates_schema, pre_load, post_load, EXCLUDE, \
    validate
from bleach import clean
from auth import get_jwt_sub
from .models import Question, Answer, User


class BaseSchema(Schema):
    class Meta:
        # Exclude unknown fields in the deserialized output
        unknown = EXCLUDE


class NotificationSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    is_read = fields.Bool(dump_only=True)
    content = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)


notification_schema = NotificationSchema()


class BaseQASchema(BaseSchema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    upvotes = fields.Function(lambda obj: obj.votes.filter_by(vote=True).count(), dump_only=True)
    downvotes = fields.Function(lambda obj: obj.votes.filter_by(vote=False).count(), dump_only=True)
    viewer_vote = fields.Method("get_viewer_vote", dump_only=True)

    def get_viewer_vote(self, obj):
        user = User.query.filter_by(username=get_jwt_sub()).first()
        return obj.get_user_vote(user) if user else None


class QuestionSchema(BaseQASchema):
    accepted_answer = fields.Int()
    answers_count = fields.Function(lambda obj: len(obj.answers), dump_only=True)

    @post_load
    def create_question(self, data, **kwargs):
        # if partial option was passed, return the dictionary of fields not an object (useful for updating)
        if kwargs.get("partial"):
            return data

        user = User.query.filter_by(username=get_jwt_sub()).first()
        if not data or not user:
            return None

        return Question(user_id=user.id, **data)


question_schema = QuestionSchema()


class AnswerSchema(BaseQASchema):
    question_id = fields.Int(required=True, validate=lambda id: Question.query.get(id) is not None)

    @post_load
    def create_answer(self, data, **kwargs):
        # sanitize content
        data['content'] = clean(data['content'])

        # if partial option was passed, return the dictionary of fields not an object (useful for updating)
        if kwargs.get("partial"):
            return data

        user = User.query.filter_by(username=get_jwt_sub()).first()
        if not data or not user:
            return None

        return Answer(user_id=user.id, **data)


answer_schema = AnswerSchema()


class VoteSchema(BaseSchema):
    vote = fields.Int(validate=validate.OneOf([0, 1, 2]))


vote_schema = VoteSchema()
