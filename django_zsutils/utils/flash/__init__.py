"""
A simple flash implementation based on miracle2k's snippet 
available on <http://www.djangosnippets.org/snippets/331/>.

The additions are:

    * Some simple helper methods to add flash-messages for
      predefined levels

    * Internally every level actually stores a list of messages
      instead of just one single message.
"""

class Middleware(object):
    """
    Simple middleware that registers the flash property to the current
    request in order to make working with it in views more convenient.
    """

    def process_request(self, request):
        request.flash = Flash()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'flash') and len(request.flash) > 0:
            request.session['_flash'] = request.flash
        return response

class Flash(dict):

    def add_success(self, msg):
        self.add('notice', msg)

    def add_warning(self, msg):
        self.add('warning', msg)

    def add_failure(self, msg):
        self.add('failure', msg)
    
    def add(self, type, msg):
        self.setdefault(type, []).append(msg)

    def __iter__(self):
        for k in self.keys():
            val = self[k]
            for v in val:
                yield {'type': k ,'msg': v}

def context_processor(request):
    flash = None
    if '_flash' in request.session:
        flash = request.session['_flash']
        del request.session['_flash']
    return {'flash': flash}
