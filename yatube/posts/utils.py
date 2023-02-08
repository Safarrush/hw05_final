from django.core.paginator import Paginator

POST_PAGES = 10


def get_page_context(posts, request):
    paginator = Paginator(posts, POST_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }
