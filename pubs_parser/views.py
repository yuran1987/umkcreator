from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from core.models import User
from .elibrary_parser import Elibrary
from .scopus_parser import Elsevier
from .models import Publications

########################################################################################################################
def run_import_pubs(request, type):
    #if request.method == 'POST':
        #form = SelectDisipForm(request.POST)
        # check whether it's valid:
        #if form.is_valid():
        #    return HttpResponseRedirect(reverse('umk_create', kwargs={'id': request.POST['discip_val'],
        #                                                              'direct_id': request.POST['direct_val'],
        #                                                              'tr_program': request.POST['training_program'],
        #                                                              'year': request.POST['year']}))
    #else:
        #form = SelectDisipForm()
    #return render(request, 'forms.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Создание рабочей программы дисциплины"})

    if type=='elibrary':
        author_id = request.user.elibrary_id
        if not author_id:
            raise ValueError('No author_id is specified')
        else:
            a = Elibrary(authorid=author_id, login=settings.ELIBRARY_LOGIN, password=settings.ELIBRARY_PASSWORD, geckodriver_path=settings.GECKODRIVER_PATH)
            a.parse_article_links()#get articles IDs from all pages
            a.parse_article_id()#view article and get info
            a.add_pubs_in_database(creator=request.user)#import publications from elibrary
    elif type=='scopus':
        a = Elsevier(author_id=request.user.scopus_id, api_key=settings.SCOPUS_API_KEY)
        a.add_pubs_in_database(creator=request.user)#import publications over Scopus API


    return render(request, 'index.html', {'title': settings.SITE_NAME})

def get_pubs_count(request):

    data = []
    tmp = {}

    c = 0
    for item in Publications.objects.filter(creator=request.user):
        if item.year not in tmp:
            tmp[item.year] = 1
        else:
            tmp[item.year] += 1

    for key in tmp.keys():
        data.append({'year': key, 'count': tmp[key]})

    response = JsonResponse(data,safe=False,charset='utf-8')
    response['Access-Control-Allow-Origin'] = '*'
    return response
