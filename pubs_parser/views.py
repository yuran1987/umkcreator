from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from docxtpl import DocxTemplate
from .elibrary_parser import Elibrary
from .scopus_parser import Elsevier
from .models import Publications
from core import generator_core
from django.utils import timezone
import pytils.translit, re, tempfile, os
########################################################################################################################
def run_import_pubs(request, type):
    if type=='elibrary':
        elibdata = request.user.elibrary_id.split(";")
        author_id = elibdata[0]
        if not author_id:
            raise ValueError('No author_id is specified')
        else:
            a = Elibrary(authorid=author_id, login=elibdata[1], password=elibdata[2], geckodriver_path=settings.GECKODRIVER_PATH, use_proxy=True)
            a.parse_article_links()#get articles IDs from all pages
            a.parse_article_id()#view article and get info
            a.add_pubs_in_database(creator=request.user)#import publications from elibrary
    elif type=='scopus':
        if not request.user.scopus_id:
            raise ValueError('No author_id is specified')
        else:
            a = Elsevier(author_id=request.user.scopus_id, api_key=settings.SCOPUS_API_KEY)
            a.add_pubs_in_database(creator=request.user)#import publications over Scopus API


    return HttpResponseRedirect(reverse('profile', kwargs={'slug': request.user}))

def get_pubs_count(request):
    data = []
    tmpRINC = {}
    tmpScopusWoS = {}
    tmpPatent={}

    for item in Publications.objects.all():
        if re.search(pytils.translit.translify(request.user.last_name), pytils.translit.translify(item.authors)):
            edition_info = eval(item.edition_info)
            if edition_info['type'] == 'патент на изобретение':
                if item.year not in tmpPatent:
                    tmpPatent[item.year] = 1
                else:
                    tmpPatent[item.year] += 1
            elif item.isScopusWoS:
                if item.year not in tmpScopusWoS:
                    tmpScopusWoS[item.year] = 1
                else:
                    tmpScopusWoS[item.year] += 1
            else:
                if item.year not in tmpRINC:
                    tmpRINC[item.year] = 1
                else:
                    tmpRINC[item.year] += 1

    tmp = list(tmpPatent.keys())

    for key in tmpScopusWoS.keys():
        if key not in tmp:
            tmp.append(key)
    for key in tmpRINC.keys():
        if key not in tmp:
            tmp.append(key)
    tmp.sort()

    for key in tmp:
        data.append({'year': key, 'patents': tmpPatent[key] if key in tmpPatent.keys() else 0,
                     'scopus': tmpScopusWoS[key] if key in tmpScopusWoS.keys() else 0,
                     'rinc': tmpRINC[key] if key in tmpRINC.keys() else 0})

    response = JsonResponse(data,safe=False,charset='utf-8')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def get_pubs_by_docx(request, type):
    if type == '5year':
        year_search = timezone.now().year - 5
        promejutok = 'за последние 5 лет'
    elif type == 'allyear':
        year_search = 1920
        promejutok = 'за все время'

    article_scopus = []
    article_vak = []
    article_rinc = []
    patents = []
    monograf = []
    ucheb_posobie = []

    def get_vol_in_pages(edition_info, authors):
        if re.search('статья в журнале - научная статья', edition_info['type']) or \
           re.search('Article',edition_info['type']) or \
           re.search('тезисы доклада на конференции', edition_info['type']) or\
           re.search('статья в сборнике трудов конференции', edition_info['type']):
                pgs = str(edition_info['pages']).split("-")
                if len(pgs)>1:
                    raznost_pgs = int(pgs[1]) - int(pgs[0])
                    authors_cnt = len(authors.split(','))
                    res = "{0}/{1:.2f}".format(raznost_pgs,raznost_pgs/authors_cnt)
                else:
                    res = "{0}/{1:.2f}".format(edition_info['pages'], 1 / len(authors.split(',')))
        else:
            pages_cnt = edition_info['pages'] if 'pages' in edition_info.keys() else 1
            res = "{0}/{1:.2f}".format(pages_cnt, int(pages_cnt)/ len(authors.split(',')))
        return res

    for item in Publications.objects.all():
        if re.search(pytils.translit.translify(request.user.last_name), pytils.translit.translify(item.authors)):
            if item.year >= year_search:
                edition_info = eval(item.edition_info)

                #удаление автора из списка соавторов
                co_authors = str(item.authors).split(",")
                for it in co_authors:
                    it.strip()
                    if re.search(request.user.get_fullname(), it) or re.search(pytils.translit.translify(request.user.last_name), it):
                        co_authors.remove(it)
                co_authors = ",".join(co_authors)

                if edition_info['type'] == 'патент на изобретение':
                    patents.append({'id': len(patents) + 1, 'title': "{0} ({1})".format(item.title,edition_info['type']),
                                    'biblio_info': "Номер патента: {0}. {1}г. {2}".format(edition_info['Номер патента'],item.year, edition_info['Страна']),
                                    'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors, 'year': item.year})
                elif edition_info['type'] == 'монография':
                    monograf.append({'id': len(monograf) + 1, 'title': "{0} ({1})".format(item.title,edition_info['type']),
                                     'biblio_info': "{0}. {1}. {2} с. ISBN:{3}".format(edition_info['edition'],item.year, edition_info['pages'], edition_info['isbn']),
                                     'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors, 'year': item.year})
                elif edition_info['type'] == 'учебное пособие':
                    ucheb_posobie.append({'id': len(ucheb_posobie) + 1, 'title': "{0} ({1})".format(item.title,edition_info['type']),
                                          'biblio_info': "{0}. {1}. {2} с. ISBN:{3}".format(edition_info['edition'],item.year, edition_info['pages'], edition_info['isbn']),
                                          'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors, 'year': item.year})
                elif re.search('статья в журнале - научная статья',str(edition_info['type'])) or re.search('Article',str(edition_info['type'])):
                    if item.isScopusWoS:

                        article_scopus.append({'id': len(article_scopus) + 1, 'title': "{0} ({1})".format(item.title,edition_info['type']),
                                               'biblio_info': '// {0}. {1}. {2} №{3}. P.{4}.'.format(str(edition_info['name']).title(), item.year,
                                                                                                    'V.'+edition_info['volume'] if edition_info['volume'] is not None else '',
                                                                                                    edition_info['number'],
                                                                                                    edition_info['pages']),
                                               'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors, 'year': item.year})
                    else:
                        format_rus = "//{0}. {1}. {2} №{3}. С.{4}." if edition_info['lang'] == 'русский' else "//{0}. {1}. {2} №{3}. P.{4}."
                        if 'volume' in edition_info.keys():
                            if edition_info['volume'] is not None and edition_info['volume']:
                                if edition_info['lang'] == 'русский':
                                    vol = 'Т.{0}.'.format(edition_info['volume'])
                                else:
                                    vol = 'V.{0}.'.format(edition_info['volume'])
                            else:
                                vol = ''
                        article_vak.append({'id': len(article_vak) + 1, 'title': "{0} ({1})".format(item.title,edition_info['type']), 'biblio_info': format_rus.format(str(edition_info['name']).title(), item.year,
                                                                                                                                  vol,
                                                                                                                                  edition_info['number'],
                                                                                                                                  edition_info['pages']),
                             'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors, 'year': item.year})
                elif re.search('тезисы доклада на конференции',str(edition_info['type'])) or re.search('статья в сборнике трудов конференции',str(edition_info['type'])):
                    format_rus = "//{0}. {1}. С.{2}." if edition_info['lang'] == 'русский' else "{0}. {1}. P.{2}."
                    article_rinc.append({'id': len(article_rinc) + 1, 'title': "{0} ({1})".format(item.title,edition_info['type']), 'biblio_info': format_rus.format(str(edition_info['name']).title(),
                                                                                                  edition_info['conference'], edition_info['pages']),
                                         'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors, 'year': item.year})
                elif re.search('диссертация',str(edition_info['type'])):
                    article_rinc.append({'id': len(article_rinc) + 1, 'title': "{0} ({1})".format(item.title, edition_info['type']),
                         'biblio_info': "// {0}. {1}. {2}c.".format(str(edition_info['type']).title(),item.year, edition_info['pages']),
                         'vol_in_page': get_vol_in_pages(edition_info, item.authors), 'co_authors': co_authors,
                         'year': item.year})
                else:
                    print('Пропущена публикация: ',edition_info['type'], ' ',item.authors,'  ', item.title, '  ', item.isScopusWoS)

    #расположение публикаций в хронологическом порядке
    article_scopus.sort(key=lambda a: a['year'])
    article_vak.sort(key=lambda a: a['year'])
    article_rinc.sort(key=lambda a: a['year'])
    ucheb_posobie.sort(key=lambda a: a['year'])
    monograf.sort(key=lambda a: a['year'])
    patents.sort(key=lambda a: a['year'])

    def set_ids(arr):
        id = 1
        for item in arr:
            item['id'] = id
            id+=1
        return arr

    article_scopus = set_ids(article_scopus)
    article_vak = set_ids(article_vak)
    article_rinc = set_ids(article_rinc)
    ucheb_posobie = set_ids(ucheb_posobie)
    patents = set_ids(patents)


    #формирование документа
    zaf_kav = generator_core.get_zaf_kaf(request.user.deparmt)
    rp_file_object = tempfile.NamedTemporaryFile(suffix='.docx')  # create temp file
    document = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_pubs.docx'))
    document.render(context={'author': {'full_name': '{0} {1} {2}'.format(request.user.last_name, request.user.first_name, request.user.patronymic),
            'IO_family': request.user.get_fullname()},
        'zav_kaf': {'position': zaf_kav['position'], 'name': zaf_kav['name']},
        'promejutok': promejutok,
        'year': timezone.now().year,
        'tbl_article_scopus': article_scopus,
        'tbl_article_vak': article_vak,
        'tbl_article_other': article_rinc,
        'tbl_monografia': monograf,
        'tbl_ucheb_posobiya_UMO': '',#-----------не сделано
        'tbl_ucheb_posobiya': ucheb_posobie,
        'tbl_ucheb_meth_izdanya': '',#-----------не сделано
        'tbl_patents': patents,
    })
    document.save(rp_file_object.name)

    res = HttpResponse(rp_file_object.file,
                       content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    res['Content-Disposition'] = 'attachment; filename=result.docx'
    res['Content-Length'] = os.path.getsize(rp_file_object.name)
    return res