from bleach import clean
from marshmallow import Schema, fields, post_load, EXCLUDE, validate
from auth import get_jwt_sub
from .models import Question, Answer, User, Role


class BaseSchema(Schema):
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        # Exclude unknown fields in the deserialized output
        unknown = EXCLUDE


LoginSchema = BaseSchema.from_dict({'username': fields.Str(required=True), 'password': fields.Str(required=True)})
login_schema = LoginSchema()

VoteSchema = BaseSchema.from_dict({'vote': fields.Int(validate=validate.OneOf([0, 1, 2]))})
vote_schema = VoteSchema()


class NotificationSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    is_read = fields.Bool(dump_only=True)
    content = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)


notification_schema = NotificationSchema()


class UserSchema(BaseSchema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True,)
    email_confirmed = fields.Bool(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(4, 20))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(8, 28))
    job = fields.Str(validate=validate.Length(max=50))
    bio = fields.Str()
    phone = fields.Str()
    avatar = fields.Str()
    questions_count = fields.Function(lambda obj: len(obj.questions), dump_only=True)
    answers_count = fields.Function(lambda obj: len(obj.answers), dump_only=True)

    @post_load
    def create_user(self, data, **kwargs):
        # strip & lowercase the email field
        if 'email' in data:
            data['email'] = data['email'].strip().lower()

        # if partial option was passed, return the dictionary of fields not an object (useful for updating)
        if kwargs.get("partial"):
            return data

        default_role = Role.query.filter_by(name="general").one_or_none()
        return User(role_id=default_role.id, **data)


user_schema = UserSchema()


class BaseQASchema(BaseSchema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    upvotes = fields.Function(lambda obj: obj.votes.filter_by(vote=True).count(), dump_only=True)
    downvotes = fields.Function(lambda obj: obj.votes.filter_by(vote=False).count(), dump_only=True)
    viewer_vote = fields.Method("get_viewer_vote", dump_only=True)
    user = fields.Nested(UserSchema(only=['id', 'first_name', 'last_name', 'avatar', 'job']))

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
