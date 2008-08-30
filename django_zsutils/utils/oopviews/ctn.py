"""
Example: Content type negotiation with OOPViews
===============================================

In some situations it comes in handy, to do some content type negotiation
to really provide an optimized view for the user depending on what a user's
application supports (say WML or HTML or XML over HTML). HTTP/1.1 handles
this using the "Accept"-request header to give the user the option, to say
what kind of content type she'd prefer or give a list of content types 
prioritized with a value between 0 and 1.

This abstract view class should demonstrate, how you can easily handle such
situations within Django purely in the view code. The idea is pretty simple:
Simply use the ``__call__`` method as dispatcher for content-type-specific
methods.

To use this code, simply inherit the basic implementation and then specify
your content-type-specific methods and register them in the 
``ctn_accept_binding``-dictionary::
    
    from django.http import HttpResponse
    from django_zsutils.utils.oopview import ctn

    class TestView(ctn.AbstractCTNView):
        ctn_accept_binding = {
            'text/html': 'html',
            'text/*': 'html',
            '*/*': 'html',
        }

        def html(self, request, *args, **kwargs):
            return HttpResponse("Hello", mimetype='text/html')

The ``ctn_accept_binding``-dictionary not only allows you to bind a method to a 
content-type, but if you set a value to a tuple instead of just a string, it
will take the first element of that tuple as a priority value similar to the
one used in the "Accept"-handling. This way, you can prioritize methods for 
the case, that the user requests any type of a given family like for instance
'text/*'.
"""

from django.http import HttpResponse

from . import BaseView


def provides_priority_sorting(a,b):
    """
    Sorting function for ``ctn_accept_binding``
    """
    if a[0].startswith('*/'): return -1
    if b[0].startswith('*/'): return 1
    if a[0].endswith('/*'): return -1
    if b[0].endswith('/*'): return 1
    a_prio = a[1][0]
    b_prio = b[1][0]
    if a_prio > b_prio: return 1
    if a_prio < b_prio: return -1
    return 0

def accept_priority_sorting(a,b):
    """
    Simple priority sorter that gives first of all generic handlers the 
    lowest priority and gives more specific handlers by default a higher
    priority. Otherwise, the q-parameter specified in the HTTP/1.1 specs
    is used.
    """
    a_prio = a[1]
    b_prio = b[1]
    a_family = a[0].split("/")[0]
    b_family = b[0].split("/")[0]
    if a[0] == "*/*": return -1
    if b[0] == "*/*": return 1
    if a_family == b_family:
        # More specific has precendence, no matter what
        if a[0].endswith('/*'):
            return -1
        if b[0].endswith('/*'):
            return 1
    if a_prio > b_prio:
        return 1
    if a_prio < b_prio:
        return -1
    return 0

class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406

class AbstractCTNView(BaseView):
    ctn_accept_binding = {'*/*': 'default'}
    
    def __init__(self, request, *args, **kwargs):
        if (self.__class__ is AbstractCTNView):
            raise TypeError, "AbstractContentSelectView is an abstract class"
        self._ctn_request_priorities = None
        self._ctn_provides_priorities = None
        super(AbstractCTNView, self).__init__(request, *args, **kwargs)
    
    def _ctn_build_provides_priorities(self):
        
        if self._ctn_provides_priorities is not None:
            return self._ctn_provides_priorities
        providing = []
        for x in self.ctn_accept_binding.items():
            if isinstance(x[1], list) or isinstance(x[1], tuple):
                providing.append(x)
            else:
                providing.append((x[0], (1, x[1])))
        providing.sort(provides_priority_sorting)
        providing.reverse()
        self._ctn_provides_priorities = providing
        return providing


    def _ctn_build_request_priorities(self, request):
        """
        Helper method for building a priority list for all the content-types
        acceptable to the user.
        """
        if self._ctn_request_priorities is not None:
            return self._ctn_request_priorities

        accept = request.META.get('HTTP_ACCEPT', "*/*")
        # Accept is basically a list separated by "," with options coming
        # before the actual type and being separated by a ";" from it.
        # For now, all this handles is the q-parameter which handles the 
        # priority of the type. If not set, this is set to 1
        types = []
        for accepted_type in accept.split(","):
            tinfo = accepted_type.split(";")
            type_ = tinfo[0].lstrip().rstrip()
            if len(tinfo) == 1:
                q = 1
            else:
                parameters = [x.lstrip().rstrip() for x in tinfo[1].split(";")]
                q = 1
                for p in parameters:
                    if p.startswith("q="):
                        q = float(p.split("=")[1])
                        break
                if q < 0 or q > 1:
                    continue
            types.append((type_, q))
        if len(types) > 0:
            types.sort(accept_priority_sorting)
            types.reverse()
        else:
            types.append(('*/*', 1))
        self._ctn_request_priorities = types 
        return types

    def __call__(self, request, *args, **kwargs):
        """
        Main dispatcher for request.
        """
        self._ctn_build_request_priorities(request)
        self._ctn_build_provides_priorities()
        for (type_, priority) in self._ctn_request_priorities:
            (tfamily, tspec) = type_.split('/')
            # If the requested type is a type-wildcard, we have to go through
            # the local priority list, otherwise a normal lookup is enough.
            if tspec is '*':
                for binding in self._ctn_provides_priorities:
                    if binding[0].startswith(tfamily+'/'):
                        return getattr(self, binding[1][1])(request, *args, **kwargs)
            else:                    
                for t in (type_, '%s/*'%(tfamily,)):
                    if t in self.ctn_accept_binding.keys():
                        if isinstance(self.ctn_accept_binding[t], tuple):
                            name = self.ctn_accept_binding[t][1]
                        else:
                            name = self.ctn_accept_binding[t]
                        return getattr(self, name)(request, *args, **kwargs)
        return HttpResponseNotAcceptable()

