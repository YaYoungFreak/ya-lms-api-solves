import arcade
import random
from requests import get
from os import makedirs
from os.path import exists

WIDTH = 1280
HEIGHT = 720
TITLE = "Угадай-ка город"
IMAGES = "cities"

GEOCODER_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
          "Казань", "Нижний Новгород", "Челябинск", "Самара",
          "Омск", "Ростов-на-Дону", "Уфа", "Красноярск"]


def get_ll_spn(city):
    url = f"http://geocode-maps.yandex.ru/1.x/?apikey={GEOCODER_KEY}&geocode={city}&format=json"
    data = get(url).json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    lon, lat = map(float, data["Point"]["pos"].split())

    envelope = data["boundedBy"]["Envelope"]
    lower = list(map(float, envelope["lowerCorner"].split()))
    upper = list(map(float, envelope["upperCorner"].split()))

    size_lon = upper[0] - lower[0]
    size_lat = upper[1] - lower[1]

    # Сдвигаем центр и уменьшаем масштаб, чтобы название города не попало в кадр.
    spn = f"{size_lon * 0.04},{size_lat * 0.04}"

    return f"{lon},{lat}", spn


class SlideShow(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)

    def setup(self):
        makedirs(IMAGES, exist_ok=True)
        base = f"https://static-maps.yandex.ru/v1?apikey={STATIC_KEY}&"

        self.cities = CITIES[:]
        random.shuffle(self.cities)

        for city in self.cities:
            ll, spn = get_ll_spn(city)
            response = get(f"{base}ll={ll}&spn={spn}")
            with open(f"{IMAGES}/{city}.png", "wb") as file:
                file.write(response.content)

        self.index = 0
        self.background = arcade.load_texture(f"{IMAGES}/{self.cities[0]}.png")
        self.show_answer = False
        self.answer_text = arcade.Text("", 20, 20, arcade.color.YELLOW, 24, bold=True)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                (self.width - self.background.width) // 2,
                (self.height - self.background.height) // 2,
                self.background.width,
                self.background.height,
            ),
        )
        if self.show_answer:
            self.answer_text.text = self.cities[self.index]
            self.answer_text.draw()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.SPACE:
            self.show_answer = not self.show_answer
        elif key == arcade.key.RIGHT:
            self.index = (self.index + 1) % len(self.cities)
            self.background = arcade.load_texture(f"{IMAGES}/{self.cities[self.index]}.png")
            self.show_answer = False
        elif key == arcade.key.LEFT:
            self.index = (self.index - 1) % len(self.cities)
            self.background = arcade.load_texture(f"{IMAGES}/{self.cities[self.index]}.png")
            self.show_answer = False


slides = SlideShow()
slides.setup()
arcade.run()
