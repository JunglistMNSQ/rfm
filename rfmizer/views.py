from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelform_factory
from django.forms import TextInput, RadioSelect, CheckboxSelectMultiple
from django.shortcuts import redirect, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, DeleteView, \
    FormView, ListView, UpdateView
from .forms import ParserForm, ProfileForm, UserRegistrationForm, \
    CreateOrUpdateTable
from .sms import RocketSMS
from .models import ActionLog, CsvFileHandler, HandlerRawData, \
    Person, Rules, Tab, UserFiles, User
import hashlib


# Create your views here.


class GetMyContextMixin:
    def get_tab(self):
        slug = self.kwargs.get('slug_tab') or self.kwargs.get('slug')
        return Tab.objects.get(slug=slug)

    def get_message(self):
        try:
            msg = self.request.session.pop('msg')
        except KeyError:
            return None
        return msg

    def file_read_n_parse(self):
        file = UserFiles.object.get(pk=self.request.session['file'])
        reader = CsvFileHandler(file.file.path)
        return HandlerRawData(reader)


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


class ProfileView(LoginRequiredMixin, GetMyContextMixin, UpdateView):
    template_name = 'personal/profile.html'
    model = User
    form_class = ProfileForm
    success_url = '/profile/'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data()
        context['msg'] = self.get_message()
        return context

    def form_valid(self, form):
        cd = form.cleaned_data
        self.object.sms_login = cd['sms_login']
        self.object.sms_pass = hashlib.md5(
            cd['sms_pass'].encode('utf-8')
        ).hexdigest()
        balance = RocketSMS.check_balance(cd['sms_login'],
                                          self.object.sms_pass)
        self.object.balance = balance[1]
        self.object.save()
        self.request.session['msg'] = balance[2]
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


class Parse(GetMyContextMixin, LoginRequiredMixin, FormView):
    template_name = 'personal/parse.html'
    form_class = ParserForm

    def get_context_data(self, **kwargs):
        context = super(Parse, self).get_context_data()
        parser = self.file_read_n_parse()
        context['lines'] = parser.take_lines(3)
        return context

    def form_valid(self, form):
        parser = self.file_read_n_parse()
        cd = form.cleaned_data
        col = 0
        order = []
        while True:
            try:
                order.append(cd['col' + str(col)])
                col += 1
            except KeyError:
                break
            finally:
                parser.order = order
        parser.owner = self.request.user
        tab = Tab.objects.get(pk=self.request.session['tab'])
        parser.tab = tab
        corrupt_data = parser.parse()
        self.request.user.files.get(
            pk=self.request.session.pop('file')
        ).delete()
        if corrupt_data:
            self.request.session['data'] = corrupt_data
            return redirect('/corrupt_data/')
        return super(Parse, self).form_valid(form)

    def get_success_url(self):
        tab = Tab.objects.get(pk=self.request.session['tab'])
        return reverse('manage_tab', kwargs={'slug': tab.slug})


class CorruptData(LoginRequiredMixin, GetMyContextMixin, ListView):
    template_name = 'personal/corrupt_data.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = self.request.session['data']
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CorruptData, self).get_context_data()
        tab = Tab.objects.get(pk=self.request.session['tab'])
        context['tab'] = tab
        return context


class MyTables(LoginRequiredMixin, ListView):
    template_name = 'personal/my_tables.html'
    context_object_name = 'list_tab'

    def get_queryset(self):
        return self.request.user.tabs.all()


class ManageTab(LoginRequiredMixin, GetMyContextMixin, UpdateView):
    model = Tab
    template_name = 'personal/manage.html'
    fields = [
        'choice_rec_1', 'choice_rec_2',
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
        'on_off': RadioSelect(attrs={'id': 'on_off'})
    }

    def get_form_class(self):
        return modelform_factory(self.model,
                                 fields=self.fields,
                                 widgets=self.widgets, )

    def form_valid(self, form):
        tab = form.save()
        tab.recency_calc()
        self.request.session['msg'] = tab.rfmizer()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ManageTab, self).get_context_data()
        context['msg'] = self.get_message()
        return context


class ClientList(LoginRequiredMixin, GetMyContextMixin, ListView):
    template_name = 'personal/client_list.html'
    model = Person
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ClientList, self).get_context_data()
        tab = self.get_tab()
        context['tab'] = tab
        context['clients'] = tab.clients.all()
        return context


class ClientCard(LoginRequiredMixin,
                 GetMyContextMixin,
                 DetailView,
                 UpdateView):
    model = Person
    template_name = 'personal/client_card.html'
    fields = ['phone', 'active_client']

    def get_context_data(self, *, object_list=None, **kwargs):
        client = Person.objects.get(slug=self.kwargs['slug'])
        context = super(ClientCard, self).get_context_data()
        context['tab'] = self.get_tab()
        context['client'] = client
        context['deals'] = client.deals.all()
        return context


class RulesList(LoginRequiredMixin, GetMyContextMixin, ListView):
    model = Rules
    template_name = 'personal/rules.html'

    def get_queryset(self):
        return self.get_tab().rules.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RulesList, self).get_context_data()
        context['tab'] = self.get_tab()
        return context


class NewRule(LoginRequiredMixin, GetMyContextMixin, CreateView):
    model = Rules
    template_name = 'personal/new_rule.html'
    fields = ['name', 'from_to', 'message','on_off_rule']
    widgets = {'on_off_rule': RadioSelect(attrs={'id': 'on_off'}),
               # 'time_to_run': RadioSelect(attrs={'id': 'time_to_run'}),
               # 'days': CheckboxSelectMultiple,
               'from_to': CheckboxSelectMultiple}

    def get_context_data(self, **kwargs):
        context = super(NewRule, self).get_context_data()
        context['tab'] = self.get_tab()
        return context

    def get_form_class(self):
        return modelform_factory(self.model,
                                 fields=self.fields,
                                 widgets=self.widgets)

    def form_valid(self, form):
        tab = self.get_tab()
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
        return modelform_factory(self.model,
                                 fields=self.fields,
                                 widgets=self.widgets)

    def get_context_data(self, **kwargs):
        context = super(EditRule, self).get_context_data()
        context['tab'] = Tab.objects.get(
            slug=self.kwargs['slug_tab']
        )
        return context


class Delete(LoginRequiredMixin, DeleteView):
    template_name = 'personal/del.html'
    model = Tab
    success_url = '/my_tables'

    def get_object(self, queryset=None):
        return super(Delete, self).get_object()


class Log(LoginRequiredMixin, ListView):
    template_name = 'personal/log.html'
    model = ActionLog
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.events.all()
