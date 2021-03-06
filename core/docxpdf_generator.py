import os,re, shutil, transliterate
from io import BytesIO, StringIO
from zipfile import ZipFile
from django.http import HttpResponse
from django.utils.timezone import datetime
from django.conf import settings
from tempfile import NamedTemporaryFile, TemporaryDirectory, gettempdir
from docxtpl import DocxTemplate, RichText
from .models import Plans, UmkArticles, UmkData, Competence, User
from .generator_kos import context_KOS, generation_exam_bilets
from .generator_core import get_predsedatel_spn, get_zaf_kaf, get_zaf_kaf_w_signature_pic, get_user_fio_w_signature, get_course, isEmptyValOrStr, get_hour_kursovaya_work_or_project, required_reconcil, html_to_docx, \
            get_OPOP_of_discipline, get_placeInStructOPOP,get_competens,get_competens_list, get_table_contentsection,get_table_interdisciplinary_relations, get_table_sections_hours, \
            get_table_lections_hours,get_table_labs_prakt, get_table_samost_hours, get_table_literature, get_table_literature_from_json,  get_table_rating_day, get_table_rating_night, isEmptyVal
#-------------------------------------------------------------------------------------------


#####################################################################################################################
#
#
#                       Формирование рабочей программы и аннотации
#
#
######################################################################################################################
def get_kursovya_work_project(plan):
    if plan is not None:
        if plan.kursovya_work_project:
            return plan.kursovya_work_project
    return "-"

