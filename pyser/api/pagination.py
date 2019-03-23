from math import ceil

from flask_restplus.reqparse import RequestParser

def_per_page = 10

parser = RequestParser()
parser.add_argument(
    'X-Page',
    default=0,
    help='Page number',
    location='headers',
    required=False,
    type=int,
)
parser.add_argument(
    'X-Per-Page',
    default=def_per_page,
    help='Items per page',
    location='headers',
    required=False,
    type=int,
)


def paginate(query, schema):
    args = parser.parse_args()
    page = args.get('X-Page')
    per_page = args.get('X-Per-Page')
    offset = page * per_page
    total = query.count()
    totalPages = ceil(total / float(per_page))
    paginated_query = query.limit(per_page).offset(offset)
    data, errors = schema.dump(paginated_query, many=True)
    if errors:
        return errors, 409
    return {
        'data': data,
        'pages': totalPages,
        'total': total,
    }
