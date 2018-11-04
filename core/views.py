from django.shortcuts import render, render_to_response, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, UpdateView
from django.contrib.auth import get_user_model
from tempfile import NamedTemporaryFile
import os,re
from .forms import SelectDisipForm,SelectPlanForm,addDatafor_core, addDatafor_addons_form, rating_form, UploadFilePlanForm, literature_form, UploadFileCompetenceForm, UserFormEdit,Umkcopy_form
from .import_plans import PlanImport, TypeEduPlan
from .models import UmkArticles,Plans, UmkData, User
from .docxpdf_generator import generation_docx, generation_docx_achive
from .getsysinfo import get_os_info, get_cpu_info,get_meminfo,get_django_version,get_ip_address_server,get_ip_client, get_cpu_cores
from .search_lit import get_lit_urait_json, get_lit_lanbook_json
from .import_competence import CompetenceImport
from .core_funcs import FORMS_CONTROL, TYPE_SAMOSTOYATELNOY_RABORY, METHODS_TEACHER_LEC, METHODS_TEACHER_PRAKT_LABS, TYPE_CONTROL_RATING ,previous_and_next_disciplines_from_umk, getTotalstr
from .umk2copy import umk_copy


# Create your views here.
def index(request):
    return render(request, 'index.html',{'title': settings.SITE_NAME})

def showAuthors(request):
    return render(request, 'authors.html', {'title': settings.SITE_NAME})

def showNews(request):
    return render(request, 'news.html', {'title': settings.SITE_NAME})

def showSysInfo(request):
    osinfo = get_os_info()
    meminfo = get_meminfo()
    return render(request, 'system_info.html', {'title': settings.SITE_NAME,
                                                'domain_name': osinfo[0],
                                                'os_info': osinfo[1],
                                                'python_ver': osinfo[2],
                                                'django_ver': get_django_version(),
                                                'cpu_list': get_cpu_info(),
                                                'total_mem': meminfo['MemTotal'],
                                                'free_mem': meminfo['MemFree'],
                                                'ip_address_server': get_ip_address_server()[0],
                                                'ip_address_for_you': get_ip_client(request),
                                                'cpu_cores': get_cpu_cores()})


class UserProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = "username"
    template_name = "registration/profile.html"

    def get_object(self,queryset=None):
        user = super(UserProfileDetailView,self).get_object(queryset)
        return user

