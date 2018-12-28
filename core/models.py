from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from .core_funcs import getSemestrs_1d, TRANING_PROGRAMS, QUALIFICATION_VALUES
# Create your models here.
#----------------------------------------------------------------------------------------------------------------------
#Информация о университете и подразделениях
class Univercity(models.Model):
    name = models.CharField(primary_key=True,max_length=255, verbose_name=u'Название университета')
    ministerstvo = models.CharField(max_length=255, verbose_name=u'Министерство', default=u'Министерство науки и высшего образования РФ')

    class Meta:
        verbose_name = u'Университет'
        verbose_name_plural = u'Список университетов'

    def __str__(self):
        return self.name

class Units(models.Model): #Подразделения
    univer = models.ForeignKey(Univercity, on_delete=models.CASCADE, verbose_name=u'Название университета')
    name = models.CharField(primary_key=True, max_length=255, verbose_name=u'Подразделение университета')
    city = models.CharField(default = u'Сургут', max_length=255, verbose_name=u'Населеный пункт')

    class Meta:
        verbose_name = u'Подразделение'
        verbose_name_plural = u'Список подразделений университета'

    def __str__(self):
        return self.name

class Departaments(models.Model):#кафедра
    units = models.ForeignKey(Units, null=True, on_delete=models.CASCADE, verbose_name=u'Название подразделения')
    name = models.CharField(primary_key=True, max_length=255, verbose_name=u'Название кафедры')

    class Meta:
        verbose_name = u'Кафедры'
        verbose_name_plural = u'Список кафедр'

    def __str__(self):
        return self.name
#----------------------------------------------------------------------------------------------------------------------
class Discipline(models.Model):  # Дисциплина
    name = models.CharField(max_length=255, verbose_name=u'Дисциплина',help_text=u'Введите название дисциплины')

    class Meta:
        verbose_name = u'Дисциплина'
        verbose_name_plural = u'Список дисциплин'

    def __str__(self):
        return self.name

#----------------------------------------------------------------------------------------------------------------------
class Directions(models.Model):  # Направление обучения
    name = models.CharField(max_length=255, verbose_name=u'Название направления')
    code = models.CharField(max_length=60, verbose_name=u'Код направления')
    number_prikaz = models.PositiveIntegerField(default=1, verbose_name=u'№ приказа')
    date_prikaz = models.DateField(default = timezone.datetime.today, verbose_name=u'Дата приказа')
    deparmt = models.ForeignKey(Departaments, null=True, on_delete=models.CASCADE, verbose_name=u'Кафедра', help_text=u'Название кафедры за которой закрепляется направление')

    class Meta:
        verbose_name = u'Направления'
        verbose_name_plural = u'Список направлений обучения'

    def get_absolute_url(self):
        return self.pk

    def __str__(self):
        return self.code + ': ' + self.name + u' приказ №' + str(self.number_prikaz) + u' от ' + str(self.date_prikaz)
#----------------------------------------------------------------------------------------------------------------------
class Profiles(models.Model):  # Профиль обучения
    direction = models.ForeignKey(Directions, on_delete=models.CASCADE, verbose_name=u'Название направления')
    name = models.CharField(primary_key=True, max_length=255, verbose_name=u'Название профиля')

    class Meta:
        verbose_name = u'Профиль'
        verbose_name_plural = u'Профили обучения'

    def __str__(self):
        return self.name

#----------------------------------------------------------------------------------------------------------------------
class Competence(models.Model): #Список компетенций
    direction = models.ForeignKey(Directions, on_delete=models.CASCADE, verbose_name=u'Название направления')
    name = models.CharField(verbose_name=u'Название компетенции', max_length=255)
    full_content = models.TextField(verbose_name=u'Содежание компетенции')
    should_know = models.TextField(verbose_name=u'Должен знать')
    should_able = models.TextField(verbose_name=u'Должен уметь')
    should_master = models.TextField(verbose_name=u'Должен владеть')
    training_program = models.CharField(max_length=30, verbose_name=u'Программа обучения', choices=TRANING_PROGRAMS)  # Программа обучения
    qualif = models.CharField(max_length=12, default='Bachelor', verbose_name=u'Квалификация', choices=QUALIFICATION_VALUES)  # Квалификация
    indicators_know = models.TextField(verbose_name=u'Показатели знать', null=True)
    indicators_can = models.TextField(verbose_name=u'Показатели уметь', null=True)
    indicators_own = models.TextField(verbose_name=u'Показатели владеть', null=True)

    class Meta:
        verbose_name = u'Компетенции'
        verbose_name_plural = u'Список компетенций'

    def __str__(self):
        return self.name + ' для ' + self.get_training_program_display() + ' ' + self.get_qualif_display()
#----------------------------------------------------------------------------------------------------------------------
class Plans(models.Model):  # Учебный план
    traningchoices = (
        ['fulltime', u'Очное(4 года)'],
        ['extramural', u'Заочная (5 лет)'],
        ['parttime', u'Заочная (3.5 года)']
    )

    code_OPOP = models.CharField(max_length=15, verbose_name=u'Код ОПОП')  # Код ОПОП
    discipline = models.ForeignKey(Discipline, null=True, on_delete=models.CASCADE, verbose_name=u'Название дисциплины')  # Дисциплина
    profile = models.ManyToManyField(Profiles, verbose_name=u'Профиль')  # Профиль
    direction = models.ForeignKey(Directions, null=True, on_delete=models.CASCADE, verbose_name=u'Направление')
    training_form = models.CharField(max_length=20, choices=traningchoices, default = 'fulltime' , verbose_name=u'Формы обучения')  # форма обучения
    qualif = models.CharField(max_length=12, verbose_name=u'Квалификация', choices=QUALIFICATION_VALUES)  # Квалификация
    training_program = models.CharField(max_length=30, verbose_name=u'Программа обучения', choices=TRANING_PROGRAMS) #Программа обучения
    year = models.IntegerField(default=timezone.datetime.now().year, verbose_name=u'Год набора') #год набора
    semestr = models.CharField(default="1", max_length=15, verbose_name=u'Семестр')  # семестр
    trudoemkost_all = models.PositiveIntegerField(default=1, verbose_name=u'Общая трудоемкость, часов')  # общая трудоемкость
    trudoemkost_zachot_edinic = models.IntegerField(null=True,default=1, verbose_name=u'Количество зачетных единиц')  # количество зачетных единиц
# Аудиторная работа
    hours_audit_work_sum = models.PositiveIntegerField(default=1, verbose_name=u'Количество аудиторной работы, час')  # Общее количество аудиторной работы
    hours_lectures = models.PositiveIntegerField(default=0, verbose_name=u'на лекции,час')  # Количество часов на лекции
    hours_pract = models.PositiveIntegerField(default=0, verbose_name=u'на практические работы,часов')  # Количество часов на практические занятия
    hours_labs = models.PositiveIntegerField(default=0, verbose_name=u'на лабораторные работы,часов')  # Количество часов на лабораторные занятия
    #hours_seminars = models.PositiveIntegerField(default=0, verbose_name=u'на семинарские работы,часов')  # Количество часов на семинарские занятия
# Самостоятельная работа
    hours_samost_work_sum = models.PositiveIntegerField(default=1, verbose_name=u'Общее количество самостоятельной работы,часов')
    hours_samost_wo_lec = models.FloatField(default=1, verbose_name=u'Самостоятельная работа студента без преподавателя, часов')
    hours_samost_w_lec_w_stud = models.FloatField(default=1, verbose_name=u'Самостоятельная работа студентов с преподавателем, часов')
    hours_samost_w_lec_w_group = models.FloatField(default=1, verbose_name=u'Самостоятельная работа группы с преподавателем, часов')
