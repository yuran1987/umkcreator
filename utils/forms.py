from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import FormActions

class Convert2File(forms.Form):
    infname = forms.FileField(help_text=u'Выберете файл в формате .pdf', label=u'Исходный файл', required=True)
    cutfname = forms.FileField(help_text=u'Выберете файл в формате .pdf', label=u'Файл содержащий заменяемые страницы', required=True)
    type = forms.CharField(widget=forms.TextInput,help_text=u"Например:1,2,3,22", label=u'Удаляемые страницы',required=True)

    def __init__(self, *args, **kwargs):
        super(Convert2File, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div('infname', 'cutfname'),
            Div('type'),
            FormActions(Submit('run_convert', u'Конвертировать', css_class="btn-primary"))
        )
