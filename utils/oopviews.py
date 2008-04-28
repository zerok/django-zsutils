__all__ = ('create_view', 'BaseView', )

def create_view(klass):
    def _func(request, *args, **kwargs):
        o = klass(request, *args, **kwargs)
        r = o(request, *args, **kwargs)
        after = getattr(o, '__after__', None)
        if after is None:
            return r
        else:
            return o.__after__(r)
    return _func

class BaseView(object):
    def __init__(self, request, *args, **kwargs):
        """
        In the constructor you can easily aggregate common functinality.
        """
        pass
        
    def __call__(self, request, *args, **kwargs):
        raise RuntimeError, "You have to override BaseView's __call__ method"
        
    def __after__(self, response):
        """
        If you want to share some response processing between multiple views
        without using a middleware and filter the affected views there, 
        this method is for you.
        """
        return response