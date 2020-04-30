import os
# Этот класс поможет нам сделать картинку из потока байт
import pygame
import requests
import spn_reformer
import math
# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:


def distance(coord_list):
    l = 111000
    len_of_way = int()
    for i in range(1, len(coord_list)):
        l_1 = math.radians((coord_list[i][1] + coord_list[i - 1][1]) / 2.)
        l_1 = math.cos(l_1)
        dx = (coord_list[i][0] - coord_list[i - 1][0]) * l * l_1
        dy = (coord_list[i][1] - coord_list[i - 1][1]) * l
        len_of_way += math.sqrt((dx ** 2) + (dy ** 2))
    return str(len_of_way).split('.')[0] + 'м'


toponym_to_find = input()

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    # обработка ошибочной ситуации
    pass

# Преобразуем ответ в json-объект
json_response = response.json()
# Получаем первый топоним из ответа геокодера.
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
# Координаты центра топонима:
toponym_coodrinates = toponym["Point"]["pos"]
# Долгота и широта:
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": ','.join(toponym_coodrinates.split()),
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    #...
    pass
# Собираем параметры для запроса к StaticMapsAPI:

json_response = response.json()
# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
toponym_spn = {'lowerCorner': [0, 0], 'upperCorner': [0, 0]}
if float(toponym_lattitude) < point[1]:
    toponym_spn['lowerCorner'][1] = toponym_lattitude
    toponym_spn['upperCorner'][1] = point[1]
else:
    toponym_spn['lowerCorner'][1] = point[1]
    toponym_spn['upperCorner'][1] = toponym_lattitude
if float(toponym_longitude) < point[0]:
    toponym_spn['lowerCorner'][0] = toponym_longitude
    toponym_spn['upperCorner'][0] = point[0]
else:
    toponym_spn['lowerCorner'][0] = point[0]
    toponym_spn['upperCorner'][0] = toponym_longitude
toponym_spn['lowerCorner'] = list(map(float, toponym_spn['lowerCorner']))
toponym_spn['upperCorner'] = list(map(float, toponym_spn['upperCorner']))

lon_, lat_ = spn_reformer.reform(toponym_spn)
map_params = {
    "ll": ",".join([str(toponym_spn['lowerCorner'][0] + (lon_ / 2)), str(toponym_spn['lowerCorner'][1] + (lat_ / 2))]),
    "spn": ",".join([str(lon_), str(lat_)]),
    "l": "map",
    "pt": f'{toponym_longitude},{toponym_lattitude},pm2blm~{str(point[0])},{str(point[1])},pm2blm'
}
map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
print('Длинна дистанции:', distance([[float(toponym_longitude), float(toponym_lattitude)], [point[0], point[1]]]))
map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
# Рисуем картинку, загружаемую из только что созданного файла.
screen.blit(pygame.image.load(map_file), (0, 0))
# Переключаем экран и ждем закрытия окна.
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()

os.remove(map_file)