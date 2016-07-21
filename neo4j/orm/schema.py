import marshmallow


Field = marshmallow.fields.Field
Str = marshmallow.fields.Str
Int = marshmallow.fields.Int
Float = marshmallow.fields.Float
Number = marshmallow.fields.Number
Bool = marshmallow.fields.Bool
Url = marshmallow.fields.Url
Email = marshmallow.fields.Email
Dict = marshmallow.fields.Dict
Nested = marshmallow.fields.Nested
List = marshmallow.fields.List


class Schema(marshmallow.Schema):
    class Meta(object):
        strict = True
