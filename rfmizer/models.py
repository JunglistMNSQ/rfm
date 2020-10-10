import csv
import re
from datetime import date, timedelta
from django.contrib.auth.models import User
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
    balance = models.IntegerField(blank=True, null=True, default=0)
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
        if len(self.data) == 0:
            line = self.bom_replace(line)
        self.data.append(line)
        return line

    def bom_replace(self, line):
        if line[0].startswith('\ufeff'):
            line[0] = line[0].replace('\ufeff', '')
        return line


class HandlerRawData:
    def __init__(self, obj):
        self.bound_obj = obj
        self.raw_data = []
        self.not_condition_data = []
        self.tab = None
        self.owner = None
        self.order = None

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
        count = 0
        for line in self.raw_data:
            count += 1
            try:
                prep_line = {}
                col = 0
                for key in self.order:
                    prep_line[key] = line[col]
                    col += 1
                prep_line['owner'] = self.owner
                prep_line['tab'] = self.tab
                Person.get_new_line(prep_line)
            except Exception:
                self.not_condition_data.append((count, line))
        if self.not_condition_data:
            return self.not_condition_data
        else:
            return False


class UserFiles(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField()
    created_at = models.DateTimeField(auto_now=timezone.now())
    owner = models.ForeignKey(User,
                              related_name='files',
                              on_delete=models.CASCADE,)

    object = models.Manager()


class Tab(models.Model):
    TAB_WORKS = ((True, 'Таблица активна'),
                 (False, 'Таблица не активна'))

    name = models.CharField(max_length=100,
                            verbose_name='Создать новую таблицу',
                            help_text='Введите название',
                            blank=True)
    owner = models.ForeignKey(User,
                              related_name='tabs',
                              on_delete=models.CASCADE, )
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
        return f'Таблица {self.name}, создана {self.create_date:%d.%m.%y}.'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super(Tab, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('manage_tab', args=[self.slug])

    def recency_calc(self):
        self.recency_1 = timedelta(
            days=(self.recency_raw_1 * self.choice_rec_1)
        )
        self.recency_2 = timedelta(
            days=(self.recency_raw_2 * self.choice_rec_2)
        )
        self.save()
        return True

    def rfmizer(self):
        if self.recency_1 and self.recency_2:
            current_date = date.today()
            list_client = Person.objects.filter(tab=self)
            for client in list_client:
                r = 100 + 100 * \
                    ((current_date - client.last_deal) < self.recency_1) + \
                    100 * ((current_date - client.last_deal) < self.recency_2)
                f = 10 + 10 * (client.deal_count > self.frequency_1) + \
                    10 * (client.deal_count > self.frequency_2)
                m = 1 + 1 * (client.pays > self.monetary_1) + \
                    1 * (client.pays > self.monetary_2)
                rfm = str(r + f + m)
                client.rfm_category_update(rfm)
            return 'RFM успешно пересчитан.'
        return 'Установите настройки RFM.'


class Person(models.Model):
    ACTIVE_CLIENT = ((True, 'Да'),
                     (False, 'Нет'))

    name = models.TextField()
    owner = models.ForeignKey(User,
                              related_name='clients',
                              on_delete=models.CASCADE,)
    slug = models.CharField(max_length=100)
    phone = PhoneNumberField(validators=[phone_validate])
    last_deal = models.DateField(null=True)
    pays = models.IntegerField(null=True)
    deal_count = models.IntegerField(null=True)
    last_deal_good = models.TextField(null=True)
    rfm_category = models.TextField(default='000')
    active_client = models.BooleanField(choices=ACTIVE_CLIENT,
                                        default=True,)
    tab = models.ForeignKey(Tab,
                            related_name='clients',
                            on_delete=models.CASCADE, )
    last_sent = models.DateField(null=True)
    rfm_move = models.TextField(default='000000')
    rfm_flag = models.BooleanField(default=False)

    objects = models.Manager()

    @classmethod
    def get_new_line(cls, data):
        phone = cls.phone_(data['phone'])
        phone_validate(phone)
        deal = {'date': data['date'],
                'pay': data['pay'],
                'good': data['good'].title()}
        obj, create = cls.objects.get_or_create(
            tab=data['tab'],
            owner=data['owner'],
            phone=phone,
            name=data['name'].title()
        )
        obj.save()
        obj.add_deal(deal)
        return obj

    @classmethod
    def phone_(cls, phone):
        if re.match(r'\+', phone):
            return phone
        if re.match(r'80', phone) and len(phone) == 11:
            return re.sub(r'80', '+375', phone, count=1)
        else:
            return '+' + phone

    @classmethod
    def date_(cls, dt):
        dt = re.findall(r'(\d{2}).(\d{2}).(\d{4})', dt)[0]
        return f'{dt[2]}-{dt[1]}-{dt[0]}'

    def add_deal(self, deal):
        deal['date'] = self.date_(deal['date'])
        deal['person'] = self
        new_deal, flag = Deals.objects.get_or_create(**deal)
        if flag:
            new_deal.save()
            self.summary()
        self.save()
        return True

    def summary(self):
        deals = Deals.objects.filter(person=self)
        pays = 0
        deal_count = 0
        for deal in deals:
            pays += deal.pay
            deal_count += 1
            if not self.last_deal or deal.date > self.last_deal:
                self.last_deal = deal.date
            self.save()
        self.pays = pays
        self.deal_count = deal_count
        self.save()

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

    def set_last_sent(self):
        self.rfm_flag = False
        self.last_sent = timezone.now()
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


class Deals(models.Model):
    person = models.ForeignKey(Person,
                               related_name='deals',
                               on_delete=models.CASCADE)
    date = models.DateField()
    pay = models.PositiveIntegerField()
    good = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return f'{self.date} {self.good} {self.pay}'


class Rules(models.Model):
    RFM = [
        ((int(a+b+c)*1000) + (int(a+b+c)-100),
         a+b+c + ' => ' + str(int(a+b+c)-100))
        for a in '32' for b in '321' for c in '321'
    ]

    # DAYS_OF_WEEK = (
    #     (1, 'Пнд'), (2, 'Втр'),
    #     (3, 'Срд'), (4, 'Чтв'),
    #     (5, 'Птц'), (6, 'Сбт'),
    #     (7, 'Вск')
    # )
    #
    # HOUR_TO_RUN = ((10, 10), (12, 12), (14, 14), (16, 16), (18, 18))

    ON_OFF = ((True, 'Правило активно'),
              (False, 'Правило не активно'))

    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,)
    name = models.CharField(max_length=250, verbose_name='Название')
    slug = models.CharField(max_length=100)
    from_to = MultiSelectField(choices=RFM,
                               default=None,
                               verbose_name='При каких переходах будет '
                                            'срабатывать триггер.')
    message = models.TextField(verbose_name='Текст рассылки. '
                                            'Можно персонализоровать с '
                                            'помощью {name}.')
    on_off_rule = models.BooleanField(default=True,
                                      choices=ON_OFF)
    tab = models.ForeignKey(Tab,
                            related_name='rules',
                            on_delete=models.CASCADE, )

    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.name, instance=self)
        super(Rules, self).save(*args, **kwargs)

    def get_absolute_url(self):
        tab = self.tab
        return reverse('rule', args=[tab.slug,
                                     self.slug])


class ActionLog(models.Model):
    owner = models.ForeignKey(User,
                              related_name='events',
                              on_delete=models.CASCADE)
    event_time = models.DateTimeField(default=timezone.now)
    event = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return self.event

    @classmethod
    def get_event(cls, event, owner):
        cls.objects.create(event=str(event), owner=owner)
