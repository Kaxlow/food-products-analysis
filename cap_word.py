import sqlite3
import time
import zlib
import string

conn = sqlite3.connect('capstone.sqlite')
cur = conn.cursor()

#Create a dictionary of counts of each manufacturing place
cur.execute('SELECT id, manufacturing_places FROM Food_products')
mfg_counts = dict()
for row in cur :
    place = row[1]
    if place is None:
        continue
    mfg_counts[place] = mfg_counts.get(place, 0) + 1

x = sorted(mfg_counts, key=mfg_counts.get, reverse=True)
# Sorted returns a new sorted list of items in the dictionary (keys), ranked in desc order by values of each key

count_list = []
for k in x:
    count_list.append(mfg_counts[k])
highest = max(count_list)
lowest = min(count_list)
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('gword.js','w')
fhand.write("gword = [")
first = True
for k in x:
    if not first : fhand.write( ",\n")
    first = False
    size = mfg_counts[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * bigsize) + smallsize)
    fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write( "\n];\n")
fhand.close()

print("Output written to gword.js")
print("Open gword.htm in a browser to see the vizualization")
