import json,re, os, jinja2, pypandoc
from tempfile import NamedTemporaryFile
from lxml import etree
from docxtpl import DocxTemplate, Document
from django.conf import settings
from .generator_core import get_competens, get_predsedatel_spn, get_zaf_kaf, required_reconcil, get_table_sections_hours, html_to_docx, remove_htmk_tags
from .tex_caller import TexLiveCaller
#   Создание КОС

def get_text(format_str,list, ending=","):
    if len(list)>1:
        res = format_str.format(list[0]['id'],list[-1]['id'])
    else:
        res = "{0}{1} ".format(list[0]['id'],ending)
    return res


def get_kursovya_table(plan, num_elem_discip, indeks_res, doc_tpl):
    sd = doc_tpl.new_subdoc()
    if plan.kursovya_work_project:
        table = sd.add_table(rows=1, cols=5, style='Table Grid')
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = '№ п/п'
        hdr_cells[1].text = '№№ элемента учебной дисциплины (темы/разделы)'
        hdr_cells[2].text = 'Результаты обучения (индекс результата)'
        hdr_cells[3].text = 'Форма и методы контроля'
        hdr_cells[4].text = 'Макс. балл'

        row_cells = table.add_row().cells
        row_cells[0].text = "1"
        row_cells[1].text = num_elem_discip
        row_cells[2].text = indeks_res
        row_cells[3].text = 'Курсовая работа/проект'
        row_cells[4].text = '100'

    return sd

def get_type_kos(komplekt_name, kos_id, ministerstvo, univer, unit, author,discipline, kos, date):
    sd = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ/kos"), 'komplekts.docx'))
    context = {
        'ministerstvo': ministerstvo,
        'UNIVERCITY': univer,
        'Units': unit,
        'author': {'name': author},
        'Discipline': discipline,
        'contents': html_to_docx(kos[kos_id], sd),
        'date': date['day'],
        'month': date['month'],
        'year': date['year'],
        'komplekt_name': komplekt_name
    }
    sd.render(context)
    tp = NamedTemporaryFile(suffix='.docx',delete=False)  # create temp file
    sd.save(tp.name)
    return tp

def get_other(doc_tpl, umkdata, ministerstvo, univer, unit, author,discipline, date):
    js = json.JSONDecoder()
    if umkdata.kos:
        kos = js.decode(umkdata.kos)
        tempfiles_list = []

        if kos['reshenie_zadach']:
            tempfiles_list.append(get_type_kos('Комплект задач (заданий)', 'reshenie_zadach', ministerstvo, univer, unit, author,discipline, kos, date))
        if kos['zad_konr_rabot']:
            tempfiles_list.append(get_type_kos('Комплект заданий для контрольной работы', 'zad_konr_rabot', ministerstvo, univer, unit, author,discipline, kos, date))
        if kos['themes_referat']:
            tempfiles_list.append(get_type_kos('Темы рефератов', 'themes_referat', ministerstvo, univer, unit, author,discipline, kos, date))
        if kos['voprosy_k_exameny']:
            tempfiles_list.append(get_type_kos('Список вопросов к экзамену', 'voprosy_k_exameny', ministerstvo, univer, unit, author, discipline, kos, date))
        if kos['voprosy_k_zachoty']:
            tempfiles_list.append(get_type_kos('Список вопросов к зачету', 'voprosy_k_zachoty', ministerstvo, univer, unit, author, discipline, kos, date))
        if kos['zad_lab_rab']:
            tempfiles_list.append(get_type_kos('Примерные задания для лабораторной работы', 'zad_lab_rab', ministerstvo, univer, unit, author,discipline, kos, date))
        if kos['zad_prakt_rab']:
            tempfiles_list.append(get_type_kos('Примерные задания для практической работы', 'zad_prakt_rab', ministerstvo, univer, unit, author,discipline, kos, date))

        #обьединение файлов docx
        merged_document = Document()

        for index, file in enumerate(tempfiles_list):
            sub_doc = Document(file.name)

            # Don't add a page break if you've reached the last file.
            if index < len(tempfiles_list) - 1:
                sub_doc.add_page_break()

            sub_doc._part = merged_document._part
            if sub_doc._element.body.sectPr is not None:
                sub_doc._element.body.remove(sub_doc._element.body.sectPr)

            for element in sub_doc.element.body:
                merged_document.element.body.append(element)

            file.delete = True
            file.close()

        tp = NamedTemporaryFile(suffix='.docx')  # create temp file
        merged_document.save(tp.name)

        doc = DocxTemplate(tp.name)
        doc._part = doc_tpl.docx._part
        if doc._element.body.sectPr is not None:
            doc._element.body.remove(doc._element.body.sectPr)
        xml = re.sub(r'</?w:body[^>]*>', '', etree.tostring(doc._element.body,encoding='unicode', pretty_print=False))
        tp.close()

        return xml
    else:
        return ''

