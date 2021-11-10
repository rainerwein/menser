import requests


url = 'https://openmensa.org/api/v2/canteens/264/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
}

response = requests.get(url + 'days', headers=headers)

if(not response.ok):
    print('error fetching data')
    exit

print('Veg[etarische/ane] Gerichte in der Mensa Langemarckplatz:')

days = response.json()
for day in days:
    if day["closed"] is True:
        break
    print(day["date"] + ":")
    meals = requests.get(url + 'days/' + day["date"] + '/meals', headers=headers).json()
    #print(meals)
    for meal in meals:
        category = meal["category"]
        if category == 'Vegan' or category == 'Vegetarisch':
            print('\t' +meal["name"])
