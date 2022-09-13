# API bitrix для оповещения о новых лидах


Метод, позвляющий сохранять лиды из вк в битрикс


***/bitrix*** доступ к api bitrix

___POST___

_/bitrix/post_ - Отправляет новые лиды(из вк) по указанному url битрикс24

*Parameters*


json - данные которые нужно перенаправить должны иметь такой вид и содержать url bitrix24

```
{
 "data": [{"name": name}, {"phone": phone}],
  "url" - url вида "https://example.bitrix24.com/rest/1/33olqeits4avuyqu"
}
```


Responses 201 успешно

___рекомендуемый пример запроса___

```
def post_to_bitrix(res, url, host):
    data = {'url': url}
    res.update(data)
    url = f'http://{host}:5001/bitrix/post'
    response = requests.post(url, json=res)
    return response
```
