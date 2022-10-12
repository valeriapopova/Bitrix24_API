import hashlib
import secrets
from collections import defaultdict
from itertools import product
from bitrix24 import Bitrix24
from flask import Flask, request, Response
from werkzeug.exceptions import BadRequestKeyError

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)


@app.route('/bitrix/post', methods=['POST'])
def post_bitrix():

    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['first_name']

        phone = json_file['data'][0]['phone_number']


        url = json_file['url']
        bx24 = Bitrix24(url)
        for i in range(len(name)):
            r = bx24.callMethod("crm.lead.add",
                            fields={
                                "NAME": name[i],
                                "PHONE": [{"VALUE": phone[i], "VALUE_TYPE": "WORK"}],
                                "ASSIGNED_BY_ID": 1,
                            },
                            params={"REGISTER_SONET_EVENT": "Y"})
        return Response("Создан лид", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/get_leads', methods=['POST'])
def get_leads():
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        num = None
        r = {}
        result = bx24.callMethod("crm.lead.list", filter={">=OPPORTUNITY": num}, select=["*"])
        result_list = defaultdict(list)
        for myd in result:
            for k, v in myd.items():
                result_list[k].append(v)

        r['data'] = [result_list]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/new_contact', methods=['POST'])
def new_contact():
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['first_name']
        phone = json_file['data'][0]['phone_number']
        if json_file['data'][0]['last_name']:
            last_name = json_file['data'][0]['last_name']
        else:
            last_name = '-'
        if json_file['data'][0]['patronymic_name']:
            patronymic_name = json_file['data'][0]['patronymic_name']
        else:
            patronymic_name = '-'

        url = json_file['url']
        bx24 = Bitrix24(url)
        for i in range(len(name)):
            r = bx24.callMethod("crm.contact.add",
                            fields={
                                "NAME": name[i],
                                "LAST_NAME": last_name[i],
                                "PHONE": [{"VALUE": phone[i], "VALUE_TYPE": "WORK"}],
                                "SECOND_NAME": patronymic_name[i],
                                "TYPE_ID": "CLIENT",
                                "ASSIGNED_BY_ID": 1,
                            },
                            params={"REGISTER_SONET_EVENT": "Y"})
        return Response("Создан новый контакт", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/feed_message', methods=['POST'])
def feed_message():
    try:
        json_file = request.get_json(force=False)
        peer_id = json_file['data'][0]['peer_id']
        text = json_file['data'][0]['text']

        url = json_file['url']
        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.livefeedmessage.add",
                            fields={
                                "POST_TITLE": f"ТЕСТ НОВОЙ СВЯЗКИ !!!! новое сообщение id/email пользователя - {peer_id}",
                                "MESSAGE": text
                            })
        return Response("Создано новое сообщение", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/new_deal', methods=['POST'])
def new_deal():
    try:
        json_file = request.get_json(force=False)
        order_id = json_file['order_id']
        url = json_file['url']
        date = json_file['date']
        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.deal.add",
                            fields={
                                "TITLE": "ТЕСТ НОВОЙ сделки !!!",
                                "COMMENTS": f'заказ {order_id}',
                                "STAGE_ID": "NEW",
                                "DATE_CREATE": date
                            })
        return Response("Создано новая сделка", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/get_key', methods=['POST'])
def homepage():
    """Возвращет пользователю - уникальный сгенерированный URL(только для метода bitrix/webhook)"""
    webhook = request.get_json(force=False)
    webhook_account_name = webhook['account_name']
    salt = secrets.token_hex(16) + webhook_account_name
    url = 'https://api.ecomru.ru/bitrix/webhook'
    url_key = hashlib.sha256(salt.encode('utf-8')).hexdigest()
    key = f'{url}/{url_key}'
    print(key)
    return key


@app.route('/bitrix/new_message', methods=['POST'])
def new_message():
    try:
        json_file = request.get_json(force=False)
        message = json_file['text']
        url = json_file['url']
        chat_id = json_file['url']
        # /getDialogId – получить идентификатор чата для внешних интеграций
        #Для отправки сообщения в общий чат или групповой чат в DIALOG_ID нужно передавать значение в формате chatXXX, где XXX - идентификатор чата

        bx24 = Bitrix24(url)

        r = bx24.callMethod("im.message.add",
                            fields={
                                    "DIALOG_ID": chat_id,
                                    "MESSAGE": message,
                            })
        return Response("Сообщение успешно отправлено", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/webhook/<key>', methods=['POST'])
def webhook():
    try:
        webhook = request.get_json(force=False)
        if webhook:
            r = {}
            r['event'] = webhook['event']
            if webhook['event'] == 'onCrmInvoiceAdd':
                """Событие, вызываемое при создании счёта."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmDealUpdate':
                """Событие, вызываемое при обновлении сделки."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmInvoiceSetStatus':
                """Событие, вызываемое при изменении статуса счёта."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmInvoiceUpdate':
                """Событие, вызываемое при обновлении счёта."""
                r['data'] = [webhook['data'].values()]
                return r
            else:
                pass

        return Response("ok", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)