from freenit.api import register_endpoints


def create_api(app):
    from .blog import blueprint as blog
    from .cfp import blueprint as cfp
    from .cfs import blueprint as cfs
    from .email import blueprint as email
    from .event import blueprint as event
    from .gallery import blueprint as gallery
    from .hall import blueprint as hall
    from .landing import blueprint as landing
    from .talk import blueprint as talk
    from .ticket import blueprint as ticket

    register_endpoints(
        app,
        '/api/v0',
        [
            blog,
            cfp,
            cfs,
            email,
            event,
            gallery,
            hall,
            landing,
            talk,
            ticket,
        ],
    )

    from ..cli import register
    register(app)
