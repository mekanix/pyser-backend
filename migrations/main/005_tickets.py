import peewee as pw

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    @migrator.create_model
    class Ticket(pw.Model):
        id = pw.AutoField()
        canceled = pw.BooleanField(constraints=[SQL("DEFAULT False")])
        identifier = pw.TextField()
        date = pw.DateTimeField()
        event = pw.ForeignKeyField(
            backref='tickets',
            column_name='event_id',
            field='id',
            model=migrator.orm['event']
        )
        visitor = pw.ForeignKeyField(
            backref='tickets',
            column_name='visitor_id',
            field='id',
            model=migrator.orm['users']
        )

        class Meta:
            table_name = "ticket"


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_model('ticket')
