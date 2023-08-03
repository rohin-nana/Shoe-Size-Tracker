# rohin
# BtmD9QGUo2YsYjlc
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def convertToArr(string) -> list[str]:
    string = string.replace("'", "")
    string = string[1: len(string)-1]

    arr = string.split(", ")
    if arr[0] == "":
        return []
    return arr


uri = "mongodb+srv://rohin:BtmD9QGUo2YsYjlc@cluster0.pmqtxfx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))



try:
    mydb = client["test"]
    shoes = mydb["shoes"]
    f = open("data.txt", "r")
    lines = f.readlines()
    length = len(lines)
    ind = 0
    while ind < length:
        ind += 1
        name = lines[ind]
        ind += 1
        gender = lines[ind]
        ind += 1
        availableSizes = lines[ind][17:]
        ind += 1
        unAvailableSizes = lines[ind][19:]
        ind += 1
        image = lines[ind][5:]
        ind += 2
        name = name[0:len(name)-1].replace("'", "’")
        gender = gender[0:len(gender)-1].replace("'", "’")
        availableSizes = availableSizes.replace("M ", "M")
        availableSizes = availableSizes.replace("W ", "W")
        availableSizes = convertToArr(availableSizes[0:len(availableSizes)-1])
        unAvailableSizes = unAvailableSizes.replace("M ", "M")
        unAvailableSizes = unAvailableSizes.replace("W ", "W")
        unAvailableSizes = convertToArr(unAvailableSizes[0:len(unAvailableSizes)-1])

        shoe = { "name": name, "gender": gender, "availableSizes": availableSizes, "unAvailableSizes": unAvailableSizes, "image": image }
        x = shoes.insert_one(shoe)
        # print(name)
        # print(gender)
        # print(availableSizes)
        # print(unAvailableSizes)
        # print(image)
        # print()

    f.close()
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)