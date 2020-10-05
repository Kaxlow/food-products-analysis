import urllib.request, urllib.parse, urllib.error
import json
import ssl
import sqlite3
import re

#API documentation says: you have to add a User-Agent HTTP Header with the name of your app, the version, system and a url (if any), not to be blocked by
#mistake.
UserAgent_HTTP_Header = {'UserAgent': 'HealthyFoodChoices - Android - Version 1.0'}

#Web server does not handle chunked data transfer correctly. May need to send http/1.0 request.

#Enter url to retrieve json file from below. Search URL format found here: https://documenter.getpostman.com/view/8470508/SVtN3Wzy?version=latest#search-url
#Include search parameters in url
url = 'https://world.openfoodfacts.org/cgi/search.pl?action=process&tagtype_0=purchase_places&tag_contains_0=contains&tag_0=singapore&page_size=1000&json=true'

urlreq = urllib.request.Request(
    url,
    data=None,
    headers=UserAgent_HTTP_Header
)

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Load up connection to SQLite and create tables to store data in

conn = sqlite3.connect('capstone.sqlite')
cur = conn.cursor()

#For variable such as ingredients with many-to-many relationship with food products, need to add additional connector table

cur.executescript('''
DROP TABLE IF EXISTS Food_products;
DROP TABLE IF EXISTS Allergens;
DROP TABLE IF EXISTS Contains_allergens;

CREATE TABLE Food_products
    (id INTEGER PRIMARY KEY, product_name TEXT UNIQUE, manufacturing_places TEXT, carbohydrates REAL, trans_fat REAL, saturated_fat REAL, cholestrol REAL, sodium REAL, caffeine REAL, nutrition_score REAL);

CREATE TABLE IF NOT EXISTS Allergens
    (id INTEGER PRIMARY KEY, allergen TEXT UNIQUE);

CREATE TABLE IF NOT EXISTS Contains_allergens
    (food_products_id INTEGER, allergens_id INTEGER, PRIMARY KEY (food_products_id, allergens_id))

''')

#Open url and read.

fhandle = urllib.request.urlopen(urlreq, context=ctx)
rawdata = fhandle.read().decode()

#Test if js will properly load as a decoded python json object
try:
    js = json.loads(rawdata)
except:
    print("Unable to decode as python JSON object")
    js = None

#Test if js is a valid object
if not js:
    print('==== Failure To Retrieve ====')
    headers = dict(fhandle.getheaders())
    print(headers)
    quit()

#Print json.dumps (encoded) test. JSON pretty print

#print(json.dumps(js, indent=4))
#print("Success")

#Extract required data from python json object
count = 0
food_id = 0
all_id = 0

for dict in js['products']:
    #Get product name
    try:
        product_name = dict['product_name_en']
    except:
        product_name = None
        continue

    #Get manufacturing place
    try:
        manufacturing_place = dict['manufacturing_places']
    except:
        manufacturing_place = None

    #Get carbohydrates per 100g
    try:
        carbohydrates = dict['nutriments']['carbohydrates_100g']
    except:
        carbohydrates = None

    #Get trans_fat per 100g
    try:
        trans_fat = dict['nutriments']['trans-fat_100g']
    except:
        trans_fat = None

    #Get saturated_fat per 100g
    try:
        saturated_fat = dict['nutriments']['saturated-fat_100g']
    except:
        saturated_fat = None

    #Get cholestrol per 100g
    try:
        cholestrol = dict['nutriments']['cholesterol_100g']
    except:
        cholestrol = None

    #Get sodium per 100g
    try:
        sodium = dict['nutriments']['sodium_100g']
    except:
        sodium = None

    #Get caffeine per 100g
    try:
        caffeine = dict['nutriments']['caffeine_100g']
    except:
        caffeine = None

    #Get nutrition_score per 100g
    try:
        nutrition_score = dict['nutriments']['nutrition-score-uk_100g']
    except:
        nutrition_score = None

    # Check if food product is a duplicate, i.e., was already added to table before. Skip duplicates
    cur.execute('SELECT product_name FROM Food_products WHERE product_name = ? ', (product_name, ))
    row = cur.fetchone()

    if row is not None :
        continue

    food_id = food_id + 1

    #Insert into SQLite food products tables
    cur.execute('''INSERT OR IGNORE INTO Food_products (id, product_name, manufacturing_places, carbohydrates, trans_fat, saturated_fat, cholestrol, sodium, caffeine, nutrition_score)
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''', (food_id, product_name, manufacturing_place, carbohydrates, trans_fat, saturated_fat, cholestrol, sodium, caffeine, nutrition_score))

    #Get food_products_id for connector table
    cur.execute('SELECT id FROM Food_products WHERE product_name = ? ', (product_name, ))
    food_products_id = cur.fetchone()[0]

    count = count + 1

    #Get allergens
    allergens_tags = dict['allergens_tags']

    #Skip records without allergens tags
    if allergens_tags == None or allergens_tags == []:
        continue
    for all in allergens_tags:
            #Parse allergen and insert into SQLite allergens table
            if re.search('^[A-Za-z]{2}\:', all):
                allergen = all[3:]
            else:
                allergen = all

            #Check if allergen already exists in allregens table. If yes, only insert into connectors table. If no, insert into Allergens table AND connectors table
            cur.execute('SELECT allergen FROM Allergens WHERE allergen = ? ', (allergen, ))

            row = cur.fetchone()

            if row is None :
                all_id = all_id + 1
                cur.execute('''INSERT OR IGNORE INTO Allergens (id, allergen)
                VALUES ( ?, ? )''', (all_id, allergen))

            #Get allergens_id for connector table
            cur.execute('SELECT id FROM Allergens WHERE allergen = ? ', (allergen, ))
            allergens_id = cur.fetchone()[0]

            #Insert into connector table (Contains_allergens)
            cur.execute('''INSERT OR IGNORE INTO Contains_allergens (food_products_id, allergens_id)
            VALUES ( ?, ? )''', (food_products_id, allergens_id))

    if count % 50 == 0 : conn.commit()

conn.commit()
cur.close()

print('Count:', count)

print('JSON attributes successfully extracted')
