from marshmallow import Schema, fields


class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    is_read = fields.Bool(dump_only=True)
    content = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)


notification_schema = NotificationSchema()
