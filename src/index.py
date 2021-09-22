import time
from selenium import webdriver
import pandas as pd

def scroll(driver):
    print('scroll')
    driver.execute_script("window.scrollTo(0, window.scrollY + 9000)")
    time.sleep(4)

def getAppDetailsUrl(driver, url):
    driver.get(url);
    time.sleep(5) # Let the user actually see something!

    for item in range(25):
        scroll(driver)

    elems = driver.find_elements_by_xpath("//a[@href]")
    host = "https://play.google.com/store/apps/details?id="
    urls = {'url': []}

    for elem in elems:
        if(host in elem.get_attribute("href")):
            goodUrl = elem.get_attribute("href");
            print(goodUrl)
            urls['url'].append(goodUrl)
    
    return urls


driver = webdriver.Chrome('/home/rudda/bin/selenium-web-drive/chromedriver')
url_host = "https://play.google.com/store/search?c=apps&"
dataframe = pd.read_csv('./data/app_id.csv', delimiter=";")

print(dataframe.head(2))

# a-Z queries 
for q  in range(97,123):
   appUrl = (url_host + "q=" + chr(q))
   print(appUrl) 
   result = getAppDetailsUrl(driver, appUrl )
   result = pd.DataFrame(result)
   dataframe = dataframe.append(result)


dataframe.to_csv("./data/dataframe.csv")


time.sleep(5)
driver.quit()