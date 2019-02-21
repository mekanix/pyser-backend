"""Peewee migrations -- 001_initial.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class BaseModel(pw.Model):
        id = pw.AutoField()

        class Meta:
            table_name = "basemodel"

    @migrator.create_model
    class User(pw.Model):
        id = pw.AutoField()
        active = pw.BooleanField(constraints=[SQL("DEFAULT True")])
        admin = pw.BooleanField(constraints=[SQL("DEFAULT False")])
        confirmed_at = pw.DateTimeField(null=True)
        email = pw.TextField()
        password = pw.TextField()
        firstName = pw.TextField(null=True)
        lastName = pw.TextField(null=True)
        bio = pw.TextField(null=True)
        twitter = pw.TextField(null=True)
        facebook = pw.TextField(null=True)

        class Meta:
            table_name = "users"

    @migrator.create_model
    class Blog(pw.Model):
        id = pw.AutoField()
        author = pw.ForeignKeyField(backref='blogs', column_name='author_id', field='id', model=migrator.orm['users'])
        content = pw.TextField()
        date = pw.DateTimeField()
        published = pw.BooleanField()
        slug = pw.TextField()
        title = pw.TextField()

        class Meta:
            table_name = "blog"

    @migrator.create_model
    class Event(pw.Model):
        id = pw.AutoField()
        year = pw.IntegerField(unique=True)
        published = pw.BooleanField(constraints=[SQL("DEFAULT False")])
        mainHall = pw.TextField()

        class Meta:
            table_name = "event"

    @migrator.create_model
    class CfS(pw.Model):
        id = pw.AutoField()
        email = pw.TextField()
        organization = pw.TextField()
        message = pw.TextField()
        event = pw.ForeignKeyField(backref='cfs', column_name='event_id', field='id', model=migrator.orm['event'])

        class Meta:
            table_name = "cfs"

    @migrator.create_model
    class GalleryAlbum(pw.Model):
        id = pw.AutoField()
        event = pw.ForeignKeyField(backref='albums', column_name='event_id', field='id', model=migrator.orm['event'], null=True)
        name = pw.TextField(index=True)

        class Meta:
            table_name = "galleryalbum"

    @migrator.create_model
    class GalleryFile(pw.Model):
        id = pw.AutoField()
        album = pw.ForeignKeyField(backref='files', column_name='album_id', field='id', model=migrator.orm['galleryalbum'])
        filename = pw.TextField(index=True)

        class Meta:
            table_name = "galleryfile"

    @migrator.create_model
    class Hall(pw.Model):
        id = pw.AutoField()
        name = pw.TextField()
        event = pw.ForeignKeyField(backref='halls', column_name='event_id', field='id', model=migrator.orm['event'])

        class Meta:
            table_name = "hall"

    @migrator.create_model
    class Role(pw.Model):
        id = pw.AutoField()
        description = pw.TextField(null=True)
        name = pw.CharField(max_length=255, unique=True)

        class Meta:
            table_name = "role"

    @migrator.create_model
    class Talk(pw.Model):
        id = pw.AutoField()
        description = pw.TextField()
        end = pw.DateTimeField(null=True)
        hall = pw.TextField(null=True)
        published = pw.BooleanField(constraints=[SQL("DEFAULT False")])
        start = pw.DateTimeField(null=True)
        title = pw.TextField()
        type = pw.TextField()
        duration = pw.IntegerField()
        user = pw.ForeignKeyField(backref='talks', column_name='user_id', field='id', model=migrator.orm['users'])
        event = pw.ForeignKeyField(backref='talks', column_name='event_id', field='id', model=migrator.orm['event'])

        class Meta:
            table_name = "talk"

    @migrator.create_model
    class UserRoles(pw.Model):
        id = pw.AutoField()
        role = pw.ForeignKeyField(backref='users', column_name='role_id', field='id', model=migrator.orm['role'])
        user = pw.ForeignKeyField(backref='roles', column_name='user_id', field='id', model=migrator.orm['users'])

        class Meta:
            table_name = "userroles"



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('userroles')

    migrator.remove_model('talk')

    migrator.remove_model('role')

    migrator.remove_model('hall')

    migrator.remove_model('galleryfile')

    migrator.remove_model('galleryalbum')

    migrator.remove_model('event')

    migrator.remove_model('cfs')

    migrator.remove_model('blog')

    migrator.remove_model('users')

    migrator.remove_model('basemodel')
