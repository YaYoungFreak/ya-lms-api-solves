import sys
from io import BytesIO

import requests
from PIL import Image

GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
SEARCH_API_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"


def get_coords(address):
    url = f"http://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_API_KEY}&geocode={address}&format=json"
    response = requests.get(url)
    if not response:
        return None

    data = response.json()
    found = data["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]["found"]
    if found == "0":
        return None

    coords = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
    return float(coords[0]), float(coords[1])


def search(text, lon, lat, results=10):
    url = (f"https://search-maps.yandex.ru/v1/?apikey={SEARCH_API_KEY}"
           f"&text={text}&lang=ru_RU&ll={lon},{lat}&type=biz&results={results}")
    response = requests.get(url)
    print(url)
    if not response:
        return []
    return response.json()["features"]


def show_map(pt):
    url = f"https://static-maps.yandex.ru/v1?pt={pt}&apikey={STATIC_API_KEY}"
    response = requests.get(url)
    if not response:
        print("Ошибка:", response.status_code, response.reason)
        sys.exit(1)

    Image.open(BytesIO(response.content)).show()


def get_color(meta):
    hours = meta.get("Hours")
    if not hours:
        return "pm2grm"
    avail = hours.get("Availabilities", [{}])[0]
    if avail.get("TwentyFourHours"):
        return "pm2gnm"
    return "pm2blm"


def main():
    address = " ".join(sys.argv[1:]) or input("Введите адрес: ")

    home = get_coords(address)
    if home is None:
        print(f"Адрес не найден: {address}")
        return

    orgs = search("аптека", *home, results=10)
    if not orgs:
        print("Аптеки не найдены")
        return

    points = [f"{home[0]},{home[1]},pm2rdm"]
    for org in orgs:
        meta = org["properties"]["CompanyMetaData"]
        lon, lat = org["geometry"]["coordinates"]
        points.append(f"{lon},{lat},{get_color(meta)}")

    show_map("~".join(points))


if __name__ == "__main__":
    main()
