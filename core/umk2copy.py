from .models import Plans, UmkData
from django.utils.timezone import datetime


def umk_copy(src_umk, dst_umk):
    src_data = UmkData.objects.get(umk_id=src_umk)
    dst_data = UmkData.objects.get(umk_id=dst_umk)

    if Plans.objects.get(id=src_data.umk_id.plan_ochka).discipline.name == Plans.objects.get(id=dst_data.umk_id.plan_ochka).discipline.name:
        dst_data.aim = src_data.aim
        dst_data.tasks = src_data.tasks
        dst_data.contentOfSections = src_data.contentOfSections
        dst_data.interdiscipRelations = src_data.interdiscipRelations
        dst_data.table_sections_hour = src_data.table_sections_hour
        dst_data.table_lectures_hour = src_data.table_lectures_hour
        dst_data.table_prakt_hour = src_data.table_prakt_hour
        dst_data.table_laborat_hour = src_data.table_laborat_hour
        dst_data.table_samost_hour = src_data.table_samost_hour
        dst_data.theme_kursovih_rabot = src_data.theme_kursovih_rabot
        dst_data.kursovya_hours = src_data.kursovya_hours
        dst_data.kursovya_semestr = src_data.kursovya_semestr
        dst_data.raschetnograp_work_hours = src_data.raschetnograp_work_hours
        dst_data.raschetnograp_work_semestr = src_data.raschetnograp_work_semestr
        dst_data.table_rating_ochka = src_data.table_rating_ochka
        dst_data.table_rating_zaochka = src_data.table_rating_zaochka
        dst_data.table_literature = src_data.table_literature
        dst_data.material_teh_obespech_dicip = src_data.material_teh_obespech_dicip
        dst_data.database_info_system = src_data.database_info_system
        dst_data.umk_id.status = 'edit'
        dst_data.umk_id.datetime_changed = str(datetime.now())
        dst_data.umk_id.save()
        dst_data.save()


    else:
        return "Discipline not equal"