# Другие
    exam_semestr = models.CharField(max_length=10,verbose_name=u'Экзамен в семестре', help_text=u'Формат: 1,2', null=True,blank=True)  # экзамен в семестре
    zachot_semestr = models.CharField(max_length=10,verbose_name=u'Зачет в семестре', help_text=u'Формат: 1,2', null=True,blank=True)  # зачет в семестре
    kursovya_work_project = models.CharField(null=True,max_length=15, verbose_name=u'КП/КР') #Курсовой проект/курсовая работа
    kontrolnaya_work = models.CharField(null=True,max_length=15, verbose_name=u'Контрольная работа', help_text=u'заполняется только для заочников') #Контрольная работа заполняется только для заочников
    zanatiya_in_interak_forms_hours = models.PositiveIntegerField(null=True, default=1, verbose_name=u'Занятия в интерактивной форме, часов')  # занятия в интерактивной форме, часов
    comps = models.TextField(null=True,blank=True, verbose_name=u'Компетенции') #Список компетенций
    weeks_count_in_semestr = models.CharField(max_length=20,verbose_name=u'Количество недель в семестре', help_text=u'Формат: 17,18', null=True,blank=True)  # Количество недель в семестре

    class Meta:
        verbose_name = u'Учебный план'
        verbose_name_plural = u'Список учебных планов'

    def get_semestrs(self):
        return self.semestr

    get_semestrs.short_description = 'Семестр'

    def get_if_zachot_exam(self):
        zachot = getSemestrs_1d(self.zachot_semestr)
        exam = getSemestrs_1d(self.exam_semestr)

        result = ""

        if len(zachot)>1 and int(zachot[0])>0:
            result = result + '{0} в {1} семестре '.format('Зачет', str(self.zachot_semestr))
        elif len(zachot)==1 and int(zachot[0])>0:
            result = result + '{0} в {1} семестре '.format('Зачет', str(self.zachot_semestr))


        if len(exam)>1 and int(exam[0])>0:
             result = result + '{0} в {1} семестре '.format('Экзамен', str(self.exam_semestr))
        elif len(exam) == 1 and int(exam[0]) > 0:
             result = result + '{0} в {1} семестре '.format('Экзамен', str(self.exam_semestr))

        return result

    get_if_zachot_exam.short_description = u'Аттестация'

    def get_profiles(self):
        profiles_list = self.profile.get_queryset()
        profiles_str = ''
        for p in profiles_list:
            profiles_str += ', ' + str(p.__str__())
        return profiles_str.lstrip(', ')

    get_profiles.short_description = u'Профили'

    def get_direction(self):
        return self.direction.code + ": " + self.direction.name

    get_direction.short_description = u'Направления'

    def get_trudoemkost_zach_ed(self):
        return "{0}/{1}".format(self.trudoemkost_all,self.trudoemkost_zachot_edinic if self.trudoemkost_zachot_edinic else "-")

    get_trudoemkost_zach_ed.short_description = u'Трудоемкость, ч./ зач. ед., ч.'


    def check_trudoemkost(self):
        v_audit = self.hours_lectures + self.hours_labs + self.hours_pract
        v_samot = self.hours_samost_wo_lec + self.hours_samost_w_lec_w_stud + self.hours_samost_w_lec_w_group
        color_code = '000000'
        s_msg = ''
        if v_audit != self.hours_audit_work_sum:
            color_code = 'FF0000'
            s_msg = u'Ошибка в аудиторных часах'
        elif round(v_samot) != self.hours_samost_work_sum:
            color_code = 'FF0000'
            s_msg = u'Ошибка в самостоятельных часах {0}!={1}'.format(round(v_samot),self.hours_samost_work_sum)
        elif (v_audit + v_samot) == self.trudoemkost_all:
            color_code = '008000'
            s_msg = 'OK'
        return format_html('<span style="color: #{0};">{1}</span>', color_code,s_msg)

    check_trudoemkost.short_description = u'Статус'

    def get_discipline(self):
        return str(self.discipline.name)

    def __str__(self):
        return str(self.discipline) + ' ' + self.get_profiles() + ' ' + self.get_training_form_display() + ' '+ "{0} {1}а".format(self.get_training_program_display(), self.get_qualif_display())  +' набор ' + str(self.year) + ' семестр:' + str(self.get_semestrs()) +\
               ' ' + '{0}/{1}'.format(self.trudoemkost_all,self.trudoemkost_zachot_edinic)

    def get_direction_date_prikaz(self):
        direction_tmp = self.profile.get_queryset()[0].direction
        return [ direction_tmp.number_prikaz,direction_tmp.date_prikaz ]


#----------------------------------------------------------------------------------------------------------------------
class UmkArticles(models.Model):
    statuschoices = (
        ['edit', u'Наполнение'],
        ['signaturing', u'На подписи'], #Отправлена на подпись
        ['confirmed', u'Подписана'],  #ПОдписана зав.кафедрой или председателем СПН
        ['empty', u'Пустая']
    )

    plan_ochka = models.PositiveIntegerField(null=True,verbose_name=u'Учебный план для очн.ф.обуч.')  # учебный план для очной формы обучения
    plan_z = models.PositiveIntegerField(null=True, verbose_name=u'Учебный план для заоч.ф.обуч.')  # учебный план для заочной формы обучения
    plan_zu = models.PositiveIntegerField(null=True,verbose_name=u'Учебный план для заоч.-уск.ф.обуч.')  # учебный план для заочно-ускоренной формы обучения
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=u'Пользователь')
    datetime_created = models.DateTimeField(verbose_name=u'Дата создания',default=timezone.now)
    datetime_changed = models.DateTimeField(verbose_name=u'Дата изменения',default=timezone.now)
    status = models.CharField(max_length=50, choices=statuschoices, default = 'empty', verbose_name=u'Статус')

    class Meta:
        verbose_name = u'Рабочая программа'
        verbose_name_plural = u'Рабочие программы'

    def get_short_name(self):
        name = str(Plans.objects.get(id=self.plan_ochka).discipline.name)
        prof = str(Plans.objects.get(id=self.plan_ochka).get_profiles())
        res1 = name if len(name) < 15 else name[0:35]
        res2 = prof if len(prof) < 15 else prof[0:35]
        return "{0}-{1}".format(res1,res2)

    def __str__(self):
        plan = Plans.objects.get(id=self.plan_ochka)
        return '#' + str(self.id) + ' ' + str(plan.discipline.name if len(plan.discipline.name)<15 else plan.discipline.name[0:35]+"...") + " " + str(plan.get_profiles()) + " {0} {1}а".format(plan.get_training_program_display(),plan.get_qualif_display())