def context_workprogram(umk, umkdata, plans, competens, zaf_kav, doc_tpl):
    dateprikaz = plans[0].get_direction_date_prikaz()
    #kursovya_work_project_sem = [re.findall("\d+",plan.kursovya_work_project )[0] for plan in plans if re.findall("\d+",plan.kursovya_work_project if plan is not None else "-")] #номер семестра на курсовой проект
    kursovya_work_project_sem = [re.findall("\d+", get_kursovya_work_project(plan))[0] for plan in plans if re.findall("\d+", get_kursovya_work_project(plan))]  # номер семестра на курсовой проект
    predsedatel_spn_ksn = get_predsedatel_spn(plans[0].direction.deparmt)

    context = {'ministerstvo': plans[0].ministerstvo,#umk.creator.deparmt.units.univer.ministerstvo,
               'UNIVERCITY': plans[0].univer,
               'Units': umk.creator.deparmt.units.name,
               'kafedra': umk.creator.deparmt.name,
               'predsedatel_spn': {'fio': predsedatel_spn_ksn['fio'], 'position': predsedatel_spn_ksn['position']},
               'zav_kaf': get_zaf_kaf_w_signature_pic(zaf_kav,doc_tpl),
               'author': {'name': umk.creator.get_fullname(),
                          'position': umk.creator.get_position_display(),
                          'academic_degree': umk.creator.get_science_stepen_display(),
                          'rank': ", {0}".format(umk.creator.get_science_zvanie_display()) if umk.creator.science_zvanie!='no' else ""},
               'Discipline': plans[0].get_discipline(),
               'direction': plans[0].get_direction(),
               'Profiles': plans[0].get_profiles(),
               'qualification': plans[0].get_qualif_display(),
               'program_traning': "{0} {1}а".format(plans[0].get_training_program_display(),plans[0].get_qualif_display()),
               'cources': "{0}/{1}/{2}".format(get_course(plans[0].get_semestrs()),
                                               get_course(plans[1].get_semestrs()) if plans[1] else "-",
                                               get_course(plans[2].get_semestrs()) if plans[2] else "-"),                                                   #нужно рассчитать изходя из семестров
               'semestrs': "{0}/{1}/{2}".format(plans[0].get_semestrs(),
                                                plans[1].get_semestrs() if plans[1] else "-",
                                                plans[2].get_semestrs() if plans[2] else "-" ),
               'audit_total_hours': "{0}/{1}/{2}".format(plans[0].hours_audit_work_sum,
                                                         plans[1].hours_audit_work_sum if plans[1] else "-" ,
                                                         plans[2].hours_audit_work_sum if plans[2] else "-"),
               'lectures_total_hours': isEmptyValOrStr(plans[0].hours_lectures,
                                                       plans[1].hours_lectures if plans[1] else 0,
                                                       plans[2].hours_lectures if plans[2] else 0),
               'prakt_total_hours': isEmptyValOrStr(plans[0].hours_pract,
                                                    plans[1].hours_pract if plans[1] else 0,
                                                    plans[2].hours_pract if plans[2] else 0),
               'labs_total_hours': isEmptyValOrStr(plans[0].hours_labs,
                                                   plans[1].hours_labs if plans[1] else 0,
                                                   plans[2].hours_labs if plans[2] else 0),
               'samost_total_hours': "{0}/{1}/{2}".format(plans[0].hours_samost_work_sum,
                                                          plans[1].hours_samost_work_sum if plans[1] else 0,
                                                          plans[2].hours_samost_work_sum if plans[2] else 0),
               'kursovya_num_semestr': isEmptyValOrStr(kursovya_work_project_sem[0],kursovya_work_project_sem[1],kursovya_work_project_sem[2]) if kursovya_work_project_sem else "-",
               'kursovya_hours': get_hour_kursovaya_work_or_project(umkdata),
               'raschotno_graph_work_semests': "-",
               'raschotno_graph_work_hours': "-",
               'zanyatiya_in_interaktiv_hours': "{0}".format(plans[0].zanatiya_in_interak_forms_hours),
               'zachot_semestrs': "{0}/{1}/{2}".format(plans[0].zachot_semestr if plans[0].zachot_semestr else isEmptyVal(plans[0].zachot_semestr),
                                                       #plans[1].zachot_semestr if plans[1].zachot_semestr else "-" if plans[1] is not None else "-",
                                                       #plans[2].zachot_semestr if plans[2].zachot_semestr else "-" if plans[2] is not None else "-"),
                                                       "-" if (plans[1] == "-" or plans[1] is None) else plans[1].zachot_semestr if plans[1].zachot_semestr else "-",
                                                       "-" if (plans[2]=="-" or plans[2]   is None) else plans[2].zachot_semestr if plans[2].zachot_semestr else "-"),
               'exam_semestrs': "{0}/{1}/{2}".format(plans[0].exam_semestr if plans[0].exam_semestr else isEmptyVal(plans[0].exam_semestr),
                                                     #plans[1].exam_semestr if plans[1].exam_semestr else "-" if plans[1] is not None else "-",
                                                     #plans[2].exam_semestr if plans[2].exam_semestr else "-" if plans[2] is not None else "-"),
                                                     "-" if plans[1] is None else plans[1].exam_semestr if plans[1].exam_semestr else "-",
                                                     "-" if plans[2] is None else plans[2].exam_semestr if plans[2].exam_semestr else "-"),
               'trudoemkost_all': "{0}".format(plans[0].trudoemkost_all),
               'zachot_edinic': "{0}".format(plans[0].trudoemkost_zachot_edinic),
               'prikaz_number': dateprikaz[0],
               'prikaz_date': dateprikaz[1].strftime("%d.%m.%Y"),
               'year': plans[0].year,
               'zav_kaf_req': required_reconcil(plans),
               # -------------------------------------------------------------------------------------------------------
               'discipline_aims':  html_to_docx(umkdata.aim, doc_tpl),
               'discipline_tasks': html_to_docx(umkdata.tasks, doc_tpl),
               'code_OPOP': get_OPOP_of_discipline(plans),
               'discipline_place': get_placeInStructOPOP(plans, doc_tpl),
               'tbl_comps': competens,
               'tbl_contentsections_and_theme': get_table_contentsection(umkdata),
               'tbl_interdisciplinary_rel': get_table_interdisciplinary_relations(umkdata),
               'tbl_section_hours': get_table_sections_hours(umkdata),
               'tbl_lections_hours': get_table_lections_hours(umkdata),
               'tbl_prakt_hours': get_table_labs_prakt(umkdata.table_prakt_hour, doc_tpl, 'практических'),
               'tbl_labs_hours': get_table_labs_prakt(umkdata.table_laborat_hour, doc_tpl, 'лабораторных'),
               'tbl_samost_hours': get_table_samost_hours(umkdata),
               'tbl_liter': get_table_literature(umkdata),
               'samost_total': "{0}/{1}/{2}".format(plans[0].hours_samost_work_sum,
                                                    plans[1].hours_samost_work_sum if plans[1] is not None else "-",
                                                    plans[2].hours_samost_work_sum if plans[2] is not None else "-"),
               'samost_total_without_prepod': "{0}/{1}/{2}".format(plans[0].hours_samost_wo_lec,
                                                                   plans[1].hours_samost_work_sum if plans[1] is not None else "-",
                                                                   plans[2].hours_samost_work_sum if plans[2] is not None else "-"),
               'samost_total_with_student': "{0}/-/-".format(plans[0].hours_samost_w_lec_w_stud),
               'samost_total_with_group': "{0}/-/-".format(plans[0].hours_samost_w_lec_w_group),
               'theme_kursovii_work': umkdata.theme_kursovih_rabot if len(umkdata.theme_kursovih_rabot)>1 else 'Учебным планом выполнение курсовых работ не предусмотрено.',
               'materialno_texnicheskoe_obespechenie': html_to_docx(umkdata.material_teh_obespech_dicip, doc_tpl),
               'database_info_system': html_to_docx(umkdata.database_info_system, doc_tpl),
               'software_obespechenie': html_to_docx(umkdata.software_lic, doc_tpl) if umkdata.software_lic else '',
               #-------------------------------------------Рейтинг------------------------------------------------------
               'rating_day': get_table_rating_day(doc_tpl,plans[0], umkdata),
               'rating_night':get_table_rating_night(doc_tpl, umkdata) if plans[1] and plans[2] is not None else '',
               #-----------------------------------------ЛИТЕРАТУРА-----------------------------------------------------
               'crs_och': get_course(plans[0].get_semestrs()),
               'crs_z': get_course(plans[1].get_semestrs())  if plans[1] is not None else "-",
               'crs_zu': get_course(plans[2].get_semestrs()) if plans[2] is not None else "-",
               'smr_och': plans[0].get_semestrs(),
               'smr_z': plans[1].get_semestrs() if plans[1] is not None else "-",
               'smr_zu': plans[2].get_semestrs() if plans[2] is not None else "-"
               }
    return context

