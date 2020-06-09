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
from django.forms.models import modelform_factory



# Create your views here.


def main(request):
    return render(request,
                  'index.html')


# class GetTabMixin():
#     tab = None
#
#     def get_tab(self):
#         if self.tab is None:
#             slug = self.kwargs['tab_slug'] or self.kwargs['slug']
#             return ManageTable.objects.get(slug=slug)
#


class Register(CreateView):
    template_name = 'registration/registration.html'
    success_url = '/login/'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        if form.clean_password2():
            cd = form.cleaned_data
            new_user = form.save()
            new_user.set_password(cd['password'])
            new_user.save()
            return HttpResponseRedirect(self.success_url)





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
        corrupt_data = parser.parse()
        file.delete()
        if corrupt_data:
            self.request.session['data'] = corrupt_data
            return redirect('/corrupt_data/')
        return super(Parse, self).form_valid(form)
    
    def get_success_url(self):
        tab = ManageTable.objects.get(pk=self.request.session['tab'])
        return reverse('manage_tab', kwargs={'slug': tab.slug})


class CorruptData(LoginRequiredMixin, ListView):
    template_name = 'personal/corrupt_data.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = self.request.session['data']
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CorruptData, self).get_context_data()
        tab = ManageTable.objects.get(pk=self.request.session['tab'])
        context['tab'] = tab
        return context


class MyTables(LoginRequiredMixin, ListView):
    template_name = 'personal/my_tables.html'
    model = ManageTable

    def get_context_data(self, **kwargs):
        context = super(MyTables, self).get_context_data()
        context['list_tab'] = ManageTable.objects.filter(
            owner=self.request.user
        )
        return context


class ManageTab(LoginRequiredMixin, DetailView, UpdateView):
    template_name = 'personal/manage.html'
    model = ManageTable
    fields = ['choice_rec_1', 'choice_rec_2',
              'recency_raw_1', 'recency_raw_2',
              'frequency_1', 'frequency_2',
              'monetary_1', 'monetary_2',
              'on_off'
              ]
    widgets = {
        'recency_raw_1': TextInput,
        'recency_raw_2': TextInput,
        'frequency_1': TextInput,
        'frequency_2': TextInput,
        'monetary_1': TextInput,
        'monetary_2': TextInput,
        'on_off': RadioSelect(attrs={'id': 'on_off'})}


class ClientList(LoginRequiredMixin, ListView):
    template_name = 'personal/client_list.html'
    model = Person
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        tab = ManageTable.objects.get(slug=self.kwargs.get('slug'))
        context = super(ClientList, self).get_context_data()
        context['tab'] = tab
        context['obj_list'] = Person.objects.filter(tab=tab)
        return context


class ClientCard(LoginRequiredMixin, DetailView, UpdateView):
    model = Person
    template_name = 'personal/client_card.html'
    fields = ['phone', 'active_client']

    def get_context_data(self, *, object_list=None, **kwargs):
        tab = ManageTable.objects.get(slug=self.kwargs['slug_tab'])
        client = Person.objects.get(slug=self.kwargs['slug'])
        context = super(ClientCard, self).get_context_data()
        context['tab'] = tab
        context['object'] = client
        context['obj_list'] = Deals.objects.filter(person=client)
        return context


class RulesList(LoginRequiredMixin, ListView):
    model = Rules
    template_name = 'personal/rules.html'

    def get_queryset(self):
        qs = super(RulesList, self).get_queryset()
        return qs.filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RulesList, self).get_context_data()
        context['tab'] = ManageTable.objects.get(
            slug=self.kwargs['slug']
        )
        return context


class NewRule(LoginRequiredMixin, CreateView):
    model = Rules
    template_name = 'personal/new_rule.html'
    fields = ['name', 'from_to', 'message', 'on_off_rule']
    widgets = {'on_off_rule': RadioSelect(attrs={'id': 'on_off'}),
               'from_to': CheckboxSelectMultiple}

    def get_context_data(self, **kwargs):
        context = super(NewRule, self).get_context_data()
        context['tab'] = ManageTable.objects.get(
            slug=self.kwargs['slug']
        )
        return context

    def get_form_class(self):
        super(NewRule, self).get_form_class()
        return modelform_factory(self.model,
                                 fields=self.fields,
                                 widgets=self.widgets)
    
    def form_valid(self, form):
        tab = ManageTable.objects.get(slug=self.kwargs.get('slug'))
        owner = self.request.user
        rule = form.save(commit=False)
        rule.owner = owner
        rule.tab = tab
        rule.save()
        return super(NewRule, self).form_valid(form)


class EditRule(LoginRequiredMixin, UpdateView):
    model = Rules
    template_name = 'personal/rule.html'
    fields = ['name', 'from_to', 'message', 'on_off_rule']
    widgets = {'on_off_rule': RadioSelect(attrs={'id': 'on_off'}),
               'from_to': CheckboxSelectMultiple}

    def get_form_class(self):
        super(EditRule, self).get_form_class()
        return modelform_factory(self.model,
                                 fields=self.fields,
                                 widgets=self.widgets)

    def get_context_data(self, **kwargs):
        context = super(EditRule, self).get_context_data()
        context['tab'] = ManageTable.objects.get(
            slug=self.kwargs['slug_tab']
        )
        return context


class Delete(LoginRequiredMixin, DeleteView):
    template_name = 'personal/del.html'
    model = ManageTable
    success_url = '/my_tables'
    
    def get_object(self, queryset=None):
        return super(Delete, self).get_object()


class Log(LoginRequiredMixin, TemplateView):
    template_name = 'personal/log.html'