class UmkData(models.Model):
    umk_id = models.OneToOneField(UmkArticles, on_delete=models.CASCADE, verbose_name=u'ID рабочей программы')
    aim = models.TextField(verbose_name=u'Цель дисциплины')
    tasks = models.TextField(verbose_name=u'Задачи дисциплины')
    contentOfSections = models.TextField(verbose_name=u'Содержание разделов и тем дисциплины', null=True)
    interdiscipRelations = models.TextField(verbose_name=u'Междисциплинарные связи c обеспециваемыми дисциплины', null=True)
    table_sections_hour = models.TextField(verbose_name=u'Разделы (модули), темы дисциплин ви виды занятий', null=True)
    table_lectures_hour = models.TextField(verbose_name=u'Перечень лекционных занятий', null=True)
    table_prakt_hour = models.TextField(verbose_name=u'Перечень практических занятий', null=True, blank=True)
    table_laborat_hour = models.TextField(verbose_name=u'Перечень лабораторных занятий', null=True, blank=True)
    table_samost_hour = models.TextField(verbose_name=u'Перечень самостоятельных занятий', null=True)
    #-----------------------------------
    theme_kursovih_rabot = models.TextField(verbose_name=u'Примерная тематика курсовых проектов (работ)', null=True, blank=True)
    # -----------------------------------
    table_rating_ochka = models.TextField(verbose_name=u'Рейтинговая система оценки для очников', null=True, blank=True)
    table_rating_zaochka = models.TextField(verbose_name=u'Рейтинговая система оценки для заочников', null=True, blank=True)
    table_literature = models.TextField(verbose_name=u'Список литературы', null=True, blank=True)
    material_teh_obespech_dicip = models.TextField(verbose_name=u'Материально-техническое обеспечение дисциплины')
    database_info_system = models.TextField(verbose_name=u'Базы данных, информационно-справочные и поисковые системы', null=True, blank=True)
    software_lic = models.TextField(verbose_name=u'Лицензионное программное обеспечение', null=True, blank=True)
    #-----------------------------------------КОС------------------------------
    kos = models.TextField(verbose_name=u'Комплект оценочных средств', null=True, blank=True)

    class Meta:
        verbose_name = u'Данные раб.программы'
        verbose_name_plural = u'Данные раб.программ'

    def __str__(self):
        return 'ID: ' + str(self.umk_id.id)


