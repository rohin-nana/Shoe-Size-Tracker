# scraping imports
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# mongodb imports
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi



# ---------------- SCRAPING ----------------

URL = "https://www.nike.com/w/shoes-y7ok"
driver = webdriver.Chrome()
driver.get(URL)

# scrolls down until end of page
last_height = driver.execute_script("return document.body.scrollHeight")
change_start = True
while True:
    if change_start:
        start = time.perf_counter()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(.1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        fin = time.perf_counter()
        if fin - start > 10:
            break
        change_start = False
    else:
        change_start = True
    last_height = new_height


# gets individual links for each shoe and its color variations
links = set()
action = ActionChains(driver)
shoe_containers = driver.find_elements(By.CLASS_NAME, "product-card__body")
for container in shoe_containers:
    action.move_to_element(container).perform()
    links_containers = driver.find_elements(By.CLASS_NAME, "css-10ic566")
    
    # shoe has more than 1 color
    if len(links_containers) != 0:
        for link in links_containers:
            try:
                action.move_to_element(link).perform()
                shoe_link = link.get_attribute("href")
                links.add(shoe_link)
                print(shoe_link)
                print()
            except Exception as e:
                print("error getting link from color")
                print(e)
                print()
    
    # shoe has only 1 color
    else:
        try:
            container_html = container.get_attribute('outerHTML') 
            bs_container = BeautifulSoup(container_html, "html.parser")
            shoe_link = bs_container.find("a", class_="product-card__img-link-overlay")
            shoe_link = shoe_link["href"]
            links.add(shoe_link)
            print(shoe_link)
            print()
        except Exception as e:
            print("error getting main shoe link")
            print(e)
            print()


# visits each shoe link
count = 0
file = open("data.txt", "w")
for links in links:
    try:
        driver.get(links)
        time.sleep(.4)
        soup_shoe_page = BeautifulSoup(driver.page_source, "html.parser")

        # get shoe name, gender, and link
        shoe_name = soup_shoe_page.find("h1", attrs={"data-test": "product-title"}).text
        shoe_gender = soup_shoe_page.find("h2", attrs={"data-test": "product-sub-title"}).text

        # get image
        img = soup_shoe_page.find("img", attrs={"data-testid": "HeroImg"})
        img = soup_shoe_page.find("img", attrs={"data-testid": "HeroImg"})["src"] if img else ""

        # get shoe sizes
        available_sizes = []
        un_available_sizes = []
        size_containers = soup_shoe_page.find("form", attrs={"id": "buyTools"})
        if size_containers != None:
            size_containers = size_containers.find_all("div", attrs={"class": None, "style": None, "id": None})
            for container in size_containers:
                input = container.find("input")
                label = container.find("label")
                if input == None or label == None:
                    continue
                if input.has_attr('disabled'):
                    un_available_sizes.append(label.text)
                else:
                    available_sizes.append(label.text)
        
        # write to file
        file.write("count: " + str(count) + "\n")
        file.write(shoe_name + "\n")
        file.write(shoe_gender + "\n")
        file.write("available sizes: " + str(available_sizes) + "\n")
        file.write("unavailable sizes: " + str(un_available_sizes) + "\n")
        file.write("img: " + img + "\n\n")
        count += 1
    except Exception as e:
        print("error getting sizes")
        print(e)
        print()


file.close()
driver.quit()
print("Total shoes:", len(links))













# ---------------- QUERYING ----------------

uri = "mongodb+srv://rohin:BtmD9QGUo2YsYjlc@cluster0.pmqtxfx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))


def convertToArr(string) -> list[str]:
    string = string.replace("'", "")
    string = string[1: len(string) - 1]

    arr = string.split(", ")
    if arr[0] == "":
        return []
    return arr


try:
    # mongodb setup
    mydb = client["test"]
    shoes = mydb["shoes"]
    # clear database
    shoes.drop()

    file = open("data.txt", "r")
    lines = file.readlines()
    length = len(lines)
    ind = 0

    # iterate through each line in data.txt and retrieve and format data
    while ind < length:
        ind += 1
        name = lines[ind]
        name = name[0:len(name)-1].replace("'", "’")
        ind += 1

        gender = lines[ind]
        gender = gender[0:len(gender)-1].replace("'", "’")
        ind += 1

        available_sizes = lines[ind][17:]
        available_sizes = available_sizes.replace("M ", "M")
        available_sizes = available_sizes.replace("W ", "W")
        available_sizes = convertToArr(available_sizes[0:len(available_sizes)-1])
        ind += 1

        un_available_sizes = lines[ind][19:]
        un_available_sizes = un_available_sizes.replace("M ", "M")
        un_available_sizes = un_available_sizes.replace("W ", "W")
        un_available_sizes = convertToArr(un_available_sizes[0:len(un_available_sizes)-1])
        ind += 1

        image = lines[ind][5:]
        ind += 2

        shoe = { "name": name, "gender": gender, "availableSizes": available_sizes, "unAvailableSizes": un_available_sizes, "image": image }
        shoes.insert_one(shoe)

        # print(name)
        # print(gender)
        # print(availableSizes)
        # print(unAvailableSizes)
        # print(image)
        # print()

    file.close()
    print("Query complete")
except Exception as e:
    print(e)