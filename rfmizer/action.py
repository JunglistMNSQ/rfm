from .models import *
from .rocket_sms import *


class BalanceExeption(Exception):
    pass


class GetItems:
    sender = None

    @classmethod
    def get_active_users(cls):
        return User.objects.filter(is_active=True)

    @classmethod
    def get_active_tabs(cls):
        users = cls.get_active_users()
        return ManageTable.objects.filter(owner__in=users, on_off=True)

    @classmethod
    def get_rules(cls):
        tabs = cls.get_active_tabs()
        return Rules.objects.filter(tab__in=tabs, on_off_rule=True)

    @classmethod
    def get_clients(cls, owner, tab, rfm_move):
        return Person.objects.filter(
            owner=owner,
            tab=tab,
            rfm_move__in=rfm_move,
            rfm_flag=True
        )


class ActionRFMizer(GetItems):
    @classmethod
    def run_rfmizer(cls):
        tabs = cls.get_active_tabs()
        for tab in tabs:
            tab.rfmizer()
        return True

    @classmethod
    def run_rules(cls):
        rules_list = cls.get_rules()
        print(rules_list)
        for rule in rules_list:
            owner, tab, rfm_move = rule.owner, rule.tab, rule.from_to
            message = rule.message
            print(owner, tab, rfm_move)
            login, pass_hash = (
                owner.profile.sms_login, owner.profile.sms_pass
            )
            clients = cls.get_clients(owner, tab, rfm_move)
            print(rule, rule.from_to, clients)
            try:
                for client in clients:
                    message = re.sub(r'\{name\}', client.name, message)
                    phone = client.phone.as_e164
                    balance = cls.sender.check_balance(
                        login, pass_hash, phone, message
                    )
                    if balance[0]:
                        res = cls.sender.send_sms(
                            login, pass_hash, phone, message
                        )
                        event = f'{res}. Баланс {balance[1]}'
                        ActionLog.get_event(event, owner)
                        client.set_last_sent()
                    else:
                        ActionLog.get_event(balance[2], owner)
                        raise BalanceExeption
            except BalanceExeption:
                break


class ActionRocketSMS(ActionRFMizer):
    sender = RocketSMS
