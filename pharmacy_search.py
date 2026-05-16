import os
import sys
import math
import requests

GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
SEARCH_API_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

MAP_FILE = "map.png"


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    return math.sqrt(dx * dx + dy * dy)


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


def find_pharmacy(lon, lat):
    url = (f"https://search-maps.yandex.ru/v1/?apikey={SEARCH_API_KEY}"
           f"&text=аптека&lang=ru_RU&ll={lon},{lat}&type=biz&results=1")
    response = requests.get(url)
    if not response:
        return None

    features = response.json()["features"]
    if not features:
        return None

    org = features[0]
    meta = org["properties"]["CompanyMetaData"]
    point = org["geometry"]["coordinates"]
    return {
        "name": meta["name"],
        "address": meta["address"],
        "hours": meta.get("Hours", {}).get("text", "часы работы не указаны"),
        "lon": float(point[0]),
        "lat": float(point[1]),
    }


def main():
    address = " ".join(sys.argv[1:]) or input("Введите адрес: ")

    home = get_coords(address)
    if home is None:
        print(f"Адрес не найден: {address}")
        return

    pharmacy = find_pharmacy(*home)
    if pharmacy is None:
        print("Аптека не найдена")
        return

    pharm = (pharmacy["lon"], pharmacy["lat"])
    dist = lonlat_distance(home, pharm)

    print(f"Название: {pharmacy['name']}")
    print(f"Адрес: {pharmacy['address']}")
    print(f"Время работы: {pharmacy['hours']}")
    print(f"Расстояние: {dist:.0f} м")

    pt = f"{home[0]},{home[1]},pm2rdm~{pharm[0]},{pharm[1]},pm2gnm"
    map_url = f"https://static-maps.yandex.ru/v1?pt={pt}&apikey={STATIC_API_KEY}"
    response = requests.get(map_url)
    if not response:
        print("Ошибка:", response.status_code, response.reason)
        sys.exit(1)

    with open(MAP_FILE, "wb") as f:
        f.write(response.content)
    os.startfile(MAP_FILE)


if __name__ == "__main__":
    main()
