import re, numpy


TRANING_PROGRAMS = (['Academic', u'академического'],['Applied', u'прикладного'])
QUALIFICATION_VALUES = (['specialist', u'специалист'],
                        ['bachelor', u'бакалавр'],
                        ['engineer',u'инженер'],
                        ['master',u'магистр'],
                        )

FORMS_CONTROL = ['Выполнение контрольной работы',   #Виды контроля
                 'Выступление (доклад) на занятии',
                 'Домашнее задание',
                 'Защита отчета',
                 'Коллоквиум',
                 'Конспект самоподготовки',
                 'Консультирование',
                 'Контрольная работа',
                 'Опрос на занятиях',
                 'Отчет по ГПО',
                 'Отчет по индивидуальному заданию',
                 'Отчет по курсовому проекту / курсовой работе',
                 'Отчет по лабораторной работе',
                 'Отчет по практическому занятию',
                 'Проверка контрольных работ',
                 'Расчетная работа',
                 'Реферат',
                 'Собеседование',
                 'Тестирование']

TYPE_SAMOSTOYATELNOY_RABORY = [ #Название темы самостоятельной работы
    'Выполнение домашних заданий',
    'Выполнение индивидуальных заданий',
    'Выполнение контрольных работ',
    'Выполнение курсового проекта / курсовой работы',
    'Выполнение расчетных работ',
    'Выполнение расчетно-графических домашних работ',
    'Выполнение переводов с иностранных языков',
    'Консультация по курсовому проекту/работе',
    'Консультация по ВКР',
    'Консультация по научно-исследовательской деятельности обучающегося',
    'Написание рефератов',
    'Научные исследования обучающегося',
    'Оформление отчетов по лабораторным работам',
    'Оформление заявок на объекты интелектуальной собственности',
    'Подготовка и написание отчета по практике',
    'Подготовка к экзамену',
    'Подготовка к зачету',
    'Подготовка к коллоквиуму',
    'Подготовка к контрольным работам',
    'Подготовка к лабораторным работам',
    'Подготовка к практическим занятиям',
    'Подготовка к докладу',
    'Подготовка публикаций по результатам научных исследований обучающегося',
    'Подготовка к олимпиаде',
    'Подготовка к конкурсу',
    'Подготовка к аттестации',
    'Представление отчета по практике к защите',
    'Проработка лекционного материала',
    'Просмотр учебных кинофильмов, видеозаписей',
    'Работа на ПК',
    'Решение задач и упражнений',
    'Самостоятельное изучение тем (вопросов) теоретической части курса',
    'Самотестирование по контрольным вопросам (тестам)',
    'Итого:'

]

METHODS_TEACHER = [  #Методы преподавания лекций
'словесный',
'наглядный', 'иллюстративный',
'словесно-наглядный',
'индуктивный/дедуктивный',
'репродуктивный',
'проблемно-поисковый',
'интерактивные',
'разбор практических ситуаций',
'работа в малых группах'
]


TYPE_CONTROL_RATING = [ #виды контрольных мероприятий в рейтинге
     'Тестирование по лекционному материалу',
     'Работа на лекциях',
     'Выполнение лабораторной работы',
     'Выполнение практической работы',
     'Отчет по лабораторной работе',
     'Отчет по практической работе',
     'Работа на практическом занятии',
     'Тестовое решение задач',
     'Самостоятельная работа',
     'Выполнение контрольной работы',
     'Выступление (доклад) на занятии',
     'Домашнее задание',
     'Защита отчета',
     'Отчет по индивидуальному заданию',
     'Отчет по курсовому проекту / курсовой работе',
     'Реферат',
     'Участие в олимпиаде/конкурсе',
     'Призовое место в олимпиаде/конкурсе',
     'Итого за 1-ую аттестацию',
     'Итого за 2-ую аттестацию',
     'Итого за 3-ую аттестацию'
]


def isNone(val):
    if not val:
        res = ''
    else:
        res = val
    return res

def getSemestrs_2d(v1,v2):
    sss = str(v1) + "," + str(v2)
    return getSemestrs_1d(sss)

def getSemestrs_1d(v1):
    if v1:
        if len(v1)>0:
            sss = str(v1)
            res = sum((i if len(i)==1 else list(range(i[0], i[1]+1))
                        for i in ([int(j) for j in i if j] for i in
                                re.findall('(\d+),?(?:-(\d+))?',sss))),[])

            res = str(res).replace("[","").replace("]","")
            return ",".join(list(map(str,sorted(list(map(int,res.split(",")))))))
    else:
        return ''

def remove_dublicates(x): #удаление дубликатов строк
    a = []
    for i in x:
        if i not in a:
            a.append(i)
    return a

def remove_quotes(x):
    res = str(x).replace('"','')
    return res

def previous_and_next_disciplines_from_umk(pl_ochka, Plans): #формирование списка предыдущих и последующих дисциплин
    num_semestr_ochka = numpy.sort(numpy.array(list(map(int, pl_ochka.semestr.split(",")))))
    comps = set(pl_ochka.comps.strip().split(" "))

    next_disciplines = set()
    previous_disciplines = set()


    for tmp in Plans.objects.filter(direction = pl_ochka.direction, training_form='fulltime', training_program = pl_ochka.training_program, year=pl_ochka.year):
        if (set(pl_ochka.profile.get_queryset()) == set(tmp.profile.get_queryset())) and (tmp.discipline!=pl_ochka.discipline):
            a = sorted(set(map(int, tmp.semestr.split(','))))
            res = comps & set(tmp.comps.strip().split(" "))
            #print(res, "  ", tmp.discipline, "  =",tmp.comps, "=",tmp.comps.split(" "))
            if res:
                for i in a:
                    if numpy.greater(i,num_semestr_ochka).all(): #сравнение чтобы i больше всех элементов из num_semestr_ochka
                        #print("next: {0} {1} {2}".format(tmp.comps.lstrip(), tmp.discipline.name.lstrip(), a))
                        next_disciplines.add(tmp)
                    elif numpy.less(i,num_semestr_ochka).all(): #сравнение чтобы i меньше всех элементов из num_semestr_ochka
                        #print("prev: {0} {1} {2}".format(tmp.comps.lstrip(), tmp.discipline.name.lstrip(), a))
                        previous_disciplines.add(tmp)

    data = {'next_disciplines': list(next_disciplines),
            'previous_disciplines': list(previous_disciplines)}

    return data


def getTotalstr(semestrs, list_foradd): #Формирование списка надписей количества часов или баллов за семестр

    sem_ochka = sorted(list(map(int,semestrs[0].split(","))))
    res_ochka = []
    if len(sem_ochka)>1:
        for id in sem_ochka:
            res_ochka.append("Всего за {0} семестр:".format(id))

    res_ochka.append("Всего:")

    #Для заочки
    sem_z = sorted(list(map(int, semestrs[1].split(","))))
    sem_zu = sorted(list(map(int, semestrs[2].split(","))))

    res_z = []
    if (len(sem_z)==len(sem_zu)) and (len(sem_z)>1 and len(sem_zu)>1):
        for i in range(0,len(sem_z)):
            res_z.append("Всего за {0}/{1} семестр:".format(sem_z[i],sem_zu[i]))

    res_z.append("Всего:")

    list_ochka = list_foradd.copy()
    list_z = list_foradd.copy()

    for id in res_ochka:
        list_ochka.append(id)

    for id in res_z:
        list_z.append(id)


    return {'ochka': list_ochka, 'zaochka': list_z}