#    Создание/Генерирование аннотации
def context_annotation(umk, umkdata, plans, competens, zaf_kav, doc_tpl):
    student_known = set()
    student_can = set()
    student_own = set()

    for v in competens:
        student_known.add(v['student_known'])
        student_can.add(v['student_can'])
        student_own.add(v['student_own'])

    context = {'zav_kaf': get_zaf_kaf_w_signature_pic(zaf_kav,doc_tpl),
               'author': {'name': umk.creator.get_fullname(),
                          'position': umk.creator.get_position_display(),
                          'academic_degree': umk.creator.get_science_stepen_display(),
                          'rank': ", {0}".format(umk.creator.get_science_zvanie_display()) if umk.creator.science_zvanie!='no' else ""},
               'discipline': plans[0].get_discipline(),
               'direction': plans[0].get_direction(),
               'audit_total_hours': "{0}/{1}/{2}".format(plans[0].hours_audit_work_sum,
                                                         plans[1].hours_audit_work_sum if plans[1] is not None else "-",
                                                         plans[2].hours_audit_work_sum if plans[2] is not None else "-"),
               'samost_total_hours': "{0}/{1}/{2}".format(plans[0].hours_samost_work_sum,
                                                          plans[1].hours_samost_work_sum if plans[1] is not None else "-",
                                                          plans[2].hours_samost_work_sum if plans[2] is not None else "-"),
               'zachot_semestrs': "{0}/{1}/{2}".format(plans[0].zachot_semestr if plans[0].zachot_semestr else isEmptyVal(plans[0].zachot_semestr),
                                                       "-" if (plans[1] == "-" or plans[1] is None) else plans[1].zachot_semestr if plans[1].zachot_semestr else "-",
                                                       "-" if (plans[2] == "-" or plans[2] is None) else plans[2].zachot_semestr if plans[2].zachot_semestr else "-"),
               'exam_semestrs': "{0}/{1}/{2}".format(plans[0].exam_semestr if plans[0].exam_semestr else isEmptyVal(plans[0].exam_semestr),
                                                     "-" if (plans[1] == "-" or plans[1] is None) else plans[1].exam_semestr if plans[1].exam_semestr else "-",
                                                     "-" if (plans[2] == "-" or plans[2] is None) else plans[2].exam_semestr if plans[2].exam_semestr else "-"),
               'trudoemkost_all': "{0}".format(plans[0].trudoemkost_all),
               'year_nabor': plans[0].year,
               # -------------------------------------------------------------------------------------------------------
               'discipline_aims':  html_to_docx(umkdata.aim, doc_tpl),
               'code_OPOP': get_OPOP_of_discipline(plans),
               'discipline_place': get_placeInStructOPOP(plans, doc_tpl),
               'comps': plans[0].comps,
               'student_known': " ".join(student_known),
               'student_can': " ".join(student_can),
               'student_own': " ".join(student_own)
               }
    return context




