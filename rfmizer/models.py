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
    import validate_international_phonenumber
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

    def __init__(self, obj):
        self.bound_obj = obj
        self.raw_data = []
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


class UserFiles(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField()
    created_at = models.DateTimeField(auto_now=timezone.now())
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,)

    object = models.Manager()

    def __str__(self):
        return self.name

    def user_directory_path(instance, filename):
        return 'user_{0}/{1}'.format(instance.user.id, filename)


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


