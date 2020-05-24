from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import *
from .forms import *
from django.contrib.auth import authenticate, login
from django.core.files.uploadedfile import TemporaryUploadedFile as Tf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render, HttpResponseRedirect
import hashlib
from .models import *


# Create your views here.


def main(request):
    return render(request,
                  'index.html')


class Register(CreateView):
    models = User
    template_name = 'registration/registration.html'
    success_url = '/login/'
    form_class = UserRegistrationForm


class Upload(LoginRequiredMixin, CreateView):
    template_name = 'personal/upload.html'
    success_url = '/parse/'
    form_class = CreateOrUpdateTable

    def get_form_kwargs(self):
        kwargs = super(Upload, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        return kwargs

    def form_valid(self, form):
        owner = self.request.user
        cd = form.cleaned_data
        new_file = UserFiles(file=cd['file'], owner=owner)
        new_file.save()
        self.request.session['file'] = new_file.pk
        if cd['name']:
            print(cd['name'])
            tab = form.save(commit=False)
            tab.owner = owner
            tab.save()
            self.request.session['tab'] = tab.pk
            self.request.session['tab_is_new'] = True
            return super().form_valid(form)
        else:
            tab = cd['choice_exist_tab']
            self.request.session['tab'] = tab.pk
            self.request.session['tab_is_new'] = False
            return redirect('/parse/')


class Parse(LoginRequiredMixin, FormView):
    template_name = 'personal/parse.html'
    form_class = ParserForm

    def get_context_data(self, **kwargs):
        context = super(Parse, self).get_context_data()
        file = UserFiles.object.get(pk=self.request.session['file'])
        reader = CsvFileHandler(file.file.path)
        parser = HandlerRawData(reader)
        context['lines'] = parser.take_lines(3)
        return context

    def form_valid(self, form):
        # tab_is_new = self.request.session['tab_is_new']
        file = UserFiles.object.get(pk=self.request.session['file'])
        reader = CsvFileHandler(file.file.path)
        parser = HandlerRawData(reader)
        cd = form.cleaned_data
        col = 0
        order = []
        while True:
            try:
                order.append(cd['col' + str(col)])
                # setattr(parser, 'col' + str(col), value)
                col += 1
            except KeyError:
                break
            finally:
                parser.order = order
        parser.owner = self.request.user
        tab = ManageTable.objects.get(pk=self.request.session['tab'])
        parser.tab = tab
        parser.parse()
        file.delete()
        return super(Parse, self).form_valid(form)
    
    def get_success_url(self):
        tab = ManageTable.objects.get(pk=self.request.session['tab'])
        return reverse('manage_tab', kwargs={'slug': tab.slug})


class MyTables(LoginRequiredMixin, ListView):
    template_name = 'personal/my_tables.html'
    model = ManageTable

    def get_context_data(self, **kwargs):
        context = super(MyTables, self).get_context_data()
        list_tab = ManageTable.objects.filter(owner=self.request.user)
        context['list_tab'] = list_tab
        return context


class ManageTab(LoginRequiredMixin, DetailView):
    template_name = 'personal/manage.html'
    model = ManageTable


class Delete(LoginRequiredMixin, DeleteView):
    template_name = 'personal/del.html'


class Log(LoginRequiredMixin, TemplateView):
    template_name = 'personal/log.html'