class UserProfileEditView(UpdateView):
    model = get_user_model()
    form_class = UserFormEdit
    template_name = "registration/profile_edit.html"

    def get_object(self,queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("profile", kwargs={"slug": self.request.user})

def User_password_changed(request):
    return render(request, 'registration/password_change_done.html', {'title': settings.SITE_NAME})

def showUmkList(request):
    table = []
    obj = UmkArticles.objects.filter(creator=request.user)
    for a in obj:
        plan = Plans.objects.get(id = a.plan_ochka)
        table.append({'id': a.id,
                      'type': "{0}, {1} {2}а".format(plan.direction, plan.get_training_program_display(), plan.get_qualif_display()),
                      'name': plan.discipline.name,
                      'datetime_create': a.datetime_created.strftime("%d/%b/%Y %H:%M:%S"),
                      'datetime_changed': a.datetime_changed.strftime("%d/%b/%Y %H:%M:%S"),
                      'status':a.get_status_display(),
                      'status_raw': a.status
                  })

    return render(request, 'umklist.html', {'title': settings.SITE_NAME, 'umk_list': table})



#------------------------------------------Работа с учебными планами----------------------------------------------------
def uploadplan(request): #загрузка учебного плана
    if request.method == 'POST':
        form = UploadFilePlanForm(request.POST,request.FILES)
        # check whether it's valid:
        if form.is_valid():
            file = request.FILES['fname']
            file_tmp = NamedTemporaryFile(suffix='.xlsx') #файл в который копироуем план
            with open(file_tmp.name,'wb') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            tp = int(form.cleaned_data['type_edu'])

            p = PlanImport(fname=file_tmp.name, type=TypeEduPlan.FULLTIME if tp==0 else TypeEduPlan.EXTRAMURAL if tp==1 else TypeEduPlan.PART_TIME,
                           num_prof=form.cleaned_data['num_prof'],
                           num_prikaz=form.cleaned_data['num_prikaz'],
                           date_prikaz=form.cleaned_data['date_prikaz'],
                           departament=form.cleaned_data['depar'],
                           isUpdate=form.cleaned_data['isUpdate'])
            print(form.cleaned_data['isUpdate'])

            p.import_plan_of_discipline()
            return HttpResponseRedirect(reverse('planlist'))
    else:
        form = UploadFilePlanForm()
    return render(request, 'form_bootstrap.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Загрузка учебного плана"})

def showPlansAll(request):#отображение всех учебных планов
    table = []
    obj = Plans.objects.all()
    for a in obj:
        table.append({'id': a.id,
                      'disp': a.discipline,
                      'name': a.get_direction(),
                      'prof': a.get_profiles(),
                      'type_edu':a.get_training_form_display(),
                      'kva': "{0} {1}а".format(a.get_training_program_display(), a.get_qualif_display())
                 })

    return render(request, 'planslist.html', {'title': settings.SITE_NAME, 'plan_list': table})

def removePlan(request, id): #удаление учебного плана
    Plans.objects.filter(id=id).delete()
    return HttpResponseRedirect(reverse('planlist'))

def uploadcompetence(request): #загрузка компетенций
    if request.method == 'POST':
        form = UploadFileCompetenceForm(request.POST,request.FILES)
        # check whether it's valid:
        if form.is_valid():
            file = request.FILES['fname']
            file_tmp = NamedTemporaryFile(suffix='.docx')#файл в который копируем компетенции
            with open(file_tmp.name,'wb') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            dat = CompetenceImport(file_tmp.name)
            dat.run_import(direc = form.cleaned_data['direction'], tr_prog=form.cleaned_data['training_program'], qualif=form.cleaned_data['qualif'])
            return HttpResponseRedirect(reverse('planlist'))
    else:
        form = UploadFileCompetenceForm()
    return render(request, 'forms.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Загрузка компетенций"})

########################################################################################################################
#
#                           Работа с рабочими программами
#
########################################################################################################################
def choiseDiscipline(request):
    if request.method == 'POST':
        form = SelectDisipForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            return HttpResponseRedirect(reverse('umk_create', kwargs={'id': request.POST['discip_val'],
                                                                      'direct_id': request.POST['direct_val'],
                                                                      'tr_program': request.POST['training_program']}))
    else:
        form = SelectDisipForm()
    return render(request, 'forms.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Создание рабочей программы дисциплины"})

def create_umk(request, dis_id, direct_id, tr_program):
    if request.method == 'POST':
        form = SelectPlanForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            instance = form.save(request.user)
            umkdata = UmkData.objects.create(umk_id=instance)
            umkdata.save()
            return HttpResponseRedirect(reverse('showumklist'))
    else:
        form = SelectPlanForm()
        form.fields['f_plan_ochka'].queryset = Plans.objects.filter(discipline_id=dis_id, direction_id=direct_id, training_form = 'fulltime', training_program = tr_program)
        form.fields['f_plan_z'].queryset = Plans.objects.filter(discipline_id=dis_id, direction_id=direct_id, training_form = 'extramural', training_program = tr_program)
        form.fields['f_plan_zu'].queryset = Plans.objects.filter(discipline_id=dis_id, direction_id=direct_id, training_form = 'parttime', training_program = tr_program)
    return render(request, 'forms.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Создание рабочей программы дисциплины"})

def remove_umk(request,id):
    UmkArticles.objects.filter(id = id).delete()
    return JsonResponse({'status': 'complete removed'})

def DataForUmk_core(request, id):
    umkdata = UmkData.objects.get(umk_id_id=id)
    plan = [
                Plans.objects.get(id=umkdata.umk_id.plan_ochka),
                Plans.objects.get(id=umkdata.umk_id.plan_z),
                Plans.objects.get(id=umkdata.umk_id.plan_zu)
    ]

    if request.method == 'POST':
        form = addDatafor_core(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(id=umkdata.id, umk_id = umkdata.umk_id,
                      table_prakt_hour=umkdata.table_prakt_hour,
                      table_laborat_hour=umkdata.table_laborat_hour,
                      table_rating_ochka=umkdata.table_rating_ochka,
                      table_rating_zaochka=umkdata.table_rating_zaochka,
                      table_literature=umkdata.table_literature)
            return HttpResponseRedirect(reverse('umk_edit_menu', kwargs={'id': id}))
    else:
        form = addDatafor_core(instance=umkdata)

    hours_for_calc  = ['{0}/{1}/{2}'.format(str(plan[0].hours_lectures),str(plan[1].hours_lectures),str(plan[2].hours_lectures)), #лекции
                       '{0}/{1}/{2}'.format(str(plan[0].hours_pract),str(plan[1].hours_pract),str(plan[2].hours_pract)),          #практики
                       '{0}/{1}/{2}'.format(str(plan[0].hours_labs),str(plan[1].hours_labs),str(plan[2].hours_labs)),             #лаб
                       '{0}/{1}/{2}'.format(str(plan[0].hours_samost_work_sum),str(plan[1].hours_samost_work_sum),str(plan[2].hours_samost_work_sum)),#самост работа
                       '{0}/{1}/{2}'.format(str(plan[0].trudoemkost_all),str(plan[1].trudoemkost_all),str(plan[2].trudoemkost_all)), #всего
                       '{0}'.format(str(plan[0].zanatiya_in_interak_forms_hours))]  #интерактив

    kpkr = "<p>"
    for i in range(0,3):
        if plan[i].kursovya_work_project:
            kpkr += plan[i].kursovya_work_project + "/"
        else:
            kpkr += "-/"

    kpkr += "</p>"
    if re.search("-/-/-",kpkr):
        kpkr = "<p>Учебным планом курсовых работа/проектов не предусмотрено.</p><p>Поэтому данное поле можно оставить пустым.</p>"

    if not plan[1].kontrolnaya_work and not plan[2].kontrolnaya_work:
        kontrol_tooltip = ""
    else:
        kontrol_tooltip = "Контр.работа для "
        if plan[1].kontrolnaya_work:
            kontrol_tooltip += "заоч.ф.обуч. в {0} семестре;".format(plan[1].kontrolnaya_work)
        if plan[2].kontrolnaya_work:
            kontrol_tooltip += "заоч.уск.ф.обуч. {0} семестре".format(plan[2].kontrolnaya_work)


    return render(request, 'edit_umk.html', {'title': settings.SITE_NAME, 'form': form,
                                             'title_form': "Наполнение рабочей программы дисциплины",
                                             'KPKR_tooltip': kpkr,
                                             'kontrol_work_tooltip': kontrol_tooltip,
                                             'hours_for_calc': hours_for_calc,
                                             'exam_zachot': '{0},{1}/{2},{3}/{4},{5}'.format(plan[0].zachot_semestr,plan[0].exam_semestr, plan[1].zachot_semestr,plan[1].exam_semestr, plan[2].zachot_semestr,plan[2].exam_semestr),
                                             'competences': plan[0].comps.lstrip(),
                                             'forms_control': FORMS_CONTROL,
                                             'type_samost_work': TYPE_SAMOSTOYATELNOY_RABORY,
                                             'methods_teacher_lec': METHODS_TEACHER_LEC,
                                             'next_discip': [ d.discipline.name for d in previous_and_next_disciplines_from_umk(plan[0], Plans)['next_disciplines']]})

def DataForUmk_addons(request, id, type):
    umkdata = UmkData.objects.get(umk_id=id)
    tmp_plan = [ Plans.objects.get(id=umkdata.umk_id.plan_ochka),
                 Plans.objects.get(id=umkdata.umk_id.plan_z),
                 Plans.objects.get(id=umkdata.umk_id.plan_zu)
               ]

    hours = "0/0/0"
    if type == 'laborat':
        initl = {'data_field': umkdata.table_laborat_hour}
        title = "4.7 Перечень лабораторных работ"
        header = 'лабораторных'
        hours = "{0}/{1}/{2}".format(str(tmp_plan[0].hours_labs), str(tmp_plan[1].hours_labs), str(tmp_plan[2].hours_labs))
        tooltip = 'Лаб.работы, час. {0}'.format(hours)
    elif type == 'prakt':
        initl = {'data_field': umkdata.table_prakt_hour}
        title = "4.6 Перечень тем практических занятий"
        header = 'практических'
        hours = "{0}/{1}/{2}".format(str(tmp_plan[0].hours_pract), str(tmp_plan[1].hours_pract), str(tmp_plan[2].hours_pract))
        tooltip = 'Практ.работы, час. {0}'.format(hours)

    if request.method == 'POST':
        form = addDatafor_addons_form(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if type == 'laborat':
                umkdata.table_laborat_hour = form.cleaned_data['data_field']
            elif type == 'prakt':
                umkdata.table_prakt_hour = form.cleaned_data['data_field']

            umkdata.umk_id.datetime_changed = str(timezone.datetime.now(tz=timezone.get_current_timezone()))
            umkdata.umk_id.save()
            umkdata.save()
            return HttpResponseRedirect(reverse('umk_edit_menu', kwargs={'id': id}))
    else:
        form = addDatafor_addons_form(initial=initl)

    return render(request, 'edit_umk_act.html', {'title': settings.SITE_NAME, 'form': form,
                                             'title_form': title, 'table_header': header,
                                             'table_hour_tooltip': tooltip,
                                             'hours_for_calc': hours,
                                             'competences': tmp_plan[0].comps,
                                             'meth_tech_pr_labs': METHODS_TEACHER_PRAKT_LABS})


def show_rating(request, id):
    umkdata = UmkData.objects.get(umk_id=id)

    if request.method == 'POST':
        form = rating_form(request.POST)
        # check whether it's valid:
        if form.is_valid():
            umkdata.table_rating_ochka = form.cleaned_data['rating_ochka']
            umkdata.table_rating_zaochka = form.cleaned_data['rating_zaochka']
            umkdata.umk_id.datetime_changed = str(timezone.datetime.now(tz=timezone.get_current_timezone()))
            umkdata.umk_id.save()
            umkdata.save()
            return HttpResponseRedirect(reverse('umk_edit_menu', kwargs={'id': id}))
    else:
        form = rating_form(initial={'rating_ochka': umkdata.table_rating_ochka, 'rating_zaochka': umkdata.table_rating_zaochka})

    totalstr = getTotalstr([ Plans.objects.get(id=umkdata.umk_id.plan_ochka).semestr, Plans.objects.get(id=umkdata.umk_id.plan_z).semestr,
                             Plans.objects.get(id=umkdata.umk_id.plan_zu).semestr
                          ], TYPE_CONTROL_RATING)

    return render(request, 'edit_umk_rating.html', {'title': settings.SITE_NAME, 'form': form,
                                                 'title_form': "Рейтинговая система оценки",
                                                 'type_control_rating_ochka': totalstr['ochka'],
                                                 'type_control_rating_zaochka': totalstr['zaochka'],
                                                 'weeks_count': Plans.objects.get(id=umkdata.umk_id.plan_ochka).weeks_count_in_semestr})

def show_liter(request, id):
    umkdata = UmkData.objects.get(umk_id=id)

    if request.method == 'POST':
        form = literature_form(request.POST)
        # check whether it's valid:
        if form.is_valid():
            umkdata.table_literature = form.cleaned_data['data_field']
            umkdata.umk_id.datetime_changed = str(timezone.datetime.now(tz=timezone.get_current_timezone()))
            umkdata.umk_id.save()
            umkdata.save()
            return HttpResponseRedirect(reverse('umk_edit_menu', kwargs={'id': id}))
    else:
        form = literature_form(initial={'data_field': umkdata.table_literature})

    return render(request, 'literature.html', {'title': settings.SITE_NAME, 'form': form,
                                               'title_form': "Карта обеспеченности дисциплины учебной и учебно-методической литературой"})


def get_literature_from_url(request, type, search, id=0):
    if type=='urait':
        data = get_lit_urait_json(search)
    elif type=='lanbook':
        data = get_lit_lanbook_json(search)
    else:
        data = {'Error': 'Unknown type system search'}

    response = JsonResponse(data,safe=False,charset='utf-8')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def actions(request, type, id=0, direct_id=0, tr_program=''):
    if type=='choiseDisp':
        return choiseDiscipline(request)
    elif type == 'create':
        return create_umk(request,dis_id=id, direct_id=direct_id, tr_program=tr_program)
    elif type == 'editcore':
        return DataForUmk_core(request, id)
    elif type == 'actlist':
        umk = UmkArticles.objects.get(id=id)
        plans = [
            Plans.objects.get(id=umk.plan_ochka),
            Plans.objects.get(id=umk.plan_z),
            Plans.objects.get(id=umk.plan_zu)
        ]
        act = []

        if plans[0].hours_labs > 0 or plans[1].hours_labs > 0 or plans[2].hours_labs > 0:
            act.append({'url': "/umk/edit/{0}/laborat/".format(id), 'name': "Перечень лабораторных работ"})

        if plans[0].hours_pract > 0 or plans[1].hours_pract > 0 or plans[2].hours_pract > 0:
            act.append({'url': "/umk/edit/{0}/prakt/".format(id), 'name': "Перечень практических работ"})

        return render(request, 'edit_umk_actions.html', {'title': settings.SITE_NAME,
                                                         'discipline': plans[0].discipline.name,
                                                         'direction': plans[0].get_direction(),
                                                         'profiles': plans[0].get_profiles(),
                                                         'actions_list': act,
                                                         'umk_id':id})
#######################################################################################################################
#
#
#
#######################################################################################################################
#
#                           Подпись рабочей программы и отправка на подпись
#
########################################################################################################################
def showUmkCopy(request): #копирование данных рабочей программы из одной umk_src в другую umk_dst
    if request.method == 'POST':
        form = Umkcopy_form(request.POST)
        # check whether it's valid:
        if form.is_valid():
            umk_copy(src_umk = request.POST['umk_src'],dst_umk = request.POST['umk_dst'])
            return HttpResponseRedirect(reverse('showumklist'))
    else:
        form = Umkcopy_form()
        form.fields['umk_src'].queryset = UmkArticles.objects.filter(creator=request.user)
        form.fields['umk_dst'].queryset = UmkArticles.objects.filter(creator=request.user)
    return render(request, 'forms.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Копирование рабочей программы дисциплины"})


#########################
def send2signature(request, id): #отправка УМК на процедуру подписи
    if len(id.split("+"))>=2:
        tmp = id.split("+")
        for i in tmp:
            obj = UmkArticles.objects.get(creator=request.user, id=int(i))
            obj.status = 'signaturing'
            obj.save()
    else:
        obj = UmkArticles.objects.get(creator=request.user, id=id)
        obj.status = 'signaturing'
        obj.save()
    return HttpResponseRedirect(reverse('showumklist'))

def send2confirm(request, id): #Подпись УМК
    if len(id.split("+"))>=2:
        tmp = id.split("+")
        for i in tmp:
            obj = UmkArticles.objects.get(id=int(i))
            obj.status = 'confirmed'
            obj.save()
    else:
        obj = UmkArticles.objects.get(id=id)
        obj.status = 'confirmed'
        obj.save()
    return HttpResponseRedirect(reverse('umklistsign'))


##################################
#вывод рабочих прогррамм которые отправлена на подпись зав.кафедрой
def showUmkForSignature(request):
    table = []
    obj = UmkArticles.objects.filter(status='signaturing')
    if obj:
        user_depart = User.objects.get(username=request.user).deparmt
        for a in obj:
            if user_depart == User.objects.get(username=a.creator).deparmt:
                plan = Plans.objects.get(id=a.plan_ochka)
                table.append({'id': a.id,
                              'type': "{0}, {1} {2}а".format(plan.direction, plan.get_training_program_display(),
                                                             plan.get_qualif_display()),
                              'name': plan.discipline.name,
                              'datetime_create': a.datetime_created.strftime("%d/%b/%Y %H:%M:%S"),
                              'datetime_changed': a.datetime_changed.strftime("%d/%b/%Y %H:%M:%S"),
                              'status': a.get_status_display()
                              })

    return render(request, 'umklist_zaf_kav.html', {'title': settings.SITE_NAME, 'umk_list': table})

########################################################################################################################
#
#                               Работа с генератором документов в форматах docx pdf
#
########################################################################################################################

def get_document(request,id,format):
    if format=='docx':
        return generation_docx(id)
    elif format == 'pdf':
        return HttpResponse('Document format {0}'.format(format))
    else:
        return HttpResponse('Document unknown format {0}'.format(format))


def get_document_in_archive(request,id_list,format):
    if format=='docx':
        return generation_docx_achive(str(id_list).split("+"))
    elif format == 'pdf':
        return HttpResponse('Document format {0}'.format(format))
    else:
        return HttpResponse('Document unknown format {0}'.format(format))