########################################################################################################################
# расширяем модель пользователя
class User(AbstractUser):
     position_choises = (
                 ['assistant', 'асс.'],
                 ['prepod', 'преп.'],
                 ['starshii_prepodavatel', 'ст.преп.'],
                 ['proffessor', 'проф.'],
                 ['docent', 'доц.'],
                 ['zaf_kaf', 'зав.каф.'],
                 ['io_zaf_kaf', 'И.о. зав.каф.'],
                 ['ved_spec', 'вед.спец.'],
                 ['glav_red', 'гл.ред.'],
                 ['glav_spec', 'гл.спец.'],
                 ['dekan', 'декан'],
                 ['director', 'дир.'],
                 ['zam_dekan', 'зам.дек.'],
                 ['zam_director', 'зам.дир.'],
                 ['konsultant', 'конс.'],
                 ['laborant', 'лаб.'],
                 ['nauch_konsultant', 'науч.конс.'],
                 ['nach_upravleniya', 'нач.упр.'],
                 ['prorector', 'проректор'],
                 ['rector', 'ректор'],
                 ['specialist', 'спец.'],
                 ['starshii_specialist', 'ст.спец.'],
                 ['starshii_laborant', 'ст.лаб.'],
                 ['starshii_tehnik', 'ст.техн.'],
                 ['stajer', 'стажер'],
                 ['tehnik', 'техн.'],
                 ['uch_sekretar', 'уч.секр.'],
                 ['predsedatel_spn', 'председатель СПН'],
     )

     sci_stepen_schoises = ( #Сокращения учёных степеней и званий (в соответствии с рекомендациями Министерство Образования и Науки РФ)
         ['k_arhitekturi', 'канд. архитектуры'],
         ['k_biol_n', 'канд. биол. наук'],
         ['k_veterinar_n', 'канд. ветеринар. наук'],
         ['k_voen_n', 'канд. воен. наук'],
         ['k_geogr_n', 'канд. геогр. наук'],
         ['k_geol_mineral_n', 'канд. геол.-минерал. наук'],
         ['k_iskusstvovedeniya', 'канд. искусствоведения'],
         ['k_ist_n', 'канд. ист. наук'],
         ['k_kulturologii', 'канд. культурологии'],
         ['k_med_n', 'канд. мед. наук'],
         ['k_ped_n', 'канд. пед. наук'],
         ['k_polit_n', 'канд. полит. наук'],
         ['k_psihol_n', 'канд. психол. наук'],
         ['k_sociol_n', 'канд. социол. наук'],
         ['k_s_h_n', 'канд. с.-х. наук'],
         ['k_teh_n', 'канд. техн. наук'],
         ['k_farmacevt_n', 'канд. фармацевт. наук'],
         ['k_fiz_mat_n', 'канд. физ.-мат. наук'],
         ['k_filol_n', 'канд. филол. наук'],
         ['k_filos_n', 'канд. филос. наук'],
         ['k_him_n', 'канд. хим. наук'],
         ['k_ekon_n', 'канд. экон. наук'],
         ['k_yurid_n', 'канд. юрид. наук'],
         ['d_arhitekturi', 'д-р архитектуры'],
         ['d_biol_n', 'д-р биол. наук'],
         ['d_veterinar_n', 'д-р ветеринар. наук'],
         ['d_voen_n', 'д-р воен. наук'],
         ['d_geog_n', 'д-р геогр. наук'],
         ['d_geol_mineral_n', 'д-р геол.-минерал. наук'],
         ['d_iskusstvovedeniya', 'д-р искусствоведения'],
         ['d_ist_n', 'д-р ист. наук'],
         ['d_kulturologii', 'д-р культурологии'],
         ['d_med_n', 'д-р мед. наук'],
         ['d_ped_n', 'д-р пед. наук'],
         ['d_polit_n', 'д-р полит. наук'],
         ['d_psihol_n', 'д-р психол. наук'],
         ['d_sociol_n', 'д-р социол. наук'],
         ['d_s_h_n', 'д-р с.-х. наук'],
         ['d_tech_n', 'д-р техн. наук'],
         ['d_farmacevt_n', 'д-р фармацевт. наук'],
         ['d_fiz_mat_n', 'д-р физ.-мат. наук'],
         ['d_filol_n', 'д-р филол. наук'],
         ['d_filos_n', 'д-р филос. наук'],
         ['d_him_n', 'д-р хим. наук'],
         ['d_ekon_n', 'д-р экон. наук'],
         ['d_yurid_n', 'д-р юрид. наук'],
     )

     sci_zvaniya = (
         ['docent', u'доцент'],
         ['proffessor', u'профессор'],
         ['no', u'без ученого звания']
     )
     patronymic = models.CharField(null=True, max_length=255,verbose_name="Отчество")
     birthday = models.DateField(blank = True, null = True, verbose_name=u'День рождения')
     deparmt = models.ForeignKey(Departaments, on_delete=models.CASCADE, verbose_name=u'Кафедра', null = True)
     position = models.CharField(choices=position_choises, default="docent",max_length=255,verbose_name="Должность")
     science_stepen = models.CharField(choices=sci_stepen_schoises, default="k_teh_n", max_length=255,verbose_name="Ученая степень")
     science_zvanie = models.CharField(choices=sci_zvaniya, default='no', max_length=255,verbose_name="Ученое звание")
     electronic_signature = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name=u'Электронная подпись')

     def get_patronymic(self):
        return self.patronymic

     def get_is_superuser(self):
         if self.is_superuser == True:
            msg = "Да"
            color_code = "00ff00"
         else:
            msg = "Нет"
            color_code = "0000b3"
         return  format_html('<span style="color: #{0};">{1}</span>', color_code,msg)

     def __str__(self):
       return self.username

     def get_position(self):
         return self.get_position_display()

     def get_fullname(self):
         return "{0} {1}. {2}.".format(self.last_name, self.first_name[0], self.patronymic[0])


     get_patronymic.short_description = u'Отчество'
     get_is_superuser.short_description = u'Администратор'
     get_position.short_description = u'Должность'

     class Meta:
         swappable = 'auth.User'
         verbose_name = u'Пользователь'
         verbose_name_plural = u'Пользователи'