def render_in_docx(document,context, umkname, save_tozip,directory):
    document.render(context)
    rp_file_object = NamedTemporaryFile(prefix="{0}-".format(umkname), suffix='.docx', dir=directory)  # create temp file
    document.save(rp_file_object.name)
    save_tozip.write(rp_file_object.name)
    rp_file_object.close()

def generation_docx(id):#формирование только одной рабочей программы и аннотации
    umkdata = UmkData.objects.get(umk_id=id)
    umk = umkdata.umk_id
    plans = umk.get_plan_list()
    umkname = umk.get_short_name()  # имя дисциплины и профиль
    code_OPOP = umk.get_plan_ochka().code_OPOP.replace("/","_")
    competens = get_competens(plans[0])
    zaf_kaf = get_zaf_kaf(umk.creator.deparmt)

    tmpdir = gettempdir()
    dir_path = "{0}/{1}/{2}/{3}".format(tmpdir, plans[0].year,
                                        "{0} {1}".format(plans[0].get_training_program_display(),
                                                         plans[0].get_qualif_display()),
                                            umkname)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    tmpfile = BytesIO()
    with ZipFile(tmpfile, 'w') as myzip:
        ####создание рабочей программы
        doc = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_work_program.docx'))
        render_in_docx(doc, context_workprogram(umk, umkdata, plans, competens, zaf_kaf, doc), "{0}-{1}".format(code_OPOP,umkname), myzip, dir_path)

        # создание аннотации
        ann_doc = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_annotation.docx'))
        render_in_docx(ann_doc, context_annotation(umk, umkdata, plans, competens, zaf_kaf, ann_doc), "{0}-{1}-аннотация".format(code_OPOP,umkname), myzip, dir_path)

        #Создание КОС
        if plans[0].year>=2016:
            kos_doc = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_kos.docx'))
            render_in_docx(kos_doc, context_KOS(umk, umkdata, plans, competens,zaf_kaf, kos_doc), "{0}-{1}-КОС".format(code_OPOP,umkname), myzip, dir_path)
            if plans[0].exam_semestr:
                generation_exam_bilets(umk, umkdata, plans, zaf_kaf, myzip, dir_path)

    shutil.rmtree(dir_path,ignore_errors=True)
    res = HttpResponse(tmpfile.getvalue(), content_type='application/zip')
    res['Content-Disposition'] = 'attachment; filename=result-{0}.zip'.format(datetime.today().strftime("%Y-%m-%d"))
    res['Content-Length'] = tmpfile.tell()
    return res


