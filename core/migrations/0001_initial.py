# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-24 13:20
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('patronymic', models.CharField(max_length=255, null=True, verbose_name='Отчество')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='День рождения')),
                ('position', models.CharField(choices=[['assistant', 'асс.'], ['prepod', 'преп.'], ['starshii_prepodavatel', 'ст.преп.'], ['proffessor', 'проф.'], ['docent', 'доц.'], ['zaf_kaf', 'зав.каф.'], ['io_zaf_kaf', 'И.о. зав.каф.'], ['ved_spec', 'вед.спец.'], ['glav_red', 'гл.ред.'], ['glav_spec', 'гл.спец.'], ['dekan', 'декан'], ['director', 'дир.'], ['zam_dekan', 'зам.дек.'], ['zam_director', 'зам.дир.'], ['konsultant', 'конс.'], ['laborant', 'лаб.'], ['nauch_konsultant', 'науч.конс.'], ['nach_upravleniya', 'нач.упр.'], ['prorector', 'проректор'], ['rector', 'ректор'], ['specialist', 'спец.'], ['starshii_specialist', 'ст.спец.'], ['starshii_laborant', 'ст.лаб.'], ['starshii_tehnik', 'ст.техн.'], ['stajer', 'стажер'], ['tehnik', 'техн.'], ['uch_sekretar', 'уч.секр.'], ['predsedatel_spn', 'председатель СПН']], default='docent', max_length=255, verbose_name='Должность')),
                ('science_stepen', models.CharField(choices=[['k_arhitekturi', 'канд. архитектуры'], ['k_biol_n', 'канд. биол. наук'], ['k_veterinar_n', 'канд. ветеринар. наук'], ['k_voen_n', 'канд. воен. наук'], ['k_geogr_n', 'канд. геогр. наук'], ['k_geol_mineral_n', 'канд. геол.-минерал. наук'], ['k_iskusstvovedeniya', 'канд. искусствоведения'], ['k_ist_n', 'канд. ист. наук'], ['k_kulturologii', 'канд. культурологии'], ['k_med_n', 'канд. мед. наук'], ['k_ped_n', 'канд. пед. наук'], ['k_polit_n', 'канд. полит. наук'], ['k_psihol_n', 'канд. психол. наук'], ['k_sociol_n', 'канд. социол. наук'], ['k_s_h_n', 'канд. с.-х. наук'], ['k_teh_n', 'канд. техн. наук'], ['k_farmacevt_n', 'канд. фармацевт. наук'], ['k_fiz_mat_n', 'канд. физ.-мат. наук'], ['k_filol_n', 'канд. филол. наук'], ['k_filos_n', 'канд. филос. наук'], ['k_him_n', 'канд. хим. наук'], ['k_ekon_n', 'канд. экон. наук'], ['k_yurid_n', 'канд. юрид. наук'], ['d_arhitekturi', 'д-р архитектуры'], ['d_biol_n', 'д-р биол. наук'], ['d_veterinar_n', 'д-р ветеринар. наук'], ['d_voen_n', 'д-р воен. наук'], ['d_geog_n', 'д-р геогр. наук'], ['d_geol_mineral_n', 'д-р геол.-минерал. наук'], ['d_iskusstvovedeniya', 'д-р искусствоведения'], ['d_ist_n', 'д-р ист. наук'], ['d_kulturologii', 'д-р культурологии'], ['d_med_n', 'д-р мед. наук'], ['d_ped_n', 'д-р пед. наук'], ['d_polit_n', 'д-р полит. наук'], ['d_psihol_n', 'д-р психол. наук'], ['d_sociol_n', 'д-р социол. наук'], ['d_s_h_n', 'д-р с.-х. наук'], ['d_tech_n', 'д-р техн. наук'], ['d_farmacevt_n', 'д-р фармацевт. наук'], ['d_fiz_mat_n', 'д-р физ.-мат. наук'], ['d_filol_n', 'д-р филол. наук'], ['d_filos_n', 'д-р филос. наук'], ['d_him_n', 'д-р хим. наук'], ['d_ekon_n', 'д-р экон. наук'], ['d_yurid_n', 'д-р юрид. наук']], default='k_teh_n', max_length=255, verbose_name='Ученая степень')),
                ('science_zvanie', models.CharField(choices=[['docent', 'доцент'], ['proffessor', 'профессор'], ['no', 'без ученого звания']], default='no', max_length=255, verbose_name='Ученое звание')),
                ('electronic_signature', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Электронная подпись')),
            ],
            options={
                'verbose_name_plural': 'Пользователи',
                'verbose_name': 'Пользователь',
                'swappable': 'AUTH_USER_MODEL',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Competence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название компетенции')),
                ('full_content', models.TextField(verbose_name='Содежание компетенции')),
                ('should_know', models.TextField(verbose_name='Должен знать')),
                ('should_able', models.TextField(verbose_name='Должен уметь')),
                ('should_master', models.TextField(verbose_name='Должен владеть')),
                ('training_program', models.CharField(choices=[['Academic', 'академического'], ['Applied', 'прикладного']], max_length=30, verbose_name='Программа обучения')),
                ('qualif', models.CharField(choices=[['specialist', 'специалист'], ['bachelor', 'бакалавр'], ['engineer', 'инженер'], ['master', 'магистр']], default='Bachelor', max_length=12, verbose_name='Квалификация')),
            ],
            options={
                'verbose_name_plural': 'Список компетенций',
                'verbose_name': 'Компетенции',
            },
        ),
        migrations.CreateModel(
            name='Departaments',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Название кафедры')),
            ],
            options={
                'verbose_name_plural': 'Список кафедр',
                'verbose_name': 'Кафедры',
            },
        ),
        migrations.CreateModel(
            name='Directions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название направления')),
                ('code', models.CharField(max_length=60, verbose_name='Код направления')),
                ('number_prikaz', models.PositiveIntegerField(default=1, verbose_name='№ приказа')),
                ('date_prikaz', models.DateField(default=datetime.datetime.today, verbose_name='Дата приказа')),
                ('deparmt', models.ForeignKey(help_text='Название кафедры за которой закрепляется направление', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Departaments', verbose_name='Кафедра')),
            ],
            options={
                'verbose_name_plural': 'Список направлений обучения',
                'verbose_name': 'Направления',
            },
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название дисциплины', max_length=255, verbose_name='Дисциплина')),
            ],
            options={
                'verbose_name_plural': 'Список дисциплин',
                'verbose_name': 'Дисциплина',
            },
        ),
        migrations.CreateModel(
            name='Plans',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_OPOP', models.CharField(max_length=15, verbose_name='Код ОПОП')),
                ('training_form', models.CharField(choices=[['fulltime', 'Очное(4 года)'], ['extramural', 'Заочная (5 лет)'], ['parttime', 'Заочная (3.5 года)']], default='fulltime', max_length=20, verbose_name='Формы обучения')),
                ('qualif', models.CharField(choices=[['specialist', 'специалист'], ['bachelor', 'бакалавр'], ['engineer', 'инженер'], ['master', 'магистр']], max_length=12, verbose_name='Квалификация')),
                ('training_program', models.CharField(choices=[['Academic', 'академического'], ['Applied', 'прикладного']], max_length=30, verbose_name='Программа обучения')),
                ('year', models.IntegerField(default=2018, verbose_name='Год набора')),
                ('semestr', models.CharField(default='1', max_length=15, verbose_name='Семестр')),
                ('trudoemkost_all', models.PositiveIntegerField(default=1, verbose_name='Общая трудоемкость, часов')),
                ('trudoemkost_zachot_edinic', models.IntegerField(default=1, null=True, verbose_name='Количество зачетных единиц')),
                ('hours_audit_work_sum', models.PositiveIntegerField(default=1, verbose_name='Количество аудиторной работы, час')),
                ('hours_lectures', models.PositiveIntegerField(default=0, verbose_name='на лекции,час')),
                ('hours_pract', models.PositiveIntegerField(default=0, verbose_name='на практические работы,часов')),
                ('hours_labs', models.PositiveIntegerField(default=0, verbose_name='на лабораторные работы,часов')),
                ('hours_samost_work_sum', models.PositiveIntegerField(default=1, verbose_name='Общее количество самостоятельной работы,часов')),
                ('hours_samost_wo_lec', models.FloatField(default=1, verbose_name='Самостоятельная работа студента без преподавателя, часов')),
                ('hours_samost_w_lec_w_stud', models.FloatField(default=1, verbose_name='Самостоятельная работа студентов с преподавателем, часов')),
                ('hours_samost_w_lec_w_group', models.FloatField(default=1, verbose_name='Самостоятельная работа группы с преподавателем, часов')),
                ('exam_semestr', models.CharField(blank=True, help_text='Формат: 1,2', max_length=10, null=True, verbose_name='Экзамен в семестре')),
                ('zachot_semestr', models.CharField(blank=True, help_text='Формат: 1,2', max_length=10, null=True, verbose_name='Зачет в семестре')),
                ('kursovya_work_project', models.CharField(max_length=15, null=True, verbose_name='КП/КР')),
                ('kontrolnaya_work', models.CharField(help_text='заполняется только для заочников', max_length=15, null=True, verbose_name='Контрольная работа')),
                ('zanatiya_in_interak_forms_hours', models.PositiveIntegerField(default=1, null=True, verbose_name='Занятия в интерактивной форме, часов')),
                ('comps', models.TextField(blank=True, null=True, verbose_name='Компетенции')),
                ('direction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Directions', verbose_name='Направление')),
                ('discipline', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Discipline', verbose_name='Название дисциплины')),
            ],
            options={
                'verbose_name_plural': 'Список учебных планов',
                'verbose_name': 'Учебный план',
            },
        ),
        migrations.CreateModel(
            name='Profiles',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Название профиля')),
                ('direction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Directions', verbose_name='Название направления')),
            ],
            options={
                'verbose_name_plural': 'Профили обучения',
                'verbose_name': 'Профиль',
            },
        ),
        migrations.CreateModel(
            name='UmkArticles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_ochka', models.PositiveIntegerField(null=True, verbose_name='Учебный план для очн.ф.обуч.')),
                ('plan_z', models.PositiveIntegerField(null=True, verbose_name='Учебный план для заоч.ф.обуч.')),
                ('plan_zu', models.PositiveIntegerField(null=True, verbose_name='Учебный план для заоч.-уск.ф.обуч.')),
                ('datetime_created', models.DateTimeField(verbose_name='Дата создания')),
                ('kursovya_hours', models.PositiveIntegerField(default=0, null=True, verbose_name='Количество часов на курсовую работу,часов')),
                ('kursovya_semestr', models.PositiveIntegerField(default=0, null=True, verbose_name='Номер cеместра на курсовую')),
                ('raschetnograp_work_hours', models.PositiveIntegerField(default=0, null=True, verbose_name='Количество часов на расчетно-графическую работу, часов')),
                ('raschetnograp_work_semestr', models.PositiveIntegerField(default=0, null=True, verbose_name='Номер семестра на расчетно-графическую работу')),
                ('status', models.CharField(choices=[['OK', 'Подписана'], ['edit', 'Наполнение'], ['empty', 'Пустая']], default='empty', max_length=50, verbose_name='Статус')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name_plural': 'Рабочие программы',
                'verbose_name': 'Рабочая программа',
            },
        ),
        migrations.CreateModel(
            name='UmkData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aim', models.TextField(verbose_name='Цель дисциплины')),
                ('tasks', models.TextField(verbose_name='Задачи дисциплины')),
                ('placeInStruct', models.TextField(verbose_name='Место дисциплины в структуре ОПОП')),
                ('contentOfSections', models.TextField(null=True, verbose_name='Содержание разделов и тем дисциплины')),
                ('interdiscipRelations', models.TextField(null=True, verbose_name='Междисциплинарные связи c обеспециваемыми дисциплины')),
                ('table_sections_hour', models.TextField(null=True, verbose_name='Разделы (модули), темы дисциплин ви виды занятий')),
                ('table_lectures_hour', models.TextField(null=True, verbose_name='Перечень лекционных занятий')),
                ('table_prakt_hour', models.TextField(blank=True, null=True, verbose_name='Перечень практических занятий')),
                ('table_laborat_hour', models.TextField(blank=True, null=True, verbose_name='Перечень лабораторных занятий')),
                ('table_samost_hour', models.TextField(null=True, verbose_name='Перечень самостоятельных занятий')),
                ('theme_kursovih_rabot', models.TextField(blank=True, null=True, verbose_name='Примерная тематика курсовых проектов (работ)')),
                ('table_rating_ochka', models.TextField(blank=True, null=True, verbose_name='Рейтинговая система оценки для очников')),
                ('table_rating_zaochka', models.TextField(blank=True, null=True, verbose_name='Рейтинговая система оценки для заочников')),
                ('table_literature', models.TextField(blank=True, null=True, verbose_name='Список литературы')),
                ('material_teh_obespech_dicip', models.TextField(verbose_name='Материально-техническое обеспечение дисциплины')),
                ('database_info_system', models.TextField(null=True, verbose_name='Базы данных, информационно-справочные и поисковые системы')),
                ('umk_id', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.UmkArticles', verbose_name='ID рабочей программы')),
            ],
            options={
                'verbose_name_plural': 'Данные раб.программ',
                'verbose_name': 'Данные раб.программы',
            },
        ),
        migrations.CreateModel(
            name='Units',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Подразделение университета')),
                ('city', models.CharField(default='Сургут', max_length=255, verbose_name='Населеный пункт')),
            ],
            options={
                'verbose_name_plural': 'Список подразделений университета',
                'verbose_name': 'Подразделение',
            },
        ),
        migrations.CreateModel(
            name='Univercity',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Название университета')),
                ('ministerstvo', models.CharField(default='Министерство науки и высшего образования РФ', max_length=255, verbose_name='Министерство')),
            ],
            options={
                'verbose_name_plural': 'Список университетов',
                'verbose_name': 'Университет',
            },
        ),
        migrations.AddField(
            model_name='units',
            name='univer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Univercity', verbose_name='Название университета'),
        ),
        migrations.AddField(
            model_name='plans',
            name='profile',
            field=models.ManyToManyField(to='core.Profiles', verbose_name='Профиль'),
        ),
        migrations.AddField(
            model_name='departaments',
            name='units',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Units', verbose_name='Название подразделения'),
        ),
        migrations.AddField(
            model_name='competence',
            name='direction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Directions', verbose_name='Название направления'),
        ),
        migrations.AddField(
            model_name='user',
            name='deparmt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Departaments', verbose_name='Кафедра'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
