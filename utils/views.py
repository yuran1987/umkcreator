from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.http import Http404, JsonResponse, FileResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from .forms import Convert2File
from .cut2pdf import cut2pdf, copy2tmpfile

def convert2pdf(request): #загрузка учебного плана
    if request.method == 'POST':
        form = Convert2File(request.POST,request.FILES)
        # check whether it's valid:
        if form.is_valid():
            infname = copy2tmpfile(request.FILES['infname'])
            cutfname = copy2tmpfile(request.FILES['cutfname'])
            skip_pages = [int(x)-1 for x in (form.cleaned_data['type']).split(',')]
            print(skip_pages)

            outfname = cut2pdf(infname.name, cutfname.name, skip_pages)

            res = FileResponse(open(outfname.name, 'rb'), content_type='application/pdf')
            res['Content-Disposition'] = 'attachment; filename=result.pdf'
            res['Content-Length'] = len(outfname.read())
            return res
    else:
        form = Convert2File()
    return render(request, 'form_bootstrap.html', {'title': settings.SITE_NAME, 'form': form, 'title_form': "Вырезка/вклейка файлов"})
