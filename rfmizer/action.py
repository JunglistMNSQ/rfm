from django.db import connection
from re import sub
from .models import ActionLog, Rules, Tab, User
from .sms import RocketSMS


class BalanceExeption(Exception):
    pass


class GetItems:
    sender = None

    @classmethod
    def select_from_db(cls, _id):
        with connection.cursor() as c:
            c.execute(f'SELECT from_to FROM rfmizer_rules '
                      f'WHERE id = {_id}')
            return c.fetchone()[0].split(',')

    @classmethod
    def get_active_users(cls):
        return User.objects.filter(is_active=True)

    @classmethod
    def get_active_tabs(cls):
        users = cls.get_active_users()
        return Tab.objects.filter(owner__in=users, on_off=True)

    @classmethod
    def get_rules(cls):
        tabs = cls.get_active_tabs()
        return Rules.objects.filter(tab__in=tabs, on_off_rule=True)


class ActionRFMizer(GetItems):
    @classmethod
    def run_rfmizer(cls):
        tabs = cls.get_active_tabs()
        for tab in tabs:
            tab.rfmizer()
        return True


class ActionRocketSMS(ActionRFMizer):
    sender = RocketSMS

    @classmethod
    def run_rules(cls):
        rules_list = cls.get_rules()
        for rule in rules_list:
            owner,  message = rule.owner, rule.message
            login, pass_hash = (
                owner.profile.sms_login, owner.profile.sms_pass
            )
            moves = cls.select_from_db(rule.id)
            clients = rule.tab.clients.filter(
                rfm_move__in=moves, rfm_flag=True
            )
            try:
                for client in clients:
                    msg = sub(r'{name}', client.name, message)
                    phone = client.phone.as_e164
                    balance = cls.sender.check_balance(
                        login, pass_hash, msg
                    )
                    if balance[0]:
                        res = cls.sender.send_sms(
                            login, pass_hash, phone, msg
                        )
                        event = f'{res}. Баланс {balance[1]}'
                        ActionLog.get_event(event, owner)
                        client.set_last_sent()
                    else:
                        ActionLog.get_event(balance[2], owner)
                        raise BalanceExeption
            except BalanceExeption:
                break
        return True
