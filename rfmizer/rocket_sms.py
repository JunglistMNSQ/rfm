import requests
import re


class RocketSMS:
    send_url = 'http://api.rocketsms.by/simple/send'
    balance_url = 'http://api.rocketsms.by/simple/balance'

    @classmethod
    def check_balance(cls, login, pass_hash, message=None):
        sms_quantity = 0
        if message:
            sms_quantity = abs(-len(message) // 67)
        try:
            request = requests.get(cls.balance_url,
                                   {'username': login,
                                    'password': pass_hash},)
            result = request.json()
            balance = result['credits']
        except Exception:
            return (
                False,
                None,
                'Не получается проверить баланс: нет связи с RocketSMS.'
            )
        else:
            if balance > sms_quantity:
                return (
                    True, balance, None
                )
            else:
                return (
                    False,
                    balance,
                    f'Не достаточно кредитов для отправки смс - {balance}'
                )

    @classmethod
    def send_sms(cls, login, pass_hash, phone, message):
        phone = re.sub(r'\+', '', phone)
        data = {'username': login, 'password': pass_hash,
                'phone': phone, 'text': message, 'priority': 'true'}
        try:
            request = requests.post(cls.send_url, data=data)
            result = request.json()
            status = result['status']
        except Exception:
            return 'Не получается выслать SMS: нет ствязи с RocketSMS.'
        else:
            if (status == 'SENT') | (status == 'QUEUED'):
                return f'SMS Принято, статус: {status}'
            else:
                return f'SMS отклонено, статус: {status}'
