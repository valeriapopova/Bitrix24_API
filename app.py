from itertools import chain

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
        name = json_file['data'][0]['name']
        phone = json_file['data'][1]['phone']
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
    try:
        json_file = request.get_json(force=False)
        url = json_file["url"]
        bx24 = Bitrix24(url)
        num = None
        result_list = []
        r = {}
        result = bx24.callMethod("crm.lead.list", filter={">=OPPORTUNITY": num}, select=['ID', 'TITLE', 'NAME', 'PHONE'])
        for res in result:
            result_list.append([{"id": res['ID']}, {"title": res['TITLE']}, {"name": res['NAME']},
                                {"phone": res['PHONE'][0]['VALUE']}])
        r['data'] = list(chain.from_iterable(result_list))
        return r

    except BadRequestKeyError:
        return Response("Пустое значение", 400)