from django.db import models
from django.conf import settings


class Publications(models.Model):

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=u'Пользователь')
    authors = models.TextField(verbose_name=u'Авторы')
    title = models.CharField(primary_key=True, max_length=255, verbose_name=u'Название')
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name=u'Год')
    edition_info = models.TextField(null=True, blank=True, verbose_name=u'Инфо об издании')

    biblio_pokazatel = models.TextField(null=True, blank=True, verbose_name=u'Библиографические показатели')
    annotation = models.TextField(null=True, blank=True, verbose_name="Аннотация")

    elib_id = models.CharField(null=True, blank=True, max_length=255, verbose_name="eLibrary ID")
    doi = models.CharField(null=True, blank=True, max_length=255, verbose_name="DOI")
    cites = models.CharField(null=True, blank=True, max_length=255, verbose_name="Цитируется, кол-во раз")
    isScopusWoS = models.BooleanField(default=False, verbose_name="Входит в базу цитирований Scopus или WoS")

    class Meta:
        verbose_name = u'Публикация'
        verbose_name_plural = u'Публикации'


    def __str__(self):
        return '#' + str(self.authors) + ' ' + str(self.title)