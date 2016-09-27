from django.http import HttpResponseRedirect

def sphinx_doc_view(request):
    return HttpResponseRedirect('static/doc/index.html')