def generation_docx_achive(id_list):
    tmpfile = BytesIO()
    with ZipFile(tmpfile, 'w') as myzip:
        for id in id_list:
            umkdata = UmkData.objects.get(umk_id=id)
            umk = umkdata.umk_id
            plans = umk.get_plan_list()
            umkname = umk.get_short_name()  # имя дисциплины и профиль
            code_OPOP = plans[0].code_OPOP.replace("/", "_")
            competens = get_competens(plans[0])
            zaf_kaf = get_zaf_kaf(umk.creator.deparmt)

            #создание временной дирректории
            tmpdir = gettempdir()
            dir_path = "{0}/{1}/{2}/{3}".format(tmpdir, plans[0].year,"{0} {1}".format(plans[0].get_training_program_display(),plans[0].get_qualif_display()),umkname)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            ####создание рабочей программы
            doc = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_work_program.docx'))
            render_in_docx(doc, context_workprogram(umk, umkdata, plans, competens, zaf_kaf, doc), "{0}-{1}".format(code_OPOP,umkname), myzip, dir_path)

            #создание аннотации
            ann_doc = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_annotation.docx'))
            render_in_docx(ann_doc, context_annotation(umk, umkdata, plans, competens, zaf_kaf, ann_doc), "{0}-{1}-аннотация".format(code_OPOP, umkname), myzip, dir_path)

            # Создание КОС
            if plans[0].year >= 2016:
                kos_doc = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_kos.docx'))
                render_in_docx(kos_doc, context_KOS(umk, umkdata, plans, competens,zaf_kaf, kos_doc), "{0}-{1}-КОС".format(code_OPOP,umkname), myzip, dir_path)
                if plans[0].exam_semestr:
                    generation_exam_bilets(umk, umkdata, plans, zaf_kaf, myzip, dir_path)

            #удаление временной дирректории
            shutil.rmtree(dir_path, ignore_errors=True)

    res = HttpResponse(tmpfile.getvalue(), content_type='application/zip')
    res['Content-Disposition'] = 'attachment; filename=result-{0}.zip'.format(datetime.today().strftime("%Y-%m-%d"))
    res['Content-Length'] = tmpfile.tell()
    return res



def generation_meth_obespech(id , tbl_lit_json, year=datetime.now().year):#формирование карты метод. обеспечения
    umkdata = UmkData.objects.get(umk_id=id)
    umk = umkdata.umk_id
    plans = umk.get_plan_list()
    umkname = umk.get_short_name()  # имя дисциплины и профиль
    code_OPOP = umk.get_plan_ochka().code_OPOP.replace("/","_")
    zaf_kaf = get_zaf_kaf(umk.creator.deparmt)

    rp_file_object = NamedTemporaryFile(prefix="{0}-{1}-КМО".format(code_OPOP,umkname), suffix='.docx')  # create temp file

    document = DocxTemplate(os.path.join(os.path.join(settings.BASE_DIR, "static/doc_templ"), 'template_card_method_obespech.docx'))
    document.render(context = {
       'kafedra': umk.creator.deparmt.name,
       'zav_kaf': get_zaf_kaf_w_signature_pic(zaf_kaf,document),
       'bibliotekar': get_user_fio_w_signature('bibliotekar', umk.creator.deparmt.units),
       'Discipline': plans[0].get_discipline(),
       'direction': plans[0].get_direction(),
       'year': year,
       'crs_och': get_course(plans[0].get_semestrs()),
       'crs_z': get_course(plans[1].get_semestrs())  if plans[1] is not None else "-",
       'crs_zu': get_course(plans[2].get_semestrs()) if plans[2] is not None else "-",
       'smr_och': plans[0].get_semestrs(),
       'smr_z': plans[1].get_semestrs() if plans[1] is not None else "-",
       'smr_zu': plans[2].get_semestrs() if plans[2] is not None else "-",
       'tbl_liter': get_table_literature_from_json(tbl_lit_json)
    })
    document.save(rp_file_object.name)

    res = HttpResponse(rp_file_object.file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    fname = transliterate.translit("{0}-{1}-КМО.docx".format(code_OPOP,umkname.replace(" ","_")),"ru", reversed=True)
    if len(fname)>100:
        fname = "result-KMO.docx"

    res['Content-Disposition'] = 'attachment; filename='+fname
    res['Content-Length'] = os.path.getsize(rp_file_object.name)
    return res