def context_KOS(umk, umkdata, plans, doc_tpl):
    #1 Контролируемые компетенции
    tbl_comps = get_competens(plans[0])

    #2 Результаты освоения учебной дисциплины
    tbl_known = []
    tbl_can = []
    tbl_own = []
    id = 1
    for c in tbl_comps:
        tbl_known.append({'id': 'З{0}'.format(id), 'res': c['student_known'], 'indicators': c['indicators_know']})
        tbl_can.append({'id': 'У{0}'.format(id), 'res': c['student_can'], 'indicators': c['indicators_can']})
        tbl_own.append({'id': 'В{0}'.format(id), 'res': c['student_own'], 'indicators': c['indicators_own']})
        id +=1

    #3 Контроль и оценка освоения учебной дисциплины
    tbl_secs = get_table_sections_hours(umkdata)
    res_obuch = get_text('{0}-{1}, ',tbl_known)
    res_obuch += get_text('{0}-{1}, ',tbl_can)
    res_obuch += get_text('{0}-{1}',tbl_own)

    indicators_obuch = ""
    indicators_obuch += get_text('{0}-{1}: ',tbl_known, ":")
    for item in tbl_known:
        indicators_obuch += '{0} '.format(item['indicators'])

    indicators_obuch += get_text('{0}-{1}: ',tbl_can,":")
    for item in tbl_can:
        indicators_obuch += '{0} '.format(item['indicators'])

    indicators_obuch += get_text('{0}-{1}: ',tbl_own,":")
    for item in tbl_own:
        indicators_obuch += '{0} '.format(item['indicators'])

    js = json.JSONDecoder()
    forms_controlya = set()
    for item in js.decode(umkdata.table_rating_ochka):
        if(re.search("тестиров", item[1].lower())):
            forms_controlya.add("Тестирование ")
        elif re.search("лаборат", item[1].lower()):
            forms_controlya.add("Лабораторная работа ")
        elif re.search("практ", item[1].lower()):
            forms_controlya.add("Практическая работа ")
        elif re.search("контрол", item[1].lower()):
            forms_controlya.add("Контрольная работа ")

    forms_controlya = " ".join(forms_controlya)

    tbl_control = []
    step_bal = 100/(len(tbl_secs)-1)

    for id in range(len(tbl_secs)-1):
        item = tbl_secs[id]
        tbl_control.append({'id': item['id'], 'name': item['name'], 'res': res_obuch, 'indicators': indicators_obuch, 'forms': forms_controlya, 'bal':step_bal})

    predsedatel_spn_ksn = get_predsedatel_spn(plans[0].direction.deparmt)

    context = {'ministerstvo': plans[0].ministerstvo.name,
               'UNIVERCITY': plans[0].univer.name,
               'Units': umk.creator.deparmt.units.name,
               'kafedra': umk.creator.deparmt.name,
               'predsedatel_spn': {'fio': predsedatel_spn_ksn['fio'], 'position': predsedatel_spn_ksn['position']},
               'zav_kaf': get_zaf_kaf(umk.creator.deparmt),
               'author': {'name': umk.creator.get_fullname(),
                          'position': umk.creator.get_position_display(),
                          'academic_degree': umk.creator.get_science_stepen_display(),
                          'rank': ", {0}".format(umk.creator.get_science_zvanie_display()) if umk.creator.science_zvanie != 'no' else ""},
               'Discipline': plans[0].get_discipline(),
               'direction': plans[0].get_direction(),
               'Profiles': plans[0].get_profiles(),
               'semestrs': "{0}".format(plans[0].get_semestrs()),
               'form_attestacii': "экзамен - {0} семестр, зачет - {1} семестр".format(plans[0].exam_semestr, plans[0].zachot_semestr) if plans[0].exam_semestr and plans[0].zachot_semestr \
                                                        else 'экзамен - {0} семестр'.format(plans[0].exam_semestr) if plans[0].exam_semestr else "зачет - {0} семестр".format(plans[0].zachot_semestr),
               'date':  "  ",
               'month': "  ",
               'year': plans[0].year,
               'zav_kaf_req': required_reconcil(umk.creator, plans),
               'tbl_comps': tbl_comps,
               'tbl_known': tbl_known,
               'tbl_can': tbl_can,
               'tbl_own': tbl_own,
               'tbl_control': tbl_control,
               'tbl_kursovya_work_project':get_kursovya_table(plans[0], "{0}-{1}".format(1,str(len(tbl_secs)-1)), res_obuch, doc_tpl),
               'tipovii_zadaniya':html_to_docx(js.decode(umkdata.kos)['tekushii_kontrol'], doc_tpl) if umkdata.kos else 'Не заполнено',
               'other_zadaniya': get_other(doc_tpl,umkdata,
                                           plans[0].ministerstvo.name,
                                           plans[0].univer.name,
                                           umk.creator.deparmt.units.name,
                                           umk.creator.get_fullname(),
                                           plans[0].get_discipline(),
                                           date={'day':"  ",'month':"  ",'year':plans[0].year})
               }
    return context



