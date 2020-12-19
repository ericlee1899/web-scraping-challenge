#import modules
from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import requests
import time
import pymongo

#mongo
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars

#creating path
def startbrowser():
    executablepath = {'executable_path': 'C:/Bin/chromedriver.exe'}
    return Browser('chrome', **executablepath, headless=False)

#scrape function
def scrape():
    browser = startbrowser()
    collection.drop()

    #mars news
    newsurl = 'https://mars.nasa.gov/news/'
    browser.visit(newsurl)
    newshtml = browser.html
    newsbs = bs(newshtml,'lxml')
    newstitle = newsbs.find("div",class_="content_title").text
    newstext = newsbs.find("div", class_="rollover_description_inner").text

    #jpl
    jplurl = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jplurl)
    jplhtml = browser.html
    jplbs = bs(jplhtml,"html.parser")
    imageurl = jplbs.find('div',class_='carousel_container').article.footer.a['data-fancybox-href']
    baselink = "https:"+jplbs.find('div', class_='jpl_logo').a['href'].rstrip('/')
    featured_image_url = baselink+imageurl

    #mars fact
    facturl = 'https://space-facts.com/mars/'
    facttable = pd.read_html(facturl)
    facthtml = facttable[0].to_html(header=False,index=False)

    #mars hemisphere
    hemiurl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemiurl)  
    hemihtml = browser.html 
    hemibs = bs(hemihtml,"html.parser") 
    results = hemibs.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
        productdict = {}
        titles = result.find('h3').text
        endlink = result.find("a")["href"]
        imagelink = "https://astrogeology.usgs.gov/" + endlink    
        browser.visit(imagelink)
        html = browser.html
        soup= bs(html, "html.parser")
        downloads = soup.find("div", class_="downloads")
        imageurl = downloads.find("a")["href"]
        productdict['title']= titles
        productdict['imageurl']= imageurl
        hemisphere_image_urls.append(productdict)

    browser.quit()
    #return scraped data in dictionary
    scrapedata ={
		'newstitle' : newstitle,
		'summary': newstext,
        'featured_image': featured_image_url,
		'facttable': facthtml,
		'hemisphere_image_urls': hemisphere_image_urls,
        'newsurl': newsurl,
        'jplurl': jplurl,
        'facturl': facturl,
        'hemisphereurl': hemiurl,
        }
    collection.insert(scrapedata)
