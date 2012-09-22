from django.template import RequestContext
from django.http import HttpResponse

def get_search_query(request):
    if request.method == 'GET':
        path = request.get_full_path()

        if path.startswith('/search/?'):
            search_query = path.replace('/search/?','')
            print search_query

        return {
            'search_query':'123',
        }

