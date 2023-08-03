import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

URL = "https://www.nike.com/w/shoes-y7ok"
driver = webdriver.Chrome()
driver.get(URL)


# scrolls down until end of page
last_height = driver.execute_script("return document.body.scrollHeight")
changeStart = True
while True:
    if changeStart:
        start = time.perf_counter()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(.1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        fin = time.perf_counter()
        if fin - start > 0:
            break
        changeStart = False
    else:
        changeStart = True
    last_height = new_height


# gets individual links for each shoe and its color variations
links = set()
action = ActionChains(driver)
shoeContainers = driver.find_elements(By.CLASS_NAME, "product-card__body")
for container in shoeContainers:
    action.move_to_element(container).perform()
    linksContainers = driver.find_elements(By.CLASS_NAME, "css-10ic566")
    if len(linksContainers) != 0:
        for link in linksContainers:
            action.move_to_element(link).perform()
            shoeLink = link.get_attribute("href")
            links.add(shoeLink)
            print(shoeLink)
            print()
    else:
        bsShoeContainer = BeautifulSoup(driver.page_source, "html.parser")
        shoeLink = bsShoeContainer.find("a", class_="product-card__img-link-overlay")
        shoeLink = shoeLink["href"]
        links.add(shoeLink)
        print(shoeLink)
        print()


# visits each shoe link
count = 0
file = open("data.txt", "w")
for links in links:
    driver.get(links)
    time.sleep(.4)
    soupShoePage = BeautifulSoup(driver.page_source, "html.parser")

    # get shoe name, gender, and link
    shoeName = soupShoePage.find("h1", attrs={"data-test": "product-title"}).text
    shoeGender = soupShoePage.find("h2", attrs={"data-test": "product-sub-title"}).text

    # get image
    img = soupShoePage.find("img", attrs={"data-testid": "HeroImg"})
    img = soupShoePage.find("img", attrs={"data-testid": "HeroImg"})["src"] if img else ""

    # get shoe sizes
    unAvailableSizes = []
    availableSizes = []
    sizeContainers = soupShoePage.find("form", attrs={"id": "buyTools"})
    if sizeContainers != None:
        sizeContainers = sizeContainers.find_all("div", attrs={"class": None, "style": None, "id": None})
        for container in sizeContainers:
            input = container.find("input")
            label = container.find("label")
            if input == None or label == None:
                continue
            if input.has_attr('disabled'):
                unAvailableSizes.append(label.text)
            else:
                availableSizes.append(label.text)
    
    # write to file
    file.write("count: " + str(count) + "\n")
    file.write(shoeName + "\n")
    file.write(shoeGender + "\n")
    file.write("available sizes: " + str(availableSizes) + "\n")
    file.write("unavailable sizes: " + str(unAvailableSizes) + "\n")
    file.write("img: " + img + "\n\n")
    count += 1
    

file.close()
driver.quit()
print("Total shoes:", len(shoeContainers))