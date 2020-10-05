# food-products-analysis
An analysis of food products purchased in Singapore

This project aims to provide insights from an analysis of food products purchased in Singapore, using data from the site of Open Food Facts.

Source: https://world.openfoodfacts.org/data 

The project consists of the following steps:

1. Retrieve data from Open Food Facts site, and stores data in SQLite Database. Once done, open capstone.sqlite in DB Browser for SQLite.

    Files: cap_ret.py, capstone.sqlite

2. Rank allergens in food products by the number of products that include them

    Files: cap_dump.py

3. Build a word cloud visualization of places where the food products were made in. The bigger the word, the more common the place of manufacturing. Once done, open gword.htm to view visualization.

    Files: cap_word.py, gword.js, gword.htm, d3.layout.cloud.js, d3.v2.js

    Note: This section includes a word cloud visualization template provided by the Coursera instructor whom I took my Python classes under.
   
An image of the word cloud visualization can be found in the file Capstone word cloud.jpg
