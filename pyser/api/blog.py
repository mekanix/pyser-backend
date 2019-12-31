from datetime import datetime

from freenit.api.methodviews import MethodView
from freenit.schemas.paging import PageInSchema, paginate
from flask_jwt_extended import get_jwt_identity, jwt_optional, jwt_required
from flask_smorest import Blueprint, abort
from freenit.models.user import User

from ..models.blog import Blog
from ..schemas.blog import BlogPageOutSchema, BlogSchema

blueprint = Blueprint('blogs', 'blogs')


@blueprint.route('', endpoint='list')
class BlogListAPI(MethodView):
    @jwt_optional
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(BlogPageOutSchema)
    def get(self, pagination):
        """List blog posts"""
        user_id = get_jwt_identity()
        if user_id is None:
            query = Blog.select().where(Blog.published)
        else:
            query = Blog.select()
        return paginate(query, pagination)

    @jwt_required
    @blueprint.arguments(BlogSchema)
    @blueprint.response(BlogSchema)
    def post(self, args):
        """Create blog post"""
        blog = Blog(**args)
        blog.date = datetime.utcnow()
        user_id = get_jwt_identity()
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            Blog.find(
                blog.date.year,
                blog.date.month,
                blog.date.day,
                blog.slug,
            )
            abort(409, message='Post with the same title already exists')
        except Blog.DoesNotExist:
            blog.author = user
            blog.save()
        return blog


@blueprint.route('/<year>/<month>/<day>/<slug>', endpoint='detail')
class BlogAPI(MethodView):
    @blueprint.response(BlogSchema)
    def get(self, year, month, day, slug):
        """Get blog post details"""
        try:
            blog = Blog.find(year, month, day, slug)
        except Blog.DoesNotExist:
            abort(404, message='No such blog')
        except ValueError:
            abort(409, message='Multiple blogs found')
        return blog

    @jwt_required
    @blueprint.arguments(BlogSchema(partial=True))
    @blueprint.response(BlogSchema)
    def patch(self, args, year, month, day, slug):
        """Edit blog post details"""
        try:
            blog = Blog.find(year, month, day, slug)
        except Blog.DoesNotExist:
            abort(404, message='No such blog')
        except ValueError:
            abort(409, message='Multiple blogs found')
        for field in args:
            setattr(blog, field, args[field])
        blog.save()
        return blog

    @jwt_required
    @blueprint.response(BlogSchema)
    def delete(self, year, month, day, slug):
        """Delete blog post"""
        try:
            blog = Blog.find(year, month, day, slug)
        except Blog.DoesNotExist:
            abort(404, message='No such blog')
        except ValueError:
            abort(409, message='Multiple blogs found')
        blog.delete_instance()
        return blog
