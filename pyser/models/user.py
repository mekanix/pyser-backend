import peewee
from freenit.models.user import User as BaseUser


class User(BaseUser):
    avatar = peewee.TextField(null=True)
    biography = peewee.TextField(null=True)
    facebook = peewee.TextField(null=True)
    firstName = peewee.TextField(null=True)
    lastName = peewee.TextField(null=True)
    twitter = peewee.TextField(null=True)
    volunteer = peewee.BooleanField(null=True)

    class Meta:
        table_name = 'users'
