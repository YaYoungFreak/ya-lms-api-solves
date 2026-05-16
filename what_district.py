import requests

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
    "geocode": input("Введите адрес: "),
    "format": "json",
}

response = requests.get(geocoder_api_server, params=geocoder_params)
if not response:
    print("Ошибка запроса:", response.status_code, response.reason)
    exit(1)

features = response.json()["response"]["GeoObjectCollection"]["featureMember"]
if not features:
    print("Адрес не найден")
    exit(1)

geocoder_params["geocode"] = features[0]["GeoObject"]["Point"]["pos"].replace(" ", ",")
geocoder_params["kind"] = "district"

response = requests.get(geocoder_api_server, params=geocoder_params)
if not response:
    print("Ошибка запроса:", response.status_code, response.reason)
    exit(1)

features = response.json()["response"]["GeoObjectCollection"]["featureMember"]
if not features:
    print("Район не найден")
    exit(1)

print(features[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"])
