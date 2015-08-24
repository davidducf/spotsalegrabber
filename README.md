# spotsalegrabber.py
Parses the Skatepark of Tampa Sale/Closeout page into something usable and sortable using BeautifulSoup.

**Running**

>python spotsalegrabber.py [flag]

Flags:

-t, --testing : Only parses one page containing sale items and three specific sale items.

**TODO**

* Parse the category a product belongs to
* Create a data structure to hold the products
* Output the products data structure to some sort of file (CSV? HTML? HTML with Sorttable?)
* Separate the output options into their own functions and add flags
