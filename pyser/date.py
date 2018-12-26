date_format = '%Y-%m-%d'
time_format = '%H:%M:%S'
datetime_format = '{}T{}'.format(date_format, time_format)
peewee_datetime_format = '{} {}.%f'.format(date_format, time_format)
