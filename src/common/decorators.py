"""
AJB 12/8/18
Copied from https://github.com/PacktPublishing/Django-2-by-Example
Above repo is released under MIT license, which allows re-use:
cf. https://github.com/PacktPublishing/Django-2-by-Example/blob/master/LICENSE
"""
from django.http import HttpResponseBadRequest


def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap
