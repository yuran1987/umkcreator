from django.urls import reverse
from admin_tools.menu import items, Menu
from django.conf import settings

# to activate your custom menu add the following to your settings.py:
#
# ADMIN_TOOLS_MENU = 'test_proj.menu.CustomMenu'

class CustomMenu(Menu):
    """
    Custom Menu for test_proj admin site.
    """
    class Media:
        css = {
           'all': ('css/menu.css',),
        }
        js = ('js/menu.js',)

    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(('Dashboard'), reverse('admin:index')),
            items.ModelList('Данные университета',
                [ 'core.models.Ministerstvo',
                  'core.models.Univercity',
                  'core.models.Units',
                  'core.models.Departaments',
                ]
            ),
            items.ModelList('Ввод',
                            ['core.models.Discipline',
                             'core.models.Directions',
                             'core.models.Profiles',
                             'core.models.Competence',
                             'core.models.Plans',
                             'core.models.UmkArticles',
                             'core.models.UmkData'
                             ]
            ),
            items.ModelList(
                'Пользователи',
                ['django.contrib.auth.*',settings.AUTH_USER_MODEL_FOR_MENU]
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass