from django.template import Library
from django.conf import settings

register = Library()

@register.inclusion_tag('pagination.html', takes_context=True)
def pagination(context):
    ctx_var = getattr(settings, 'CONTEXT_PAGINATION_VARIABLE', 'page')
    page = context.get(ctx_var, None)
    if page is None:
        return {'has_pagination':False}
    previous_pages = range(1, page.number)[-5:]
    next_pages = range(page.number+1, page.paginator.num_pages+1)[:5]
    last_page = page.paginator.num_pages
    return {
        'page': page,
        'previous_pages': previous_pages,
        'next_pages': next_pages,
        'has_pagination': True, 
        'show_first': page.number != 1 and page.number not in previous_pages,
        'show_last': page.number != last_page and page.number not in next_pages,
        'last_page': last_page,
    }