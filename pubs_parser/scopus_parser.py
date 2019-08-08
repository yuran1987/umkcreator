import requests, json
from datetime import datetime
from django.utils import timezone
from .models import Publications

class Elsevier(object):

    ___base_uri = "https://api.elsevier.com/content/search/scopus"
    ___api_key = '000000xdfdfdfg'
    ___article_count = 0
    articles = []

    def __init__(self, author_id, api_key, uri = ''):
        """Initializes an author given a Scopus author URI or author ID"""
        if uri:
            self.___base_uri = uri
        if not uri and not author_id:
            raise ValueError('No URI or author ID specified')
        if api_key:
            self.___api_key = api_key

        self.author_id = author_id
        resp = requests.get(url="{0}?query=AU-ID({1})&field=dc:identifier".format(self.___base_uri, author_id),
                            headers={'Accept': 'application/json',
                                     'X-ELS-APIKey': self.___api_key})
        data = resp.json()
        self.___article_count = data['search-results']['opensearch:totalResults']
        print("Получено публикаций в результате поиска: {0}".format(self.___article_count))

        for item in data['search-results']['entry']:
            d = {'url': item['prism:url'], 'scopus_id': item['dc:identifier']}
            self.articles.append(d)

    def get_article_info(self, article_url):
        url = (article_url
               + "?field=authors,title,publicationName,volume,issueIdentifier,"
               + "prism:pageRange,coverDate,article-number,prism:doi,citedby-count,prism:aggregationType,subtypeDescription")
        resp = requests.get(url, headers={'Accept': 'application/json', 'X-ELS-APIKey': self.___api_key})
        if resp.text:
            results = json.loads(resp.text.encode('utf-8'))
            coredata = results['abstracts-retrieval-response']['coredata']
            edition_info = {}
            # return {'authors':', '.join([au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']]),
            #           'title': coredata['dc:title'],
            #           'pubname': coredata['prism:publicationName'],
            #           'volume': coredata['prism:volume'],
            #           'pages': coredata.get('prism:pageRange'),
            #           'number': coredata.get('article-number'),
            #           'year': datetime.strptime(coredata['prism:coverDate'], "%Y-%m-%d").year,
            #           'doi': coredata['prism:doi'] if 'prism:doi' in coredata.keys() else None,
            #           'cites': int(coredata['citedby-count'])
            #         }
            edition_info.update({'name': coredata['prism:publicationName']})
            edition_info.update({'volume': coredata.get('prism:volume')})
            edition_info.update({'number': coredata.get('prism:issueIdentifier')})
            edition_info.update({'pages': coredata.get('prism:pageRange')})
            edition_info.update({'type': coredata.get('subtypeDescription')})

            return {'doi': coredata['prism:doi'] if 'prism:doi' in coredata.keys() else None,
                    'authors': ', '.join([au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']]),
                    'title': coredata['dc:title'],
                    'year': datetime.strptime(coredata['prism:coverDate'], "%Y-%m-%d").year,
                    'edition_info': edition_info,
                    'cites': coredata['citedby-count']}
        else:
            raise ValueError("Request return empty result")

    def print_article_list(self):
        res = []
        for item in self.articles:
            res.append(self.get_article_info(article_url=item['url']))
        print("Распознано публикаций: {0}".format(len(res)))
        return res

    def add_pubs_in_database(self, creator):
        count = 0
        count_upd = 0
        for item in self.articles:
            res = self.get_article_info(article_url=item['url'])
            pubs = Publications.objects.filter(title=res['title'])
            if pubs.exists() is False:
                p = Publications(creator=creator, authors = res['authors'], title=res['title'].capitalize(),
                                   year=res['year'] if res['year']>1920 else timezone.now().year,
                                   edition_info = res['edition_info'],
                                   doi = res['doi'], cites = res['cites'], isScopusWoS = True)
                p.save()
                count+=1
            else:
                for p in pubs:
                    p.isScopusWoS=True
                    p.doi = res['doi']
                    p.cites = res['cites']
                    p.save()
                    count_upd += 1
        print("Распознано публикаций: ",count,'  Обновлено публикаций: ', count_upd)
#**************************************************************************
#
#
#                               EXAMPLE
#
#
#**************************************************************************
#import configparser
#config = configparser.RawConfigParser()
#config.read("config.conf")
#api_key = config.get("scopus", "api_key")
#a = Elsevier(author_id = '55409988300', api_key=api_key)
#res = a.print_article_list()
#for item in res:
#    print(item)

#**************************************************************************