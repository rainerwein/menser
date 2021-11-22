import datetime
import re
import xml.etree.ElementTree as ET
import sys
import requests
import locale
from rich.console import Console
from rich.table import Table
from rich import box
import math
import argparse

LIGHT_PURPLE_BG = '\033[48;2;48;51;107;30m'
WHITE_TEXT = '\033[38;2;255;255;255m'
LIGHT_BLUE_BG = '\033[48;2;126;214;223;30m'
LIGHT_GREEN_BG = '\033[48;2;186;220;88;30m'
DARK_GREEN_BG = '\033[48;2;106;176;76;30m'
LIGHT_GREEN_TEXT = '\033[38;2;186;220;88;179m'
DARK_GREEN_TEXT = '\033[38;2;106;176;76;179m'
ENDC = '\033[0m'

refs_regex = re.compile('(\([ ,a-zA-Z0-9]*\))')
split_refs_regex = re.compile('[\(,]([ a-zA-Z0-9]*)')
remove_refs_regex = re.compile('\([ ,a-zA-Z0-9]*\)')
console = Console()

def get_food_types(piktogramme):
    fs = piktogramme
    food_types = []
    if fs is None:
        food_types.append('Sonstiges')
        return food_types
    if '/S.png' in fs:
        food_types.append('Schwein')
    if '/R.png' in fs:
        food_types.append('Rind')
    if '/G.png' in fs:
        food_types.append('Geflügel')
    if '/L.png' in fs:
        food_types.append('Lamm')
    if '/W.png' in fs:
        food_types.append('Wild')
    if '/F.png' in fs:
        food_types.append('Fisch')
    if '/V.png' in fs:
        food_types.append('Vegetarisch')
    if '/veg.png' in fs:
        food_types.append('Vegan')
    if '/MSC.png' in fs:
        food_types.append('MSC Fisch')
    if '/Gf.png' in fs:
        food_types.append('Glutenfrei')
    if '/CO2.png' in fs:
        food_types.append('CO2-Neutral')
    if '/B.png' in fs:
        food_types.append('Bio')
    if '/MV.png' in fs:
        food_types.append('MensaVital')
    
    return food_types


def get_refs(title):
    raw = ''.join(refs_regex.findall(title))
    return split_refs_regex.findall(raw)


def build_notes_string(title):
    food_is = []
    food_contains = []
    refs = get_refs(title)
    for r in refs:
        #Zusatzstoffe
        if r == '1':
            food_is.append('mit Farbstoff')
        elif r == '2':
            food_is.append('mit Koffein')
        elif r == '4':
            food_is.append('mit Konservierungsstoffen')
        elif r == '5':
            food_is.append('mit Süßungsmittel')
        elif r == '7':
            food_is.append('mit Antioxidationsmittel')
        elif r == '8':
            food_is.append('mit Geschmacksverstärker')
        elif r == '9':
            food_is.append('geschwefelt')
        elif r == '10':
            food_is.append('geschwärzt')
        elif r == '11':
            food_is.append('gewachst')
        elif r == '12':
            food_is.append('mit Phosphat')
        elif r == '13':
            food_is.append('mit einer Phenylalaninquelle')
        elif r == '30':
            food_is.append('mit Fettglasur')

        #Allergene
        elif r == 'Wz':
            food_contains.append('Weizen (Gluten)')
        elif r == 'Ro':
            food_contains.append('Roggen (Gluten)')
        elif r == 'Ge':
            food_contains.append('Gerste (Gluten)')
        elif r == 'Hf':
            food_contains.append('Hafer')
        elif r == 'Kr':
            food_contains.append('Krebstiere')
        elif r == 'Ei':
            food_contains.append('Eier')
        elif r == 'Er':
            food_contains.append('Erdnüsse')
        elif r == 'So':
            food_contains.append('Soja')
        elif r == 'Mi':
            food_contains.append('Milch/Laktose')
        elif r == 'Man':
            food_contains.append('Mandeln')
        elif r == 'Hs':
            food_contains.append('Haselnüsse')
        elif r == 'Wa':
            food_contains.append('Walnüsse')
        elif r == 'Ka':
            food_contains.append('Cashewnüsse')
        elif r == 'Pe':
            food_contains.append('Pekanüsse')
        elif r == 'Pa':
            food_contains.append('Paranüsse')
        elif r == 'Pi':
            food_contains.append('Pistazien')
        elif r == 'Mac':
            food_contains.append('Macadamianüsse')
        elif r == 'Sel':
            food_contains.append('Sellerie')
        elif r == 'Sen':
            food_contains.append('Senf')
        elif r == 'Ses':
            food_contains.append('Sesam')
        elif r == 'Su':
            food_contains.append('Schwefeloxid/Sulfite')
        elif r == 'Lu':
            food_contains.append('Lupinen')
        elif r == 'We':
            food_contains.append('Weichtiere')
        else:
            food_contains.append('mit undefinierter Chemikalie ' + r)
    return food_contains


def get_description(title):
    raw = remove_refs_regex.split(title)
    return ''.join(raw)

def pprint(description, category, food_type, notes, plist, veggieFlag=False):
    color_text = ''
    color_bg = ''
    color = ''
    if 'Vegan' in food_type:
        color = 'rgb(0,148,50)'
        color_bg = DARK_GREEN_BG
        color_text = DARK_GREEN_TEXT
    elif 'Vegetarisch' in food_type:
        color = 'rgb(163,203,56)'
        color_bg = LIGHT_GREEN_BG
        color_text = LIGHT_GREEN_TEXT
    elif not veggieFlag:
        color = 'white'
    else: 
        return

    pStud = f'{plist[0]}'
    if pStud == '-':
        pStud = '💯'
    pStud += '€'
    
    console.print(f'[white]{category}: [{color}]{", ".join(food_type)}[/] [{color} reverse] {" ".join(description.split())}[/] [{color}]{pStud} [/]')

def parse_url(url, mensa):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    }

    xml_data = requests.get(url, headers=headers);

    if not xml_data.ok:
        print(f'Error: {xml_data.status_code}. check mensa parameter')
        return

    root = ET.fromstring(xml_data.content.decode('utf-8'))
    for day in root:
        date = datetime.date.fromtimestamp(int(day.get('timestamp')))
        today = datetime.date.today()
        if date < today:
            continue
        if date == today:
            daystring = 'Heute'
        elif today + datetime.timedelta(days=1) == date:
            daystring = 'Morgen'
        else:
            daystring = date.strftime('%A')
        fullstring = date.strftime(f'{daystring} %d.%m.%Y')
        width = console.width - len(fullstring)
        left = (math.floor(width / 2) - 1) * '-'
        right = (math.ceil(width / 2) - 1) * '-'
        print(f'\n{left} {fullstring} {right}\n')

        for item in day:
            title = item.find('title').text
            description = get_description(title)
            category = item.find('category').text
            notes = build_notes_string(title)
            plist = [item.find('preis1').text,
                     item.find('preis2').text,
                     item.find('preis3').text]
            food_type = get_food_types(item.find('piktogramme').text)
            if '-v' in sys.argv:
                pprint(description, category, food_type, notes, plist, veggieFlag=True)
            else:
                pprint(description, category, food_type, notes, plist)
        
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: ' + sys.argv[0] + ' <mensa>')
        exit(1)

    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    
    url = f'https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml/mensa-{sys.argv[1]}.xml'
    parse_url(url=url, mensa=sys.argv[1])