def generation_exam_bilets(umk,umkdata,plans, myzip, directory):
    #Формирование экзаменационных билетов
    sets = str(umk.creator.sets)
    if re.search("bilets",sets): #в настройках включено формирование билетов
        latex_jinja_env = jinja2.Environment(
            block_start_string='\BLOCK{',
            block_end_string='}',
            variable_start_string='\VAR{',
            variable_end_string='}',
            comment_start_string='\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(os.path.join(settings.BASE_DIR, "static/doc_templ/kos"))
        )
        template = latex_jinja_env.get_template('template_bilets.tex')
        zaf_kav = get_zaf_kaf(plans[0].direction.deparmt)

        js = json.JSONDecoder()
        if umkdata.kos:
            kos = js.decode(umkdata.kos)
            data = kos['voprosy_k_exameny']
            if data:
                questions_list = []

                kos_questions = []
                for item in re.split(r"[\d+]|[\r]|[\n]$",remove_htmk_tags(data)):
                    if item:
                        kos_questions.append(item)
                print(kos_questions)

                for i in range(0,len(kos_questions)-1,2):
                    if kos_questions[i]!='\r\n':
                        kos_questions[i] = kos_questions[i].replace('\r\n',"")
                    if kos_questions[i+1]!='\r\n':
                        kos_questions[i+1] = kos_questions[i+1].replace('\r\n', "")
                    if kos_questions[i] and kos_questions[i+1]:
                        questions_list.append({'first': kos_questions[i].lstrip(), 'two':kos_questions[i+1].lstrip()})
                print(questions_list)
                if questions_list:
                    template_vars = {'Ministerstvo': plans[0].ministerstvo.name,
                                     'Univercity': plans[0].univer.name,
                                     'Units': umk.creator.deparmt.units.name,
                                     'kafedra': umk.creator.deparmt.name,
                                     'discipline': plans[0].get_discipline(),
                                     'zaf_kaf': {'fio': zaf_kav['name'], 'academic_degree': zaf_kav['science_stepen'], 'academic_zvanie': zaf_kav['science_zvanie']+',' if zaf_kav['science_zvanie']!='без ученого звания' else ''},
                                     'date': {'day': '\_\_', 'month': '\_\_', 'year': plans[0].year},
                                     'list_q': questions_list
                                     }

                    # create a file and save the latex
                    rp_file_object = NamedTemporaryFile(prefix="{0}-{1}-".format(plans[0].discipline,'экзаменационные билеты'), suffix='.pdf',dir=directory)  # create temp file
                    #pypandoc.convert(template.render(template_vars), 'pdf', format='latex', outputfile=rp_file_object.name, extra_args=['--latex-engine=pdflatex'])
                    t = TexLiveCaller(fnameout=rp_file_object.name)
                    myzip.write(t.latex2pdf(template.render(template_vars)))
                    #myzip.write(rp_file_object.name)
                    rp_file_object.close()