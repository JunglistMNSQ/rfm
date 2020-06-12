import requests
import re

# config
send_url = 'http://api.rocketsms.by/simple/send'
balance_url = 'http://api.rocketsms.by/simple/balance'


# def save_log(string, sender=User):


def check_balance(login, pass_hash, message=None):
    sms_quantity = 0
    if message:
        sms_quantity = -len(message) // 67
    try:
        request = requests.get(balance_url,
                               {'username': login,
                                'password': pass_hash},)
        result = request.json()
        balance = result['credits']
    except Exception as e:
        print('Не получается проверить баланс: нет ствязи с RocketSMS.')
        print(e)
    else:
        if balance > -sms_quantity:
            return True, balance
        else:
            print(f'Не достаточно кредитов для отправки смс - '
                  f'{balance}')
            return False, balance


def send_sms(login, pass_hash, phone, message):
    phone = re.sub(r'\+', '', phone)
    data = {'username': login, 'password': pass_hash,
            'phone': phone, 'text': message, 'priority': 'true'}
    try:
        request = requests.post(send_url, data=data)
        result = request.json()
        status = result['status']
    except Exception as e:
        print('Не получается выслать SMS: нет ствязи с RocketSMS.')
        print(e)
    else:
        if (status == 'SENT') | (status == 'QUEUED'):
            print(f'SMS Принято, статус: {status}')
        else:
            print(f'SMS отклонено, статус: {status}')
