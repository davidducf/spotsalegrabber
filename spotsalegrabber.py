'''
	Spot Sale Grabber
	
	Fetches all Sale/Closeout items for Skatepark of Tampa's webpage
	
	By: Ross Cooper and David Demianovich
'''

#Import
from bs4 import BeautifulSoup
import urllib2
import re

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
	
	if(len(productsOnPage)==0):
		print "Skipping this page."
		return
	
	
	#Iterate through all the products on the page and parse them.
	'''
	for product in productsOnPage:
		currentProductURL = rootURL + product.a.get('href')
		parseProduct( currentProductURL )
	'''
	
	#Rigged to only analyze one product
	parseProduct('http://skateparkoftampa.com/product/28486/Deathwish_Green_Glitter_Lizard_King_Gang_Name_Deck/&CID=9234')
	
	
	
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
	
	#Discount can now be calculated
	discountPercent =  str(1-float(productPriceSale)/float(productPriceOriginal))
	
	#Advance along the page to get to the div containing the color text
	colorDiv = priceDiv.next_sibling.next_sibling
	
	regexPattern = ".*Color: (?P<color>.+).*"
	regexMatch = re.match(regexPattern , colorDiv.get_text().strip())
	
	productColor = regexMatch.group('color')
	
	sizesDiv = colorDiv.next_sibling.next_sibling.next_sibling.next_sibling
	sizes = sizesDiv.find_all('a', class_='CartAddLinks')
	
	#For loop to iterate through the size divs
	#Strips them of special chars then isolates the size text
	#then reassigns the list value to that text
	for size in sizes:	
		regexPattern = ".*ADD TO CART: (?P<size>.+).*"
		regexMatch = re.match(regexPattern , size.get_text().strip())
		size = regexMatch.group('size')
	
	print "\t\t\tproductName: " + productName	
	print "\t\t\tproductURL: " + productURL
	print "\t\t\tproductID: " + productID
	print "\t\t\tproductColorID: " + productColorID
	print "\t\t\tproductKey: " + productKey
	#print "\t\t\tproductCompany: " + productCompany
	print "\t\t\tproductColor: " + productColor
	print "\t\t\tproductPriceOrginal: " + productPriceOriginal
	print "\t\t\tproductPriceSale: " + productPriceSale
	print "\t\t\tdiscountPercent: " + discountPercent
	print "\t\t\tsizes:"
	#for size in sizes:
	#	print ("\t\t\t" + size),
	
	print "\n"
	

#pagesToParse = numPages + 1

#Rigged to only parse one page
pagesToParse = 2

for pageNum in range (1, pagesToParse):
	currentListPageURL = closeoutURL + "?Page=" + str(pageNum)
	print "\tParsing Page: " + currentListPageURL 
	parseListPage(currentListPageURL)
