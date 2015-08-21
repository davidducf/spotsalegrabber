'''
	Spot Sale Grabber
	Fetches all Sale/Closeout items for Skatepark of Tampa's webpage
	By: Ross Cooper and David Demianovich
'''

#Import
from bs4 import BeautifulSoup
import urllib2
import re
import sys

#If -t or --testing are passed, only parse a few product links.
#If not, parse all products on all pages.
testing = False
if len(sys.argv) == 2:
	if (sys.argv[1] == '-t') or (sys.argv[1] == '--testing'):
		testing = True

#All of the URLS are additions to this base URL
rootURL = 'http://skateparkoftampa.com'
closeoutURL = 'http://skateparkoftampa.com/spot/closeout.aspx'

#Download and parse the page using BeautifulSoup
basepageHTML = urllib2.urlopen(closeoutURL).read()
basepageSoup = BeautifulSoup(basepageHTML, "lxml")

#Get the number of sale pages.
#The links to each page are under the "ProductPager" class div
#Just get the length of the object resulting for a search for links under the ProductPager div
numPages = len(basepageSoup.find('div', class_="ProductPager").find_all('a'))

print "Number of Products List Pages: " + str(numPages)

def parseListPage(listpageURL):
	listpageHTML = urllib2.urlopen(listpageURL).read()
	listpageSoup = BeautifulSoup(listpageHTML, "lxml")
	
	productsOnPage = listpageSoup.find_all('div', class_="ProductBlock")
	
	print "\t\tNumber of products on this page: " + str(len(productsOnPage)) + "\n"
	
	#If it's an empty page, skip it
	if(len(productsOnPage)==0):
		print "Skipping this page."
		return
	
	
	#If we're testing 
	if testing:
		#Rigged to parse two products: 
		#one with the ADD TO CART text in the size divs and one without it.
		parseProduct('http://skateparkoftampa.com/product/69618/DC_Shoe_Co._Red_Charcoal_Rob_Dyrdek_Format_Tank_Top/&CID=191')
		parseProduct('http://skateparkoftampa.com/product/69587/Volcom_Dark_Grey_Skarktack_T_Shirt/&CID=2489')
	else: 
		#Iterate through all the products on the page and parse them.
		for product in productsOnPage:
			currentProductURL = rootURL + product.a.get('href')
			parseProduct( currentProductURL )
	
def parseProduct(productPageURL):
	productURL = productPageURL
	
	#Create a regex pattern to match the productID and colorID strings in the product URL
	#Uses the (?P<name>) syntax to create names for the matched sets
	regexPattern = "^http://skateparkoftampa.com/product/(?P<productID>[0-9]+)/.*/&CID=(?P<colorID>[0-9]+)"
	regexMatch = re.match(regexPattern , productPageURL)
	
	#Assign the values we get from regexing the URL
	productID = regexMatch.group('productID')
	productColorID = regexMatch.group('colorID')
	
	#The productKey is the concatenation of the PID and CID, 
	#might be useful as a unique identifier
	productKey = productID + productColorID

	#Open the product page with BeautifulSoup
	productpageHTML = urllib2.urlopen(productURL).read()
	productpageSoup = BeautifulSoup(productpageHTML, "lxml")
	
	#Take the product name from the title of the page by Stripping out the rest of the text
	productName = productpageSoup.title.string.replace(" in stock at SPoT Skate Shop", "").strip('\r\n\t')
	
	priceDiv = productpageSoup.find('div', class_='Ollie')
	
	regexPattern = ".*Reg Price: \$(?P<priceOriginal>.+) Your Price: \$(?P<priceSale>.+).*"
	regexMatch = re.match(regexPattern , priceDiv.get_text())
	
	#Assign the values we get from regexing the priceDivs
	productPriceOriginal = regexMatch.group('priceOriginal')
	productPriceSale = regexMatch.group('priceSale')
	
	#Discount can now be calculated.
	#A percentage rounded to two decimal places
	discountPercent =  str(round(1-float(productPriceSale)/float(productPriceOriginal),2))
	
	#Advance along the page to get to the div containing the color text
	colorDiv = priceDiv.next_sibling.next_sibling
	
	regexPattern = ".*Color: (?P<color>.+).*"
	regexMatch = re.match(regexPattern , colorDiv.get_text().strip())
	
	productColor = regexMatch.group('color')
	
	#Advance further along the page to find the div containing the sizes
	sizesDiv = colorDiv.next_sibling.next_sibling.next_sibling.next_sibling
	sizes = sizesDiv.find_all('a', class_='CartAddLinks')
	
	#For loop to iterate through the size divs
	#Strips them of special chars then isolates the size text
	#then reassigns the list value to that text
	for i in range(len(sizes)):	
		sizeRawText = sizes[i].get_text().strip()
		#Zero or One occurrences of ADD TO CART. Some have it, some don't.
		regexPattern = "(ADD TO CART: )?(?P<size>.+).*"
		regexMatch = re.match(regexPattern , sizeRawText)
		sizes[i] = regexMatch.group('size')
	
	print "\t\t\tproductName: " + productName	
	print "\t\t\tproductURL: " + productURL
	print "\t\t\tproductID: " + productID
	print "\t\t\tproductColorID: " + productColorID
	print "\t\t\tproductKey: " + productKey
	#print "\t\t\tproductCompany: " + productCompany //Not sure if this is necessary
	print "\t\t\tproductColor: " + productColor
	print "\t\t\tproductPriceOrginal: " + productPriceOriginal
	print "\t\t\tproductPriceSale: " + productPriceSale
	print "\t\t\tdiscountPercent: " + discountPercent
	print "\t\t\tsizes:"
	for i in range(len(sizes)):
		print "\t\t\t\t" + sizes[i]
	
	print "\n"

#Rigged to only parse one page if in testing mode,
#Otherwise parse every page of products
if testing:
	pagesToParse = 2
else:
	pagesToParse = numPages + 1

for pageNum in range (1, pagesToParse):
	currentListPageURL = closeoutURL + "?Page=" + str(pageNum)
	print "\tParsing Page: " + currentListPageURL 
	parseListPage(currentListPageURL)
