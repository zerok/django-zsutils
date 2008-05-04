"""
The pagination tag is a very simple way to add page-navigation to your 
view/template. When you fetch content from a model and want to have it
paginated, simply add something like this to your view::
    
    page_nr = request.REQUEST.get('p', 1)
    paginator = Paginator(NewsItem.objects.select_related().all(), 5)
    page = paginator.page(page_nr)
    
and add the page to your context (with the name 'page'). Then add the
paginator tag to your template first by loading this library::
    
    {% load zsutils.pagination %}
    
and then by adding the tag itself::
    
    {% pagination %}
    
That's it. Now you will get a nice simple pagination, which you can easily
customize by overwriting the pagination.html template.

In case the template variable has a different semantic for you, you can
tell the pagination template tag to use a different context variable through
settings.CONTEXT_PAGINATION_VARIABLE.

By default, you will get 10 pages in your pagination (if your resultset has
this many pages). You can configure this value again in your settings.py by
setting PAGINATION_PAGE_LIMIT to whatever number of pages you like (note that
a value below 3 hardly makes any sense, so you will get an error message if
you still try that).
"""

from django.template import Library
from django.conf import settings

register = Library()

@register.inclusion_tag('pagination.html', takes_context=True)
def pagination(context):
    """
    For details on this templatetag see the pydoc for this module
    """
    ctx_var = getattr(settings, 'CONTEXT_PAGINATION_VARIABLE', 'page')
    page_limit = int(getattr(settings, 'PAGINATION_PAGE_LIMIT', 10))
    
    assert page_limit >= 2, "Set PAGINATION_PAGE_LIMIT to a value bigger than 2"
    
    page = context.get(ctx_var, None)
    if page is None:
        return {'has_pagination':False}
    # Calculate the number of pages on each side of the current page
    lower_half = (page_limit-(page_limit % 2 == 0 and 1 or 0))/2
    previous_pages = range(1, page.number)[-lower_half:]
    upper_half = (page_limit/2)
    if len(previous_pages) < lower_half:
        upper_half += lower_half-len(previous_pages)
    next_pages = range(page.number+1, page.paginator.num_pages+1)[:upper_half]
    if len(next_pages) < upper_half:
        lower_half += upper_half-len(next_pages)
        previous_pages = range(1, page.number)[-lower_half:]
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