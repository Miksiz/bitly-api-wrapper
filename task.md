# Обертка для REST API
От вас требуется реализовать обертку для REST API веб-сервиса bit.ly. Следующий фрагмент кода описывает предполагаемый сценарий использования:
```
async with BitlyAPI(**credentials) as api:
    responses = await asyncio.gather(
        api.link.clicks(link='https://bit.ly/2EAh3Vo'),
        api.link.clicks(link='2A7lTGn'),
    )
    for response in responses:
        print(response.link_clicks)  # output: <number of clicks>

    try:
        response = await api.link.clicks(link='bad_link')
    except APIException as err:
        print(err)  # output: [404] NOT FOUND
```

## Требования и пояснения к заданию №2
- В качестве сервиса, обертку над API которого вы хотите реализовать, вы можете выбрать любой популярный сервис с REST API (или другим видом HTTP API). Например, нам будет особенно интересно API какого-нибудь рекламного кабинета =) Вариант с bit.ly предложен как один из наиболее простых.
    - Если вашим выбором все-таки будет bit.ly, код, приведенный выше, должен выполняться и демонстрировать ожидаемое поведение. Для других сервисов вам потребуется написать аналогичный демонстрационный код.
    - Вы самостоятельно выбираете, какую версию API конкретного сервиса использовать. В том числе для bit.ly. Мы рекомендуем работать с версией v3.
    - Запрос к выбранному вами сервису должен подразумевать аутентификацию. Например, через access token или какой-нибудь другой механизм. Чем сложнее — тем интереснее =)
- Запросы к API должны быть асинхронными. Для реализации разрешается использовать библиотеки. Например, aiohttp. Однако логическая реализация самой обертки должна быть полностью разработана вами.
- Класс-обертка должен имплементировать осмысленный интерфейс асинхронного контекстного менеджера (__aenter__/__aexit__). «Осмысленный» — значит, в указанных методах должен выполняться некоторый полезный код =) Если осмысленный код написать не получается, реализуйте версию без контекстного менеджера.
- В реализацию достаточно включить некоторый минимальный набор методов для демонстрации работоспособности обертки. 
