import time
from selenium import webdriver
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import re
import sqlite3

def print_nothing():
    return True


def scroll(driver, size):
    try: 
        driver.execute_script("window.scrollTo(0, window.scrollY + "+str(size)+" )")
        time.sleep(4)
        show_more_bt = driver.find_element_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > div > div.W4P4ne > div:nth-child(2) > div.PFAhAf > div > span > span")
        show_more_bt.click()
        time.sleep(4)
    except NoSuchElementException:
       print("show more button not found!")


def getAppDetailsUrl(driver, url, conn, package_name, description=""):
    # retrive url
    driver.get(url);
    time.sleep(5) # Let the user actually see something!

    try:
        print("get app name and genre!")
        # app_name & genre                                            
        app_name = root = driver.find_element_by_xpath("""//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz/c-wiz[1]/div/div[2]/div/div[1]/c-wiz[1]/h1""").text
        # app_name = root = driver.find_element_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > c-wiz > c-wiz:nth-child(1) > div > div.D0ZKYe > div > div.sIskre > c-wiz:nth-child(1) > h1 > span").text
        genre =  root = driver.find_element_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > c-wiz > c-wiz:nth-child(1) > div > div.D0ZKYe > div > div.sIskre > div.jdjqLd > div.ZVWMWc > div:nth-child(1) > span:nth-child(2) > a").text
    except:
        print("some exception happened on get app name and genre")

    #scrolling the page in order to load more comments
    # how much scroll then more comments are loaded
    scroll_limit = 150
    current_scroll = 0
    for i in range(0,scroll_limit):
        page_h = driver.execute_script("return document.body.scrollHeight")
        if page_h > current_scroll:
            print("scroling", i, "of" ,scroll_limit, page_h)
            scroll(driver, page_h)
            current_scroll = page_h
        else :
            print("scroll limit was archivied")

    # find the root comment comments and try to evaluate how many childs (comments) are in the conteiner
    root = driver.find_element_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > div > div.W4P4ne > div:nth-child(2) > div")
    zc7KVe = root.find_elements_by_class_name("zc7KVe")

    # logical element selector
    start_host_comment_selector  = "#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > div > div.W4P4ne > div:nth-child(2) > div > div:nth-child("
    middle_host_comment_selector = ") > div > div.d15Mdf.bAhLNe > div.UD7Dzf > span:nth-child("

    # OBJECT THAT WILL BE SAVE ON DATABASE
    output = {
        "url": "",
        "app_name": "",
        "short_comment": "",
        "full_comment": "",
        "description": "",
        "genre": "",
    }

    #for each all childs comments
    childs_len = (len(zc7KVe))
    for i in range(1, childs_len):
        try:
            print("save data", i, "of", childs_len)

            short_comment_element = driver.find_element_by_css_selector(start_host_comment_selector + str(i) + middle_host_comment_selector+("1)"))
            full_comment_element = driver.find_element_by_css_selector(start_host_comment_selector + str(i) + middle_host_comment_selector+("2)"))
            
            full_comment = full_comment_element.get_attribute("textContent")
            short_comment = short_comment_element.text

            output['url']           = (url)
            output['app_name']      = (app_name)
            output['short_comment'] = ("<p>" + re.sub(r'\n(.)', r'\1', short_comment) + "</p>")
            output['full_comment']  = ("<p>" +re.sub(r'\n(.)', r'\1', full_comment) + "</p>")
            output['description']   = ("<p>" +re.sub(r'\n(.)', r'\1', description) + "</p>")
            output['genre']         = (genre)

            insertData(conn, output)

        except:
            print("expected error")
    
       

def getAppDescription(driver, url):
    driver.get(url);
    time.sleep(5) # Let the user actually see something!
    description_selector = "#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > c-wiz:nth-child(1) > c-wiz:nth-child(4) > div > div.W4P4ne > div.PHBdkd > div.DWPxHb > span > div"
    description_element = driver.find_element_by_css_selector(description_selector)
    return description_element.text
   
def connectDB():
    conn = sqlite3.connect('playStore.db')
    return conn


def insertData(conn, data ):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO reviews (url, app_name, short_comment, full_comment, description, genre)
        VALUES (?,?,?,?,?,?)
        """, (data['url'], data['app_name'], data['short_comment'], data['full_comment'], data['description'], data['genre']))
        conn.commit()
    except Exception as e:
        print(" insertData ", str(e))

def closeApplication(driver):
    print("quit")
    time.sleep(5)
    driver.quit()

query = "&showAllReviews=true"
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
driver = webdriver.Chrome('/home/rudda/bin/selenium-web-drive/chromedriver', chrome_options=options)

dataframe = pd.read_csv("./data/app_url.csv", delimiter=",")
conn = connectDB()

dataframe_len = len(dataframe['url'])
app_order = 1

for url in dataframe['url']:
    print("profress ", str(app_order/dataframe_len) + "%" ,app_order, "of", dataframe_len)
    package_name = str(url).split('?id=')[1]
    description = getAppDescription(driver, url)
    getAppDetailsUrl(driver, url+str(query), conn, package_name, description)

conn.close()

closeApplication(driver)



 
