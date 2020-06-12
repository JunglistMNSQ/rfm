from .models import *

class GetItems:
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


class ActionRFMizer(GetItems):
    @classmethod
    def run_rfmizer(cls):
        tabs = cls.get_active_tabs()
        for tab in tabs:
            tab.rfmizer()
        return True


class ActionSMSSender(ActionRFMizer):
    pass
