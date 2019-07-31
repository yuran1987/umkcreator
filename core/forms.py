from django import forms
from django.core.exceptions import ValidationError
from .models import Discipline, Directions, Plans, Departaments,UmkArticles, UmkData
from .core_funcs import TRANING_PROGRAMS, QUALIFICATION_VALUES
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, TabHolder, Tab, FieldWithButtons, StrictButton
from django.utils.timezone import datetime
from django.contrib.auth import get_user_model
from tinymce.widgets import TinyMCE
import os


class SelectDisipForm(forms.Form):
    discip_val = forms.ModelChoiceField(queryset=Discipline.objects.all().order_by("name"), help_text=u'Выберете дисциплину', label=u'Дисциплина')
    direct_val = forms.ModelChoiceField(queryset=Directions.objects.all(), help_text=u'Выберете направление', label=u'Направление')
    training_program = forms.ChoiceField(choices=TRANING_PROGRAMS, help_text=u'Выберите программу обучения для специалиста или бакалавра',label=u'Программа обучения')  # Программа обучения
    year = forms.ChoiceField(choices=([x,x] for x in range(2014,datetime.now().year)), help_text=u'Выберете год набора',label=u'Год набора')
    def __init__(self, *args, **kwargs):
        super(SelectDisipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(Submit('save', u'Далее', css_class="btn-primary"),
                        Submit('cancel', 'Отмена'))
        )

class SelectPlanForm(forms.ModelForm):
    f_plan_ochka = forms.ModelChoiceField(queryset=Plans.objects.all(), help_text=u'Выберете учебный план для очной формы обучения', label=u'Учебный план для очн.ф.обуч.')
    f_plan_z = forms.ModelChoiceField(queryset=Plans.objects.all(), help_text=u'Выберете учебный план для заочной формы обучения', label=u'Учебный план для заоч.ф.обуч.',required=False)
    f_plan_zu = forms.ModelChoiceField(queryset=Plans.objects.all(), help_text=u'Выберете учебный план для заочно-ускоренной формы обучения',  label=u'Учебный план для заоч.-уск.ф.обуч.',required=False)

    def __init__(self, *args, **kwargs):
        super(SelectPlanForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div('f_plan_ochka','f_plan_z', 'f_plan_zu'),
            FormActions(Submit('next', 'Сохранить', css_class="btn-primary"),
                        Submit('cancel', 'Отмена'))
        )

    def save(self, user, commit=True):
        instance = super(SelectPlanForm, self).save(commit=False)
        instance.creator = user
        instance.plan = "{0}/{1}/{2}".format(self.cleaned_data['f_plan_ochka'].id,
                                             self.cleaned_data['f_plan_z'].id if self.cleaned_data['f_plan_z'] is not None else "-",
                                             self.cleaned_data['f_plan_zu'].id if self.cleaned_data['f_plan_zu'] is not None else "-")
        #print("plan: ",instance.plan)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = UmkArticles
        fields = ['f_plan_ochka','f_plan_z','f_plan_zu']


class addDatafor_core(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(addDatafor_core, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(TabHolder(
                Tab(u'1. Цели и задачи', Div('aim','tasks')),
                Tab(u'2. Содержание дисциплины',
                        TabHolder(
                            Tab(u'2.1 Содержание разделов и тем дисциплины',Div(css_id='tablecontentOfSections'), Div('contentOfSections')),
                            Tab(u'2.2 Междициплинарные связи с последующими дисциплинами',Div(css_id='tableinterdiscipRelations'), Div('interdiscipRelations')),
                            Tab(u'2.3 Разделы (модули), темы дисциплин виды занятий', Div(css_id='tablesectionshour',css_class='col-md-auto'), Div('table_sections_hour'),
                                Div(Button('button_calc', 'Рассчитать часы', css_class='btn btn-success', css_id='button_fill_hour_sections'))),
                            Tab(u'2.4 Перечень лекционных занятий', Div(css_id='tablelectureshour', css_class='col-md-auto'), Div('table_lectures_hour'),
                                Div(Button('button_calc','Рассчитать часы',css_class='btn btn-success', css_id='button_fill_hour_lec'))),
                            Tab(u'2.8 Перечень тем самостоятельной работы', Div(css_id='tablesamosthour', css_class='col-md-auto'), Div('table_samost_hour'),
                                    Div(Button('button_calc', 'Рассчитать часы', css_class='btn btn-success', css_id='button_fill_hour_samost'))),
                            Tab(u'2.9 Примерная тематика курсовых проектов (работ)', Div('theme_kursovih_rabot')),
                            Tab(u'2.10 Лицензионное программное обеспечение', Div('software_lic')),
                        )
                    ),
                Tab(u'3 Материально-техническое обеспечение дисциплины', Div('material_teh_obespech_dicip')),
                Tab(u'4 Базы данных, информационно-справочные и поисковые системы', Div('database_info_system'))),
                css_id='tabslist'
            ),
            FormActions(Submit('next', u'Сохранить', css_class="btn-primary", css_id='btn_save_data_umk'),
                        Submit('cancel', u'Назад'))
        )

        self.fields['aim'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30})
        self.fields['tasks'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30})
        self.fields['contentOfSections'].widget = forms.HiddenInput()
        self.fields['interdiscipRelations'].widget = forms.HiddenInput()
        self.fields['table_sections_hour'].widget = forms.HiddenInput()
        self.fields['table_lectures_hour'].widget = forms.HiddenInput()
        self.fields['table_samost_hour'].widget = forms.HiddenInput()
        self.fields['material_teh_obespech_dicip'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30})
        self.fields['database_info_system'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30})
        self.fields['software_lic'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30})

    def save(self, commit=True):
        instance = super(addDatafor_core, self).save(commit=False)
        instance.umk_id.status = 'edit'
        instance.umk_id.save()

        if commit:
            instance.save()
        return instance

    class Meta:
        model = UmkData
        exclude = ['umk_id','table_prakt_hour','table_laborat_hour', 'table_rating_ochka', 'table_rating_zaochka', 'table_literature', 'kos']

class addDatafor_addons_form(forms.Form):
    data_field = forms.CharField(widget = forms.Textarea(),required = False)

    def __init__(self, *args, **kwargs):
        super(addDatafor_addons_form, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(css_id='tablejexcel', css_class='col-md-auto'), Div('data_field'),
            FormActions(Submit('next', u'Сохранить', css_class="btn-primary", css_id='btn_save'),
                        Submit('cancel', u'Назад'),Button('button_calc', 'Рассчитать часы', css_class='btn btn-success', css_id='button_fill_hour'))
        )
        self.fields['data_field'].widget = forms.HiddenInput()
    class Meta:
        fields = ['data_field']


class rating_form(forms.Form):
    rating_ochka = forms.CharField(widget = forms.Textarea(), required=False)
    rating_zaochka = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super(rating_form, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab(u'1 Рейтинговая система оценки для очников', Div(css_id='tablejexcel_ochka', css_class='col-md-auto'), Div('rating_ochka')),
                Tab(u'2 Рейтинговая система оценки для заочников', Div(css_id='tablejexcel_zaochka', css_class='col-md-auto'), Div('rating_zaochka'))),
            FormActions(Submit('next', u'Сохранить', css_class="btn-primary", css_id='btn_save'),
                        Submit('cancel', u'Назад'))
        )
        self.fields['rating_ochka'].widget = forms.HiddenInput()
        self.fields['rating_zaochka'].widget = forms.HiddenInput()


class ChoiceField_without_validate(forms.ChoiceField):
    # The only thing we need to override here is the validate function.
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])

class literature_form(forms.Form):
    data_field = forms.CharField(widget=forms.Textarea(), required=False)
    liter_search = forms.CharField(label='Строка поиска:', widget=forms.TextInput, required=False, initial=u'Информатика')
    type_search_system = ChoiceField_without_validate(label=u'Поисковая система:', required=False, choices=(('urait','Издательство: Юрайт'),('lanbook','Издательство: Лань')))
    liters_list = ChoiceField_without_validate(label=u'Результат поиска:', required=False)

    def __init__(self, *args, **kwargs):
        super(literature_form, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab(u'1. Литература', Div(css_id='tablejexcel', css_class='col-md-auto'), Div('data_field')),
                Tab(u'2. Подбор', Row(Div('type_search_system', css_class="col-md-4 col-md-push-8"), FieldWithButtons('liter_search', Button('bsearch',"Искать",css_id='start_bsearch'), css_class="col-md-8 col-md-pull-4")), Div('liters_list'),Button('button_add', 'Добавить в таблицу', css_class='btn btn-success',css_id='button_add_to_table')),
            ),
            FormActions(Submit('next', u'Сохранить', css_class="btn-primary", css_id='btn_save'),
                        Submit('cancel', u'Назад'))
        )
        self.fields['data_field'].widget = forms.HiddenInput()

    class Meta:
        fields = ['data_field','liters_list','liter_search']


class card_method_obespech(forms.Form):
    data_field = forms.CharField(widget=forms.Textarea(), required=False)
    umk_src = forms.ModelChoiceField(queryset=UmkArticles.objects.all(),help_text=u'Выберете рабочую программу к которой хотите сделать карту мед. обес.',
                                     label=u'Рабочая программа:')
    year = forms.ChoiceField(choices=([x, x] for x in reversed(range(2014, datetime.now().year+1))), help_text=u'Выберете год формирования', label=u'Год')

    def __init__(self, *args, **kwargs):
        super(card_method_obespech, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(Div(FieldWithButtons('umk_src', Button('bchoosen', "Выбрать", css_id='start_search'))), Div('year',css_class="col-md-2 col-xs-3"), Div(css_id='tablejexcel'),
            Div('data_field')),
            FormActions(Submit('export', u'Сформировать', css_class="btn-primary", css_id='btn_export'), #
                        Submit('save', u'Сохранить', css_class="btn-success", css_id='btn_save'),
                        Submit('cancel', u'Назад'))
        )
        self.fields['data_field'].widget = forms.HiddenInput()

    class Meta:
        fields = ['data_field','umk_src', 'year']


################################################################################
#
#
#                       КОС
#
#
################################################################################
class form_kos(forms.Form):
    data_field = forms.Field(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)

    def __init__(self, *args, **kwargs):
        super(form_kos, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div('data_field'),
            FormActions(Submit('next', u'Сохранить', css_class="btn-primary", css_id='btn_save_data_umk'),
                        Submit('cancel', u'Назад'))
        )




###################
#Копирование одной рабочей программы в другую
###################
class Umkcopy_form(forms.Form):
    umk_src = forms.ModelChoiceField(queryset=UmkArticles.objects.all(), help_text=u'Выберете исходную рабочую программу', label=u'Рабочая программа источник:')
    umk_dst = forms.ModelChoiceField(queryset=UmkArticles.objects.all(), help_text=u'Раб. программа в которую будет произведено копирование', label=u'Рабочая программа назначение:')

    def __init__(self, *args, **kwargs):
        super(Umkcopy_form, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(Div('umk_src'), Div('umk_dst')),
            FormActions(Submit('next', u'Далее', css_class="btn-primary", css_id='btn_next'),
                        Submit('cancel', u'Назад'))
        )
    class Meta:
        fields = ['umk_src','umk_dst']
########################################################################################################################
#
#                               Работа с учебным планом
#
#
########################################################################################################################
def validate_file_xlsx(val):#проверка на нужный формат файла
    ext = os.path.splitext(val.name)[1]
    valid_ext = ['.xlsx']
    if not ext.lower() in valid_ext:
        raise ValidationError(u'Не поддерживаемый формат файла')

def validate_file_docx(val):#проверка на нужный формат файла
    ext = os.path.splitext(val.name)[1]
    valid_ext = ['.docx']
    if not ext.lower() in valid_ext:
        raise ValidationError(u'Не поддерживаемый формат файла')

