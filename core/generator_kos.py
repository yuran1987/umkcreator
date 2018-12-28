from django.utils.timezone import datetime
import json,re, os
from tempfile import NamedTemporaryFile
from lxml import etree
from docxtpl import DocxTemplate, Document
from django.conf import settings
from .generator_core import get_competens, get_predsedatel_spn, get_zaf_kaf, required_reconcil, get_table_sections_hours, html_to_docx
from .models import Plans
#   Создание КОС

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
        'date': date.day,
        'month': date.month,
        'year': date.year,
        'komplekt_name': komplekt_name
    }
    sd.render(context)
    tp = NamedTemporaryFile(suffix='.docx',delete=False)  # create temp file
    sd.save(tp.name)
    return tp

def get_other(doc_tpl, umkdata, ministerstvo, univer, unit, author,discipline):
    js = json.JSONDecoder()
    kos = js.decode(umkdata.kos)
    date = datetime.now()
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

def context_KOS(umk, umkdata, plans, doc_tpl):
    plan = Plans.objects.get(id=umkdata.umk_id.plan_ochka)

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
    res_obuch = '{0}-{1}, {2}-{3}, {4}-{5}'.format(tbl_known[0]['id'],tbl_known[-1]['id'], tbl_can[0]['id'], tbl_can[-1]['id'], tbl_own[0]['id'], tbl_own[-1]['id'])

    indicators_obuch = ""
    indicators_obuch +='{0}-{1}: '.format(tbl_known[0]['id'],tbl_known[-1]['id'])
    for item in tbl_known:
        indicators_obuch += '{0};'.format(item['indicators'])

    indicators_obuch += '{0}-{1}: '.format(tbl_can[0]['id'], tbl_can[-1]['id'])
    for item in tbl_can:
        indicators_obuch += '{0}'.format(item['indicators'])

    indicators_obuch += '{0}-{1}: '.format(tbl_own[0]['id'], tbl_own[-1]['id'])
    for item in tbl_own:
        indicators_obuch += '{0}'.format(item['indicators'])

    js = json.JSONDecoder()
    forms_controlya = set()
    for item in js.decode(umkdata.table_rating_ochka):
        print(item[1])
        if(re.search("тестиров", item[1].lstrip())):
            forms_controlya.add("Тестирование ")
        elif re.search("лаборат", item[1].lstrip()):
            forms_controlya.add("Лабораторная работа ")
        elif re.search("практ", item[1].lstrip()):
            forms_controlya.add("Практическая работа ")
        elif re.search("контрол", item[1].lstrip()):
            forms_controlya.add("Контрольная работа ")

    forms_controlya = " ".join(forms_controlya)

    tbl_control = []
    step_bal = 100/(len(tbl_secs)-1)

    for id in range(len(tbl_secs)-1):
        item = tbl_secs[id]
        tbl_control.append({'id': item['id'], 'name': item['name'], 'res': res_obuch, 'indicators': indicators_obuch, 'forms': forms_controlya, 'bal':step_bal})

    context = {'ministerstvo': umk.creator.deparmt.units.univer.ministerstvo,
               'UNIVERCITY': umk.creator.deparmt.units.univer.name,
               'Units': umk.creator.deparmt.units.name,
               'kafedra': umk.creator.deparmt.name,
               'predsedatel_spn': get_predsedatel_spn(plans[0].direction.deparmt),
               'zav_kaf': get_zaf_kaf(umk.creator.deparmt),
               'author': {'name': umk.creator.get_fullname(),
                          'position': umk.creator.get_position_display(),
                          'academic_degree': umk.creator.get_science_stepen_display(),
                          'rank': ", {0}".format(umk.creator.get_science_zvanie_display()) if umk.creator.science_zvanie != 'no' else ""},
               'Discipline': plans[0].get_discipline(),
               'direction': plans[0].get_direction(),
               'Profiles': plans[0].get_profiles(),
               'semestrs': "{0}".format(plans[0].get_semestrs()), #plans[1].get_semestrs(),plans[2].get_semestrs()),
               'form_attestacii': "экзамен - {0} семестр, зачет - {1} семестр".format(plan.exam_semestr, plan.zachot_semestr) if plan.exam_semestr and plan.zachot_semestr \
                                                        else 'экзамен - {0} семестр'.format(plan.exam_semestr) if plan.exam_semestr else "зачет - {0} семестр".format(plan.zachot_semestr),
               'date': datetime.now().day,
               'month': datetime.now().month,
               'year': datetime.now().year,
               'zav_kaf_req': required_reconcil(umk.creator, plans),
               'tbl_comps': tbl_comps,
               'tbl_known': tbl_known,
               'tbl_can': tbl_can,
               'tbl_own': tbl_own,
               'tbl_control': tbl_control,
               'tbl_kursovya_work_project':get_kursovya_table(plan, "{0}-{1}".format(1,str(len(tbl_secs)-1)), res_obuch, doc_tpl),
               'tipovii_zadaniya':html_to_docx(js.decode(umkdata.kos)['tekushii_kontrol'], doc_tpl),
               'other_zadaniya': get_other(doc_tpl,umkdata,umk.creator.deparmt.units.univer.ministerstvo,umk.creator.deparmt.units.univer.name,umk.creator.deparmt.units.name, umk.creator.get_fullname(), plans[0].get_discipline())
               }
    return context