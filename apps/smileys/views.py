from django.shortcuts import render
from django.http import HttpResponseRedirect
import csv
from .forms import Uploading
from .models import Smiley
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def home(request):
    form = Uploading()
    if request.method == 'POST': # If the form has been submitted...
        form = Uploading(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES['import_file'].name.find('.csv') > 0:
                dataReader = csv.reader( request.FILES['import_file'], delimiter=',', quotechar='"')
                for r in dataReader:
                    try:
                        smile = Smiley.objects.get(pattern=r[0])
                        smile.description = r[1]
                        smile.image = r[2]
                        smile.save()
                    except ObjectDoesNotExist:
                        smile = Smiley()
                        smile.pattern = r[0]
                        smile.description = r[1]
                        smile.image = r[2]
                        smile.save()
            return HttpResponseRedirect('/')

    return render(request, 'smileys/import.html', {
        'form': form})