class UploadFilePlanForm(forms.Form):
    fname = forms.FileField(help_text=u'Выберете файл в котором содержится план в формате .xlsx', label=u'Файл с планом', validators=[validate_file_xlsx], required=True)
    type_edu = forms.ChoiceField(help_text=u'Выберите форму обучения',label=u'Форма обучения', choices=[(0,'Очная'), (1,'Заочная'), (2,'Заочно-ускоренная')],required=True)
    num_prof = forms.IntegerField(help_text=u'Введите количество профилей, которое содержится в учебном плане', label=u'Количество уч.профилей',min_value=1,max_value=5, initial=1) #максимальное количество профилей равное 5 сделано на будущее
    num_prikaz = forms.IntegerField(help_text=u'Введите номер', label=u'Номер приказа',min_value=1, initial=1) #номер приказа
    date_prikaz = forms.DateField(help_text=u'Введите дату', label=u'Дата приказа', initial=datetime.today, input_formats=["%d/%m/%Y"]) #номер приказа
    depar = forms.ModelChoiceField(queryset=Departaments.objects.all(), label=u'Кафедра', help_text=u'Кафедра за которой будет закреплено данное направление')
    isUpdate = forms.BooleanField(label="Обновление", help_text=u'Обновить только часы, кол-во недель', required=False)


    def __init__(self, *args, **kwargs):
        super(UploadFilePlanForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div('fname'),
            Row(Div('type_edu', css_class='col-md-4'),Div('num_prof', css_class='col-md-4'), Div('depar', css_class='col-md-4')),
            Row(Div('num_prikaz', css_class='col-md-4'), Div('date_prikaz', css_class='col-md-4'), Div('isUpdate', css_class='col-md-4')),
            FormActions(Submit('upload', u'Загрузить', css_class="btn-primary"))
        )
        self.fields['date_prikaz'].widget.attrs["id"] = 'datetimepicker'

class UploadFileCompetenceForm(forms.Form):
    fname = forms.FileField(help_text=u'Выберете файл в котором содержится паспорт компетенций в формате .docx', label=u'Файл с паспортом компетенций', validators=[validate_file_docx], required=True)
    direction = forms.ModelChoiceField(queryset=Directions.objects.all(), help_text=u'Выберете направление',label=u'Направление')
    training_program = forms.ChoiceField(label=u'Программа обучения', choices=TRANING_PROGRAMS)
    qualif = forms.ChoiceField(label=u'Квалификация', choices=QUALIFICATION_VALUES, initial='bachelor')

    def __init__(self, *args, **kwargs):
        super(UploadFileCompetenceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div('fname', 'direction'),
            Row(Div('training_program', css_class="col-md-4"), Div('qualif', css_class="col-md-4")),
            FormActions(Submit('upload', u'Загрузить', css_class="btn-primary"))
        )



class UserFormEdit(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserFormEdit, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(Div('first_name',css_class="col-md-2"), Div('last_name',css_class="col-md-2"),Div('patronymic',css_class="col-md-2"),Div('birthday', css_class="col-md-2")),
            Row(Div('deparmt', css_class="col-md-2"),  Div('position', css_class="col-md-2"),Div('science_stepen', css_class="col-md-2"), Div('science_zvanie', css_class="col-md-2")),
            Row(Div('electronic_signature', css_class="col-md-3"),Div('email', css_class="col-md-3"),Div('sets', css_class="col-md-3")),
            Row(Div('scopus_id', css_class="col-md-3"), Div('elibrary_id', css_class="col-md-3")),
            FormActions(Submit('save', u'Сохранить', css_class="btn-primary", css_id='btn_save'),
                        Submit('cancel', u'Назад'))
        )

    class Meta:
        model = get_user_model()
        fields = ['first_name','last_name','patronymic','birthday','deparmt',
                  'position','science_stepen','science_zvanie',
                  'electronic_signature', 'email',
                  'sets', 'scopus_id', 'elibrary_id' ]

    def save(self,first_name, last_name, patronymic, birthday, deparmt, position,
             science_stepen, science_zvanie, electronic_signature, email, sets,
             scopus_id, elibrary_id):
        user = super(UserFormEdit, self).save(commit=False)
        user.first_name = first_name
        user.last_name = last_name
        user.patronymic = patronymic
        user.birthday = birthday
        user.deparmt = deparmt
        user.position = position
        user.science_stepen = science_stepen
        user.science_zvanie = science_zvanie
        user.electronic_signature = electronic_signature
        user.email = email
        user.sets = sets
        user.scopus_id = scopus_id
        user.elibrary_id = elibrary_id
        user.save()
        return user