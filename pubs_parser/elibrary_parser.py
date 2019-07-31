from selenium import webdriver
from bs4 import BeautifulSoup
import re
from django.utils import timezone
from .models import Publications


class Elibrary(object):

    def __init__(self, authorid, login, password, geckodriver_path):
        # Указываем полный путь к geckodriver.exe на вашем ПК.
        opts = webdriver.FirefoxOptions()
        opts.add_argument('-headless')
        assert opts.headless #no gui
        self.browser = webdriver.Firefox(executable_path=geckodriver_path, options=opts)
        self.elibrary_url = "https://elibrary.ru"
        self.authorid = str(authorid)
        self.articles_links = []
        self.articles = []

        if login and password:
            self.browser.get(self.elibrary_url)
            __login = self.browser.find_element_by_id('login')
            __password = self.browser.find_element_by_id('password')
            __login.send_keys(login)
            __password.send_keys(password)
            __button = self.browser.find_element_by_class_name('butred')
            __button.click()

    def __del__(self):
        self.browser.close()


    def remove_htmk_tags(self, val):
        res = "{0}".format(re.compile(r'<.*?>').sub('', str(val)))
        res = res.replace('\xa0'," ")
        return res.replace('\n', "")


    def get_html(self, url):
        self.browser.get(url)
        html = self.browser.page_source
        return html

    def get_pages_count(self, parser):
        tr_pages = parser.find('tr', {'align': 'center', 'valign': 'middle', 'class': 'menurb'})
        pages = 1
        if tr_pages == 'None':
            list_js = []
            for url in tr_pages.find_all('a'):
                tmp = url.get('href')
                if tmp not in list_js:
                    list_js.append(tmp)
            pages = len(list_js)
        return pages

    def parse_article_links(self):#просмотр всех страниц и получение ссылок
        parser = BeautifulSoup(self.get_html(self.elibrary_url + "/author_items.asp?authorid={0}&pagenum=1".format(self.authorid)),'html.parser')
        pages = self.get_pages_count(parser)
        print("Количество страниц {0}".format(pages))

        def analyse_page(parser,page):
            table = parser.find('table', {'width': '580', 'cellspacing': '0', 'cellpadding': '3'})
            trs = table.find_all('tr', {'valign': 'middle'})
            for tr in trs:
                td = tr.find('td', {'align': 'left', 'valign': 'top'})
                if td is not None:
                    a_url = td.find('a').get('href')
                    if re.search("item.asp", a_url):
                        self.articles_links.append(a_url)
                    span = tr.find('span', {'class': "menug"}) #Версии:
                    if span is not None:
                        url_tmp = str(span.find('a').get('href'))
                        if url_tmp.startswith("/") is False:
                            self.articles_links.append("/" + url_tmp)
                        else:
                            self.articles_links.append(url_tmp)

            print("Распознана страница: {0}".format(page))

        if pages>1:
            analyse_page(parser, 1)
            for page in range(2, pages + 1):
                parser = BeautifulSoup(self.get_html(self.elibrary_url + "/author_items.asp?authorid={0}&pagenum={1}".format(self.authorid, page)), 'html.parser')
                analyse_page(parser, page)
        else:
            analyse_page(parser, 1)

        print("Получено ссылок публикаций: {0}".format(len(self.articles_links)))

    def parse_article_id(self):#Получение списка публикаций по ссылкам
        self.articles = []
        for artcl in self.articles_links:
            edition_info = {}
            doi = None
            annotation = None
            parser = BeautifulSoup(self.get_html(self.elibrary_url + artcl), 'html.parser')
            tables = parser.find_all('table', {'width': '550', 'cellspacing':'0', 'cellpadding':'3', 'border':'0'})

            for tbl in tables:
                tmp = tbl.find('td',{'width': '43%', 'align': 'left'})
                if tmp:#Получаем eLIBRARY_ID
                    eLIBRARY_ID = self.remove_htmk_tags(tmp).replace('eLIBRARY ID: ','')
                tmp = tbl.find('td',{'width':'46%', 'align':'right'})
                if tmp:#получаем DOI
                    tmp = self.remove_htmk_tags(tmp.find('a'))
                    doi = tmp if tmp != 'None' else None
                tmp = tbl.find('td',{'width': '534'})
                if tmp: #Название
                    title = self.remove_htmk_tags(tmp.find('b')).title()
                tmp = tbl.find('td',{'width':'514', 'valign':'middle','align':'center'})
                if tmp:#авторы
                    tmp = tmp.find_all('b')
                    authors = []
                    for auth in tmp:
                        t = self.remove_htmk_tags(auth).title()
                        if re.search("\.",t) is None:
                            family_IO = t.split(" ")#дробим строку на фамилию имя и отчество
                            if len(family_IO)==3:
                                authors.append('{} {:.1}.{:.1}.'.format(*family_IO))
                            else:
                                authors.append('{} {:.1}.'.format(*family_IO))
                        else:
                            authors.append(t)
                tmp = tbl.find('td', {'colspan': '2', 'align': 'left'})
                if tmp:
                    if re.findall('БИБЛИОМЕТРИЧЕСКИЕ ПОКАЗАТЕЛИ:', str(tmp)):
                        biblio_pokazatel = {}
                        tmp = tbl.find('td',{'width':'504', 'align':'left', 'valign':'middle'})
                        for item in str(tmp).split('<img class="imghelp help" src="/images/but_orange_question.gif"/>'):
                            it = self.remove_htmk_tags(item).split(':')
                            if it:
                                if re.search('Входит в РИНЦ', it[0]):
                                    biblio_pokazatel.update({'Входит в РИНЦ': it[1].strip()})
                                elif re.search('Цитирований в РИНЦ', it[0]):
                                    biblio_pokazatel.update({'Цитирований в РИНЦ': it[1].strip()})
                                elif re.search('Входит в ядро РИНЦ', it[0]):
                                    biblio_pokazatel.update({'Входит в ядро РИНЦ': it[1].strip()})
                                elif re.search('Цитирований из ядра РИНЦ', it[0]):
                                    biblio_pokazatel.update({'Цитирований из ядра РИНЦ': it[1].strip()})
                                elif re.search('Входит в Scopus', it[0]):
                                    biblio_pokazatel.update({'Входит в Scopus': it[1].strip()})
                                elif re.search('Цитирований в Scopus', it[0]):
                                    biblio_pokazatel.update({'Цитирований в Scopus': it[1].strip()})
                                elif re.search('Входит в Web of Science', it[0]):
                                    biblio_pokazatel.update({'Входит в Web of Science': it[1].strip()})
                                elif re.search('Цитирований в Web of Science', it[0]):
                                    biblio_pokazatel.update({'Цитирований в Web of Science': it[1].strip()})
                                elif re.search('Норм. цитируемость по журналу', it[0]):
                                    biblio_pokazatel.update({'Норм. цитируемость по журналу': it[1].strip()})
                                elif re.search('Импакт-фактор журнала в РИНЦ', it[0]):
                                    biblio_pokazatel.update({'Импакт-фактор журнала в РИНЦ': it[1].strip()})
                                elif re.search('Норм. цитируемость по направлению', it[0]):
                                    biblio_pokazatel.update({'Норм. цитируемость по направлению': it[1].strip()})
                                elif re.search('Дециль в рейтинге по направлению', it[0]):
                                    biblio_pokazatel.update({'Дециль в рейтинге по направлению': it[1].strip()})
                                elif re.search('Тематическое направление', it[0]):
                                    biblio_pokazatel.update({'Тематическое направление': it[1].strip()})
                                elif re.search('Рубрика ГРНТИ', it[0]):
                                    biblio_pokazatel.update({'Рубрика ГРНТИ': it[1].replace('(изменить)','').strip()})

                    elif re.findall('ЖУРНАЛ:', str(tmp)):#Инфо про журнал
                        tmp = tbl.find('td', {'width': '504', 'align': 'left', 'valign': 'middle'})
                        items = str(tmp).split('<br/>')
                        print(items)
                        eISSN_item=''
                        ISSN_item = ''
                        for it in items:
                            if re.search('eISSN', it):
                                eISSN_item = it
                            elif re.search('ISSN', it):
                                ISSN_item = it

                        if re.search('eISSN',eISSN_item):
                            issn_eissn = eISSN_item.split('<span style="margin-left:20px;"></span>')
                            edition_info.update({'name': self.remove_htmk_tags(items[0])})
                            edition_info.update({'edition': self.remove_htmk_tags(items[1]).replace('Издательство: ','')})
                            edition_info.update({'issn': self.remove_htmk_tags(issn_eissn[0]).replace('ISSN: ',"")})
                            edition_info.update({'eissn': self.remove_htmk_tags(issn_eissn[1]).replace('eISSN: ',"")})
                        else:
                            edition_info.update({'name': self.remove_htmk_tags(items[0])})
                            edition_info.update({'edition': self.remove_htmk_tags(items[1]).replace('Издательство: ','')})
                            edition_info.update({'issn': self.remove_htmk_tags(ISSN_item).replace('ISSN: ',"")})

                    elif re.findall('ИСТОЧНИК:', str(tmp)):#Инфо про источник
                        tmp = tbl.find('td', {'width': '504', 'align': 'left', 'valign': 'middle'})
                        items = str(tmp).split('Издательство:')
                        edition_info.update({'name': self.remove_htmk_tags(items[0].replace('<br/>',' ')).strip()})
                        edition_info.update({'edition': self.remove_htmk_tags(items[1].replace('<br/>',' ')).strip()})
                    elif re.findall('КОНФЕРЕНЦИЯ:', str(tmp)):  # Инфо про конференеция
                        tmp = tbl.find('td', {'width': '504', 'align': 'left', 'valign': 'middle'})
                        edition_info.update({'conference': self.remove_htmk_tags(str(tmp).replace('<br/>',' '))})
                    elif re.findall('АННОТАЦИЯ:', str(tmp)): #Аннотация
                        annotation = self.remove_htmk_tags(tbl.find('div', {'id': "abstract1"}))

            #находим Том страницы номер выпуска
            tables = parser.find('table', {'width': '580', 'cellspacing': '0', 'cellpadding': '2', 'border': '0'})
            tmp = tables.find_all('td',{'width':'574', 'align':'center', 'valign':'middle'})
            year = 0
            if tmp:
                for item in tmp:
                    for d in str(item).split('<span style="margin-left:20px;">'):
                        if re.findall('Тип:', d):
                            edition_info.update({'type': self.remove_htmk_tags(d).replace('Тип: ','')})
                        elif re.findall('Язык:', d):
                            edition_info.update({'lang': self.remove_htmk_tags(d).replace('Язык: ', '')})
                        elif re.findall('ISBN:', d):
                            edition_info.update({'isbn': self.remove_htmk_tags(d).replace('ISBN: ', '')})
                        elif re.search(r'Год\sиздания:|Год:', d):
                            year = int(self.remove_htmk_tags(d).replace('Год издания: ', '').replace('Год:', ''))
                        elif re.findall('Место издания:', d):
                            edition_info.update({'place': self.remove_htmk_tags(d).replace('Место издания: ', '')})
                        elif re.search(r'Число\sстраниц:|Страницы:', d):
                            edition_info.update({'pages': self.remove_htmk_tags(d).replace('Число страниц: ', '').replace('Страницы:', '').strip()})
                        elif re.findall('Издательство:', d):
                            edition_info.update({'edition': self.remove_htmk_tags(d).replace('Издательство: ', '')})
                        elif re.findall('УДК:', d):
                            edition_info.update({'udk': self.remove_htmk_tags(d).replace('УДК: ', '').strip()})
                        elif re.findall('Номер:', d): #номер журнала
                            edition_info.update({'number': self.remove_htmk_tags(d).replace('Номер: ', '')})
                        elif re.findall('Том:', d): #том журнала
                            edition_info.update({'volume': self.remove_htmk_tags(d).replace('Том: ', '')})

            self.articles.append({'elibrary_id': eLIBRARY_ID, 'doi': doi, 'authors': ", ".join(authors), 'title': title.capitalize(), 'year': year, 'annotation': annotation, 'edition_info': edition_info, 'biblio_indicators': biblio_pokazatel})

    def get_articles(self):#Получение списка публикаций
        return self.articles


    def add_pubs_in_database(self, creator):
        count = 0
        for item in self.articles:
            c = Publications.objects.filter(title=item['title']).exists()
            if not c:
                pub = Publications(creator=creator, authors = item['authors'], title=item['title'],
                                   year=item['year'] if item['year']>1920 else timezone.now().year, edition_info = item['edition_info'],
                                   doi = item['doi'], biblio_pokazatel = item['biblio_indicators'],
                                   annotation = item['annotation'], elib_id = item['elibrary_id'])
                pub.save()
                count+=1
        print("Распознано публикаций: ",count)


    #-------------------------------------------------------------------------------------------------------------------
    def parse_article_list(self):#Получение списка публикаций со страницы МОИ ПУБЛИКАЦИИ
        self.articles = []
        def article_from_td(td):
            title = td.find('b')
            authors = td.find('i')
            edition = str(td).replace(str(title), " ").replace(str(authors), " ").replace("\xa0", "").replace("\n", "")
            return {'authors': self.remove_htmk_tags(authors), 'title': self.remove_htmk_tags(title).title(),
                    'edition': self.remove_htmk_tags(edition).strip()}

        soup = BeautifulSoup(self.get_html(self.elibrary_url + '/author_items_print.asp?authorid={0}'.format(self.authorid)), 'html.parser')
        tables = soup.body.find_all('table', {'cellpadding': '3'})
        for i in range(0, len(tables)):
            trs = tables[i].find_all('tr', {'valign': 'middle'})  # .get('href')
            for tr in trs:
                td = tr.find('td', {'align': 'left', 'valign': 'top'})
                span = td.find('span', {'class': "menug"})
                tbl = td.find('table', {'border': '0', 'cellspacing': '0', 'cellpadding': '0'})
                if span:
                    tmp = str(td).replace(str(tbl), "").replace(str(td.find('div')), "")
                    self.articles.append(article_from_td(BeautifulSoup(tmp, 'html.parser')))
                    self.articles.append(article_from_td(span))
                else:
                    self.articles.append(article_from_td(td))

        print("Получено публикаций: {0}".format(len(self.articles)))


#**************************************************************************
#
#
#                               EXAMPLE
#
#
#**************************************************************************
#config = configparser.RawConfigParser()
#config.read("config.conf")
#elogin = config.get("elibrary", "login")
#epass = config.get("elibrary", "password")
#geckodrv_path = config.get("elibrary", "geckodriver_path")
#a = Elibrary(authorid=660373, login = elogin, password=epass, geckodriver_path=geckodrv_path)
#a.parse_article_links()
#a.parse_article_id()

#a.parse_article_list()
#res = a.get_articles()

#for item in res:
#    print(item)
#**************************************************************************






