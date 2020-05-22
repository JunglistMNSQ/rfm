import csv
import re
from datetime import date
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.validators \
    import validate_international_phonenumber as phone_validate
from uuslug import uuslug

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sms_login = models.CharField(blank=True, max_length=50)
    sms_pass = models.TextField(blank=True)
    balance = models.IntegerField(blank=True, default=0)
    notification_msg = models.TextField(blank=True)

    def notification(self, msg):
        self.notification_msg = msg
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class CsvFileHandler(csv.Sniffer):

    def __init__(self, path):
        super(CsvFileHandler, self).__init__()
        self.opened = open(path, 'r')
        self.dialect = self.sniff(self.opened.readline())
        self.opened.seek(0)
        self.file = csv.reader(self.opened, self.dialect)
        self.data = []

    def get_line(self):
        line = self.file.__next__()
        self.data.append(line)
        return line


class HandlerRawData:

    col0 = None
    col1 = None
    col2 = None
    col3 = None
    col4 = None
    order = []

    def __init__(self, obj):
        self.bound_obj = obj
        self.raw_data = []
        self.not_condition_data = []
        self.tab = None
        self.owner = None

    def take_line(self):
        line = self.bound_obj.get_line()
        self.raw_data.append(line)
        return line

    def take_lines(self, n=0):
        while True:
            try:
                self.take_line()
            except StopIteration:
                break
            if len(self.raw_data) == n:
                break
        return self.raw_data

    def parse(self):
        self.take_lines()
        self.col_order()
        for line in self.raw_data:
            try:
                prep_line = {}
                column = 0
                for key in self.order:
                    prep_line[key] = line[column].title()
                    column += 1
                prep_line['owner'] = self.owner
                prep_line['tab'] = self.tab
                prep_line['phone'] = phone_validate(
                    self.phone(prep_line['phone'])
                )
                prep_line['date'] = self.date(prep_line['date'])
                res = Person.get_new_line(prep_line)
                if not res:
                    self.not_condition_data.append(line)
                # return prep_line, self.order, line
            except BaseException:
                self.not_condition_data.append(line)
                # return prep_line, self.order, line
        return True

    def col_order(self):
        col = 0
        while True:
            try:
                hasattr(self, 'col' + str(col))
                self.order.append(getattr(self, 'col' + str(col)))
                col += 1
            except AttributeError:
                break
        return self.order

    def phone(self, phone):
        if re.match(r'\+', phone):
            return phone
        if re.match(r'80', phone) and len(phone) == 11:
            return re.sub(r'80', '+375', phone, count=1)
        else:
            return '+' + phone

    def date(self, date):
        dt = re.findall(r'(\d{2}).(\d{2}).(\d{4})', date)[0]
        return f'{dt[2]}-{dt[1]}-{dt[0]}'


class UserFiles(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField()
    created_at = models.DateTimeField(auto_now=timezone.now())
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,)

    object = models.Manager()

    # def user_directory_path(instance, filename):
    #     return 'user_{0}/{1}'.format(instance.user.id, filename)


class ManageTable(models.Model):
    TAB_WORKS = ((True, 'Таблица активна'),
                 (False, 'Таблица не активна'))

    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,)
    name = models.CharField(max_length=100,
                            verbose_name='Создать новую таблицу',
                            help_text='Введите название',
                            blank=True)
    create_date = models.DateTimeField(default=timezone.now)
    slug = models.CharField(max_length=100)
    on_off = models.BooleanField(default=True,
                                 choices=TAB_WORKS,)

    CHOICE_DURATION = (
        (1, 'Дни'),
        (7, 'Недели'),
        (30, 'Месяцы'),
    )

    choice_rec_1 = models.IntegerField(choices=CHOICE_DURATION,
                                       default=1,)
    choice_rec_2 = models.IntegerField(choices=CHOICE_DURATION,
                                       default=1,)
    recency_raw_1 = models.PositiveIntegerField(null=True,
                                                default=0,)
    recency_raw_2 = models.PositiveIntegerField(null=True,
                                                default=0,)
    recency_1 = models.DurationField(null=True,)
    recency_2 = models.DurationField(null=True,)
    frequency_1 = models.PositiveIntegerField(null=True,
                                              default=0,)
    frequency_2 = models.PositiveIntegerField(null=True,
                                              default=0,)
    monetary_1 = models.PositiveIntegerField(null=True,
                                             default=0,)
    monetary_2 = models.PositiveIntegerField(null=True,
                                             default=0,)

    objects = models.Manager()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super(ManageTable, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('manage_tab', args=[self.slug])

    def rfmizer(self):
        if not self.recency_1:
            return 'Установите настройки RFM.'
        current_date = date.today()
        list_client = Person.objects.filter(table=self)
        for client in list_client:
            r = 100 + 100 * \
                (current_date - client.last_deal < self.recency_1) + \
                100 * (current_date - client.last_deal < self.recency_2)
            f = 10 + 10 * (client.deal_count > self.frequency_1) + \
                10 * (client.deal_count > self.frequency_2)
            m = 1 + 1 * (client.pays > self.monetary_1) + \
                1 * (client.pays > self.monetary_2)
            rfm = str(r + f + m)
            client.rfm_category_update(rfm)
        return 'RFM успешно пересчитан'


class Person(models.Model):
    ACTIVE_CLIENT = ((True, 'Да'),
                     (False, 'Нет'))

    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,)
    slug = models.CharField(max_length=100)
    name = models.TextField()
    phone = PhoneNumberField(validators=[phone_validate])
    last_deal = models.DateField(null=True)
    pays = models.IntegerField(null=True)
    deal_count = models.IntegerField(null=True)
    last_deal_good = models.TextField(null=True)
    rfm_category = models.TextField(default='000')
    active_client = models.BooleanField(choices=ACTIVE_CLIENT,
                                        default=True,)
    tab = models.ForeignKey(ManageTable,
                            on_delete=models.CASCADE,)
    last_sent = models.DateField(null=True)
    rfm_move = models.TextField(default='000000')
    rfm_flag = models.BooleanField(default=False)

    objects = models.Manager()

    @classmethod
    def get_new_line(cls, data):
        obj, create = Person.objects.get_or_create(
            tab=data['tab'],
            owner=data['owner'],
            phone=data['phone'],
            name=data['name']
        )
        obj.save()
        return True

    def rfm_category_update(self, rfm):
        if self.rfm_category != rfm:
            self.rfm_category = rfm
            self.rfm_flag = True
            self.save()
            self.rfm_move_update()

    def rfm_move_update(self):
        if self.rfm_category != self.rfm_move[3:] and self.rfm_flag:
            self.rfm_move = self.rfm_move[3:] + self.rfm_category
            self.save()

    def rfm_flag_update(self, flag):
        self.rfm_flag = flag
        self.save()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.phone

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super(Person, self).save(*args, **kwargs)

    def get_absolute_url(self):
        tab = self.tab
        return reverse('client_card', args=[tab.slug,
                                            self.slug])


class ListDeals(models.Model):
    person = models.ForeignKey(Person,
                               on_delete=models.CASCADE)
    date = models.DateField()
    pay = models.PositiveIntegerField()
    good = models.TextField()

    objects = models.Manager()

