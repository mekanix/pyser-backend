import peewee as pw

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    migrator.add_fields(
        'users',
        avatar=pw.TextField(null=True),
        biography=pw.TextField(null=True)
    )
    migrator.remove_fields('users', 'bio')
    migrator.change_fields('ticket', canceled=pw.BooleanField(default=False))


def rollback(migrator, database, fake=False, **kwargs):
    migrator.add_fields(
        'users',
        bio=pw.TextField(null=True),
        lastName=pw.TextField(null=True),
        twitter=pw.TextField(null=True),
        firstName=pw.TextField(null=True),
        facebook=pw.TextField(null=True),
        volunteer=pw.BooleanField(null=True)
    )
