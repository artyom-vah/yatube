from django.core.paginator import Paginator
from .models import Post

POSTS_PER_PAGE_10 = 10


def paginator_page(request, posts=Post.objects.
                   select_related('group', 'author')):
    paginator = Paginator(posts, POSTS_PER_PAGE_10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
