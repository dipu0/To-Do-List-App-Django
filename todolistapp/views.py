from typing import Any, Dict
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .models import Task
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from django.views import View
from django.db import transaction
from .forms import PositionForm

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'todolistapp/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name='todolistapp/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('task')
        return super(RegisterPage, self).get(*args, **kwargs)

class TaskList(LoginRequiredMixin, ListView): 
    model = Task
    context_object_name = 'tasks'
    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['tasks'] = contex['tasks'].filter(user=self.request.user)
        contex['count'] = contex['tasks'].filter(complete=False)
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            contex['tasks'] = contex['tasks'].filter(
                title__startswith=search_input
            )
        return contex

class TaskDetail(LoginRequiredMixin, DetailView): 
    model = Task
    context_object_name = 'task'
    template_name = 'todolistapp/task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('tasks')

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))