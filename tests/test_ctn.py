"""
Test module for oopviews.ctn related stuff
"""

from django.http import HttpResponse

import sys
from django_zsutils.utils.oopviews import ctn
from . import utils

class DummyView(ctn.AbstractCTNView):
    ctn_accept_binding = {
        'text/plain': (0.9, 'text_plain'),
        'text/html': 'text_html',
        'text/*': 'text_default',
        '*/*': 'default',
    }

    def default(self, request, *args, **kwargs):
        return HttpResponse('default')
    def text_plain(self, request, *args, **kwargs):
        return HttpResponse('text_plain')
    def text_html(self, request, *args, **kwargs):
        return HttpResponse('text_html')
    def text_default(self, request, *args, **kwargs):
        return HttpResponse('text_default')

def testAcceptOrdering():
    request = utils.RequestFactory().get('/', 
        HTTP_ACCEPT='text/plain, text/html;q=0.5, text/*')
    vo = DummyView(request)
    priorities = vo._ctn_build_request_priorities(request)
    assert priorities == [('text/plain', 1), ('text/html', 0.5), ('text/*', 1)]

def testInvalidPriority():
    request = utils.RequestFactory().get('/', 
        HTTP_ACCEPT='text/plain, text/html;q=2, text/*')
    vo = DummyView(request)
    priorities = vo._ctn_build_request_priorities(request)
    assert priorities == [('text/plain', 1), ('text/*', 1)]

def testFallback():
    request = utils.RequestFactory().get('/')
    vo = DummyView(request)
    priorities = vo._ctn_build_request_priorities(request)
    assert priorities == [('*/*', 1),]

def testFallbackInvalid():
    request = utils.RequestFactory().get('/', 
            HTTP_ACCEPT = 'text/plain;q=2')
    vo = DummyView(request)
    priorities = vo._ctn_build_request_priorities(request)
    assert priorities == [('*/*', 1),]

def testHandlerPriorities():
    request = utils.RequestFactory().get('/')
    vo = DummyView(request)
    priorities = vo._ctn_build_provides_priorities()
    assert [x[0] for x in priorities] == ['text/html', 'text/plain', 'text/*', '*/*']

def testHandlerLookupFamilyPresent():
    request = utils.RequestFactory().get('/',
            HTTP_ACCEPT='text/somethingelse, */*')
    vo = DummyView(request)
    assert vo(request).content == 'text_default'

def testHandlerLookupDefault():
    request = utils.RequestFactory().get('/')
    vo = DummyView(request)
    assert vo(request).content == 'default'
