import hashlib
import secrets
from collections import defaultdict
import random

from bitrix24 import Bitrix24
from flask import Flask, request, Response
from werkzeug.exceptions import BadRequestKeyError

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)


@app.route('/bitrix/post', methods=['POST'])
def post_lead_bitrix():
    """Добавляет новый лид"""
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['first_name']

        phone = json_file['data'][0]['phone_number']

        url = json_file['url']
        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.lead.add",
                            fields={
                                "NAME": name,
                                "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
                                "ASSIGNED_BY_ID": 1,
                            },
                            params={"REGISTER_SONET_EVENT": "Y"})
        return Response("Создан лид", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/get_leads', methods=['POST'])
def get_leads():
    """Возвращает список лидов по фильтру. Является реализацией списочного метода для лидов"""
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


@app.route('/bitrix/get_contact_list', methods=['POST'])
def get_contact_list():
    """Возвращает список контактов по фильтру. Является реализацией списочного метода для контактов."""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        r = {}
        result = bx24.callMethod("crm.contact.list", filter={"TYPE_ID": "CLIENT"}, select=["*"])
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
    """Добавляет новый контакт"""
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['first_name']
        phone = json_file['data'][0]['phone_number']
        if 'last_name' in json_file['data'][0]:
            last_name = json_file['data'][0]['last_name']
        else:
            last_name = '-'
        if 'patronymic_name' in json_file['data'][0]:
            patronymic_name = json_file['data'][0]['patronymic_name']
        else:
            patronymic_name = '-'

        url = json_file['url']
        bx24 = Bitrix24(url)
        r = bx24.callMethod("crm.contact.add",
                            fields={
                                "NAME": name,
                                "LAST_NAME": last_name,
                                "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
                                "SECOND_NAME": patronymic_name,
                                "TYPE_ID": "CLIENT",
                                "ASSIGNED_BY_ID": 1,
                            },
                            params={"REGISTER_SONET_EVENT": "Y"})
        return Response("Создан новый контакт", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/feed_message', methods=['POST'])
def feed_message():
    """Отправляет сообщение в ленту в Birix24 по url"""
    try:
        json_file = request.get_json(force=False)
        peer_id = json_file['data'][0]['peer_id']
        text = json_file['data'][0]['text']

        url = json_file['url']
        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.livefeedmessage.add",
                            fields={
                                "POST_TITLE": f"ТЕСТ НОВОЙ СВЯЗКИ !!!! новое сообщение id/email "
                                              f"пользователя - {peer_id}",
                                "MESSAGE": text
                            })
        return Response("Создано новое сообщение", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/new_deal', methods=['POST'])
def new_deal():
    """Создает новую сделку"""
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
        # Для отправки сообщения в общий чат или групповой чат в DIALOG_ID нужно передавать значение
        # в формате chatXXX, где XXX - идентификатор чата

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
            r = {'event': webhook['event']}
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
            elif webhook['event'] == 'onCrmLeadAdd':
                """Событие, вызываемое при создании лида."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmLeadUpdate':
                """Событие, вызываемое при обновлении лида."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmLeadDelete':
                """Событие, вызываемое при удалении лида."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmActivityAdd':
                """Событие, вызываемое при создании дела."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'OnVoximplantCallStart':
                """Событие вызывается при начале разговора 
                (ответе оператора при входящем и ответе абонента при исходящем)"""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmContactAdd':
                """Событие, вызываемое при создании контакта."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmContactUpdate':
                """Событие, вызываемое при обновлении контакта."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'onCrmDealAdd':
                """Событие, вызываемое при создании сделки."""
                r['data'] = [webhook['data'].values()]
                return r
            elif webhook['event'] == 'OnSaleOrderSaved':
                """Происходит в конце сохранения заказа, когда заказ и все связанные сущности уже сохранены. """
                r['data'] = [webhook['data'].values()]
                return r
            # elif webhook['event'] == '':
            #     """"""
            #     r['data'] = [webhook['data'].values()]
            #     return r
            else:
                pass

        return Response("ok", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/new_company', methods=['POST'])
def new_company():
    """Создаёт новую компанию."""
    try:
        json_file = request.get_json(force=False)
        company_name = json_file['data'][0]['company_name']
        url = json_file['url']
        phone = json_file['data'][0]['phone']

        if 'email' in json_file['data'][0]:
            email = json_file['data'][0]['email']
        else:
            email = 'nomail@no.com'
        if 'address' in json_file['data'][0]:
            address = json_file['data'][0]['address']
        else:
            address = '-'

        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.company.add",
                            fields={
                                "TITLE": company_name,
                                "ADDRESS": address,
                                "COMPANY_TYPE": "CUSTOMER",
                                "INDUSTRY": "MANUFACTURING",
                                "OPENED": "Y",
                                "ASSIGNED_BY_ID": 1,
                                "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
                                "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}]
                            })
        return Response("Создано новая компания", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_user_id', methods=['POST'])
def search_user_by_id():
    """Метод для получения списка пользователей с ускоренным поиском по id"""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        id_ = json_file['data'][0]['id']
        r = {}
        result = bx24.callMethod("user.search", FILTER={"ID": id_, "USER_TYPE": "employee"})
        result_list = defaultdict(list)
        for myd in result:
            for k, v in myd.items():
                result_list[k].append(v)

        r['data'] = [result_list]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_user_email', methods=['POST'])
def search_user_by_email():
    """Метод для получения списка пользователей с ускоренным поиском по email"""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        email = json_file['data'][0]['email']
        bx24 = Bitrix24(url)
        r = {}
        result = bx24.callMethod("user.search", FILTER={"EMAIL": email, "USER_TYPE": "employee"})
        result_list = defaultdict(list)
        for myd in result:
            for k, v in myd.items():
                result_list[k].append(v)

        r['data'] = [result_list]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_contact_id', methods=['POST'])
def search_contact_by_id():
    """Возвращает контакт по идентификатору."""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        id_ = json_file['data'][0]['id']
        r = {}
        result = bx24.callMethod("crm.contact.get", FILTER={"ID": id_})

        r['data'] = [result]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_deal_id', methods=['POST'])
def search_deal_by_id():
    """Возвращает сделку по идентификатору."""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        id_ = json_file['data'][0]['id']
        r = {}
        result = bx24.callMethod("crm.deal.get", FILTER={"ID": id_})

        r['data'] = [result]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_invoice_id', methods=['POST'])
def search_invoice_by_id():
    """Возвращает счёт по идентификатору"""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        id_ = json_file['data'][0]['id']
        r = {}
        result = bx24.callMethod("crm.invoice.get", FILTER={"ID": id_})

        r['data'] = [result]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/new_product', methods=['POST'])
def new_product():
    """Создаёт новый товар."""
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['name']
        url = json_file['url']
        price = json_file['data'][0]['price']

        if 'description' in json_file['data'][0]:
            description = json_file['data'][0]['description']
        else:
            description = '-'

        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.product.add",
                            fields={
                                "NAME": name,
                                "PRICE": price,
                                "DESCRIPTION": description,
                                "CURRENCY_ID": "RUB"
                            })
        return Response("Создан новый товар.", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/update_product', methods=['POST'])
def update_product():
    """Обновляет товар"""
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['NAME']
        url = json_file['url']
        price = json_file['data'][0]['PRICE']
        id_ = json_file['data'][0]['id']
        bx24 = Bitrix24(url)

        r = bx24.callMethod("crm.product.update",
                            id=id_,
                            fields={
                                "NAME": name,
                                "PRICE": price,
                                "CURRENCY_ID": "RUB"
                            })
        return Response("Товар обновлен", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/new_element', methods=['POST'])
def new_element():
    """Метод создаёт элемент списка."""
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['name']
        url = json_file['url']
        iblock_type_id = json_file['data'][0]['IBLOCK_TYPE_ID']
        iblock_code = json_file['data'][0]['IBLOCK_CODE']
        element_code = json_file['data'][0]['ELEMENT_CODE']

        bx24 = Bitrix24(url)

        r = bx24.callMethod("lists.element.add",
                            IBLOCK_TYPE_ID=iblock_type_id,
                            IBLOCK_CODE=iblock_code,
                            ELEMENT_CODE=element_code,
                            fields={
                                "NAME": name})
        return Response("Создан новый элемент списка.", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/update_element', methods=['POST'])
def update_element():
    """Обновляет элемент списка'"""
    try:
        json_file = request.get_json(force=False)
        name = json_file['data'][0]['name']
        url = json_file['url']
        iblock_type_id = json_file['data'][0]['IBLOCK_TYPE_ID']
        iblock_code = json_file['data'][0]['IBLOCK_CODE']
        element_code = json_file['data'][0]['ELEMENT_CODE']

        bx24 = Bitrix24(url)

        def find_match(string_list, wanted):
            for string in string_list:
                if string.startswith(wanted):
                    return string
            return None

        pr_key = find_match(json_file['data'][0], 'property')

        if pr_key is not None:
            pr_value = json_file['data'][0][pr_key]
            r = bx24.callMethod("lists.element.update",
                                IBLOCK_TYPE_ID=iblock_type_id,
                                IBLOCK_CODE=iblock_code,
                                ELEMENT_CODE=element_code,
                                fields={
                                    "NAME": name,
                                    pr_key: pr_value})
            return Response("Элемент списка обновлен", 201)

        else:
            r = bx24.callMethod("lists.element.update",
                                IBLOCK_TYPE_ID=iblock_type_id,
                                IBLOCK_CODE=iblock_code,
                                ELEMENT_CODE=element_code,
                                fields={
                                    "NAME": name})
            return Response("Элемент списка обновлен", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_product_id', methods=['POST'])
def search_product_by_id():
    """Возвращает товар по идентификатору."""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        id_ = json_file['data'][0]['id']
        r = {}
        result = bx24.callMethod("crm.product.get", FILTER={"ID": id_})

        r['data'] = [result]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/search_company_id', methods=['POST'])
def search_company_by_id():
    """Возвращает компанию по идентификатору."""
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        id_ = json_file['data'][0]['ID']
        r = {}
        result = bx24.callMethod("crm.company.get", FILTER={"ID": id_})

        r['data'] = [result]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/update_deal', methods=['POST'])
def update_deal():
    """Обновляет сделку по id"""
    try:
        json_file = request.get_json(force=False)
        url = json_file['url']
        id_ = json_file['data'][0]['ID']
        bx24 = Bitrix24(url)
        result = json_file['data'][0]
        result_list = defaultdict(list)
        for k, v in result.items():
            if k != 'id':
                result_list[k].append(v)
        r = bx24.callMethod("crm.deal.update",
                            id=id_,
                            fields=result_list)
        return Response("Товар обновлен", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/tel_reqister', methods=['POST'])
def tel_reqister():
    """Метод регистрирует звонок в Битрикс24, для чего ищет в CRM соответствующий номеру объект"""
    try:
        json_file = request.get_json(force=False)
        url = json_file['url']
        id_ = json_file['data'][0]['USER_ID']
        user_phone_inner = json_file['data'][0]['USER_PHONE_INNER']
        phone = json_file['data'][0]['PHONE_NUMBER']
        bx24 = Bitrix24(url)
        r = {}
        res = bx24.callMethod("telephony.externalcall.register",
                              fields={
                                  "USER_ID": id_,
                                  "USER_PHONE_INNER": user_phone_inner,
                                  "PHONE_NUMBER": phone
                              })
        r['data'] = [res]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/tel_finish', methods=['POST'])
def tel_finish():
    """Метод завершает звонок, фиксирует его в статистике, скрывает у пользователя карточку звонка."""
    try:
        json_file = request.get_json(force=False)
        url = json_file['url']
        id_ = json_file['data'][0]['USER_ID']
        call_id = json_file['data'][0]['CALL_ID']
        duration = json_file['data'][0]['DURATION']

        if 'COST' in json_file['data'][0]:
            cost = json_file['data'][0]['COST']
        else:
            cost = '-'

        bx24 = Bitrix24(url)
        r = {}
        res = bx24.callMethod("telephony.externalcall.finish",
                              fields={
                                  "USER_ID": id_,
                                  "CALL_ID": call_id,
                                  "DURATION": duration,
                                  "COST": cost
                              })
        r['data'] = [res]
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/tel_hide', methods=['POST'])
def tel_hide():
    """Метод скрывает карточку звонка у пользователя."""
    try:
        json_file = request.get_json(force=False)
        url = json_file['url']
        id_ = json_file['data'][0]['USER_ID']
        call_id = json_file['data'][0]['CALL_ID']

        bx24 = Bitrix24(url)

        res = bx24.callMethod("telephony.externalcall.hide",
                              fields={
                                  "USER_ID": id_,
                                  "CALL_ID": call_id
                              })
        return Response("Карточка звонка у пользователя скрыта", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)


@app.route('/bitrix/tel_attach_record', methods=['POST'])
def tel_attach_record():
    """Метод прикрепляет запись к завершенному звонку и к Делу звонка. (Должен вызываться после
    tel_finish, если запись на момент вызова finish еще не готова.) """
    try:
        json_file = request.get_json(force=False)
        url = json_file['url']
        call_id = json_file['data'][0]['CALL_ID'] #Идентификатор звонка из метода tel_register.
        if 'FILENAME' in json_file['data'][0]:
            filename = json_file['data'][0]['FILENAME']
        else:
            filename = f'{random.randint(0, 99999999)}{random.randint(0, 99999999)}.mp3'
        bx24 = Bitrix24(url)

        res = bx24.callMethod("telephony.externalCall.attachRecord",
                              fields={
                                  "CALL_ID": call_id,
                                  "FILENAME": filename
                              })
        return Response("Запись прикреплена", 201)

    except BadRequestKeyError:
        return Response("Пустое значение", 400)