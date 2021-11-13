import requests
import datetime
import locale
import sys


locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

LIGHT_PURPLE_BG = '\033[48;2;48;51;107;30m'
WHITE_TEXT = '\033[38;2;255;255;255m'
LIGHT_BLUE_BG = '\033[48;2;126;214;223;30m'
LIGHT_GREEN_BG = '\033[48;2;186;220;88;30m'
DARK_GREEN_BG = '\033[48;2;106;176;76;30m'
LIGHT_GREEN_TEXT = '\033[38;2;186;220;88;179m'
DARK_GREEN_TEXT = '\033[38;2;106;176;76;179m'

ENDC = '\033[0m'

url = 'https://openmensa.org/api/v2/canteens/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
}

mensa_id = '264'

if len(sys.argv) == 2:
    mensa_id = sys.argv[1]

url += mensa_id + '/'
name = requests.get(url, headers=headers).json()['name']

response = requests.get(url + 'days', headers=headers)

if(not response.ok):
    print('error fetching data')
    exit

print(LIGHT_PURPLE_BG + WHITE_TEXT + 'VegX Gerichte in ' + name + ':' + ENDC)
print()
days = response.json()
for day in days:
    if day["closed"] is True:
        break
    datum = datetime.datetime.strptime(day["date"], '%Y-%m-%d').date()
    today = datetime.date.today()
    if today == datum:
        daystring = 'Heute'
    elif datetime.date.today() + datetime.timedelta(days=1) == datum:
        daystring = 'Morgen'
    else:
        daystring = datum.strftime('%A')
    print(LIGHT_BLUE_BG + daystring + datum.strftime(' %d.%m.%Y ') + ENDC)
    meals = requests.get(url + 'days/' + day["date"] + '/meals', headers=headers).json()

    for meal in meals:
        category = meal["category"]
        price = meal["prices"]["students"]
        if category == 'Vegan' or category == 'Vegetarisch':
            if category == 'Vegan':
                color_bg = DARK_GREEN_BG
                color_text = DARK_GREEN_TEXT
            else:
                color_bg = LIGHT_GREEN_BG
                color_text = LIGHT_GREEN_TEXT

            print(color_bg + ' ' + category + ' ' + ENDC + ' ' + color_text + ' ' + meal["name"] + ' ' + ENDC + color_bg + str(price) + '€' + ENDC)

    print()
