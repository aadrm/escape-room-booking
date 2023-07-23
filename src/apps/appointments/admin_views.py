from django.shortcuts import render
from .forms import SlotCreationForm


def add_many_slots(request):

    return render(request, 'admin/change_form.html')
