from django.shortcuts import redirect, render
from django.urls import reverse

from ..view.models import Description

from .forms import AddForm

def add(request):
    form = AddForm()
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            stream = form.save()
            Description.objects.create(stream=stream, description=form.cleaned_data["description"])
            return redirect(reverse('add:index'))
    
    return render(request, 'add/add.html', context={'form': form})
