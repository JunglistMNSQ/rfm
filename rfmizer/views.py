from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, FormView
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
        table = None
        owner = self.request.user
        cd = form.cleaned_data

        file = Tf.temporary_file_path(cd['file'])
        parser = HandlerRawData(CsvFileHandler(file))
        lines = parser.take_lines(3)
        parser.take_lines()
        if cd['name']:
            print(cd['name'])
            table = form.save(commit=False)
            table.owner = owner
            table.save()
            parser.tab = table
            return super().form_valid(form)

        title = f'Файл загружен и обработан.'
        # if lines[1] and cd['name']:
        #     table.delete()
        #     title = lines[0]
        # elif lines[1] and cd['choice_exist_tab']:
        #     title = lines[0]
        # else:
        #     pass
        parser.tab = cd['choice_exist_tab']
        return redirect('/parse/', parser)


class Parse(LoginRequiredMixin, TemplateView):
    template_name = 'personal/parse.html'


class Log(LoginRequiredMixin, TemplateView):
    template_name = 'personal/log.html'
