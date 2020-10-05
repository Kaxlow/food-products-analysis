import sqlite3

conn = sqlite3.connect('capstone.sqlite')
cur = conn.cursor()

cur.execute('''SELECT Allergens.allergen, COUNT(Contains_allergens.allergens_id) AS allergen_count
    FROM Contains_allergens JOIN Allergens ON Contains_allergens.allergens_id = Allergens.id
    GROUP BY Allergens.id
    ORDER BY allergen_count DESC
    LIMIT 10''')

for row in cur:
    print(row[0])
    print('Count:', row[1])

print('Completed')
