from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import csv
import ctypes
import os
import glob

REBIRTH = "Rebirth"
AFTERBIRTH = "Afterbirth"
AFTERBIRTH_PLUS = "Afterbirth Plus"
REPENTANCE = "Repentance"

#DEFAULT_STRING = "Misc"
PASSIVE_STRING = "Passive"

URL = "https://platinumgod.co.uk/repentance"

# Type Directory Here
DIR = r"C:\Users\Luca Hughes\Desktop\Web_Scraper"

ITEM_ID = "item_id"
TRINKET_ID = "trinket_id"

HEADER_ITEMS = [ITEM_ID, "item_name", "item_desc", "item_quality", "item_type", "item_game"]
HEADER_TRINKETS = [TRINKET_ID, "trinket_name", "trinket_desc", "trinket_game"]
HEADER_ACTIVE_ITEM = [ITEM_ID, "item_charge"]
HEADER_BOSS_ITEM = [ITEM_ID, "unlock_char", "unlock_boss"]
HEADER_BOSS_TRINKET = [TRINKET_ID, "unlock_char", "unlock_boss"]
HEADER_CHALLENGE_ITEM = [ITEM_ID, "unlock_challenge"]
HEADER_CHALLENGE_TRINKET = [TRINKET_ID, "unlock_challenge"]
HEADER_MISC_ITEM = [ITEM_ID, "misc_unlock"]
HEADER_MISC_TRINKET = [TRINKET_ID, "misc_unlock"]
HEADER_ITEM_POOLS = [ITEM_ID, "item_pool"]
HEADER_ITEM_TRANSFORMATIONS = [ITEM_ID, "item_transformation"]
HEADER_PASSIVE_TAGS = [ITEM_ID, "item_tag"]

#characters = ["Isaac", "Maggy", "Cain", "Judas", "???", "Eve", "Samson", "Azazel", "Lazarus", "Eden", "The Lost", "Lilith", "Keeper", "Apollyon", "The Forgotten", "Bethany", "Jacob and Esau"]
DARK_ROOM = "Dark Room"
CHEST = "Chest"
LAMB = "The Lamb"
BLUE_BABY = "???"
BOSSES = ["Mom's Heart", "Mega Satan", "Greedier", "Mom", "Isaac", BLUE_BABY, "Satan", LAMB, "Boss Rush", "Hush", "Delirium", "Mother", "The Beast", "Greed"]

def deleteFiles():
    files = glob.glob(DIR + "\Data/*")
    for f in files:
        os.remove(f)

def showError():
    ctypes.windll.user32.MessageBoxW(0, 'Website Markup Code has Changed! Please Investigate.', 'Error!', 16)
    raise SystemExit(0) # exit from script so new CSV files are not created

def filterBosses(bossList):
    for unlockBoss in bossList:
        if unlockBoss[2] != "Isaac, ???, Satan and The Lamb":
            for boss in BOSSES:
                if boss.lower() in unlockBoss[2].lower():
                    print(boss + " " + unlockBoss[2])
                    unlockBoss[2] = boss
                    break
                elif DARK_ROOM.lower() in unlockBoss[2].lower():
                    unlockBoss[2] = LAMB
                    break
                elif CHEST.lower() in unlockBoss[2].lower():
                    unlockBoss[2] = BLUE_BABY
                    break

            no_lowercase = ' '.join([w for w in unlockBoss[2].split(' ') if not w.islower()])
            if no_lowercase != "":
                no_numbers = ' '.join([w for w in no_lowercase.split(' ') if not w.isdigit()])
                no_brackets = no_numbers.split('(', 1)[0]
                unlockBoss[2] = no_brackets
            else:
                try:
                    pFrom = unlockBoss[2].index("the ") + 4
                    pTo = unlockBoss[2].index(" for")
                    unlockBoss[2] = unlockBoss[2][pFrom: pTo].title()
                except:
                    showError()
                    #unlockBoss[2] = DEFAULT_STRING
                    
    return bossList


def miscUnlock(id, itemTrinketList, miscUnlocks):
    try:
        #pFrom = (itemTrinketList[-1].rindex("by ") + 3)
        misc = itemTrinketList[-1].split('by', 1)[1].lstrip().capitalize()
    except:
        try:
            misc = itemTrinketList[-1].split('UNLOCK:', 1)[1].lstrip().capitalize()
        except:
            showError()
            #misc = DEFAULT_STRING
    print(misc)
    miscUnlocks.append([id, misc])
    return miscUnlocks

def challengeUnlock(id, itemTrinketList, challengeUnlocks):
    try:
        try:
            pFrom = itemTrinketList[-1].rindex("defeating ") + 10
        except:
            pFrom = itemTrinketList[-1].rindex("beating ") + 8
        challenge = itemTrinketList[-1][pFrom:]
    except:
        showError()
        #challenge = DEFAULT_STRING
    print(challenge)
    challengeUnlocks.append([id, challenge])
    return challengeUnlocks

def bossUnlock(id, itemTrinketList, bossUnlocks):
    try:
        try:
            pFrom = itemTrinketList[-1].rindex("defeating ") + 10
        except:
            pFrom = itemTrinketList[-1].rindex("beating ") + 8
        try:
            try:
                pTo = itemTrinketList[-1].rindex(" as")
                inc = 4
            except:
                pTo = itemTrinketList[-1].rindex(" with")
                inc = 6
            boss = itemTrinketList[-1][pFrom: pTo]

            # The 'Blue Baby' character is inconsistently named on website
            if '???' in itemTrinketList[-1][pTo+inc:]:
                 char = "Blue Baby"
            else:
                char = itemTrinketList[-1][pTo+inc:]
        except:
            boss = itemTrinketList[-1][pFrom:]
            char = "Any Character" # the unlock requirements for the item/trinket can be met with any character
    except:
        showError()
        #boss = DEFAULT_STRING
        #char = DEFAULT_STRING
    print(boss)
    print(char)
    bossUnlocks.append([id, char, boss])
    return bossUnlocks

# Checks the Paragraph String for any Transformations
def checkForTrans(details, id, transformations):
    if(details[-1].startswith('Counts')):
        try: 
            pFrom = details[-1].rindex("the ") + 4
            pTo = details[-1].rindex(" transformation")
            transformation = details[-1][pFrom: pTo]
            print(transformation)
            transformations.append([id, transformation])
            details.pop()
            checkForTrans(details, id, transformations)
        except: 
            print("Planetarium Unlock Item") # Not Data Required for this Project
    return transformations

# Outputs a List to a CSV File
def outputToCSV(list, file, header):
    if list: # make sure list is populated before trying to write as CSV
        file = DIR + "\Data/" + file
        with open(file, 'a', newline='') as fd:
            writer = csv.writer(fd, escapechar='\\')
            if len(open(file).readlines()) == 0: writer.writerow([h for h in header])
            writer.writerows(list)

# Scrapes Website for Game Items
def scrapeItems(game, div):
    itemList = []
    itemPools = []
    itemTransformations = []

    bossUnlocks = []
    challengeUnlocks = []
    miscUnlocks = []

    activeItemRecharge = []
    passiveItemTags = []

    # Repentance and Afterbirth Plus items denote the number of them using a span tag
    if game == AFTERBIRTH_PLUS or game == REPENTANCE: 
        spanIndex = 1 
    else: 
        spanIndex = 0
    listIndex = 0

    found = True 
    items = soup.find("div", {"class": div})

    while found == True:
        try:
            itemDetails = []
            for li in items.find_all("span")[spanIndex].find_all("p"):
                itemDetails.append(li.get_text())

            itemDetails.pop() # last paragraph is always the "tags"

            itemName = itemDetails[0]
            print(itemName)

            itemID = itemDetails[1][8:]
            print(itemID)

            itemPickup = re.sub('"', "", itemDetails[2])
            print(itemPickup)

            itemQuality = itemDetails[3][9:]
            print(itemQuality)
                
            extrasList = []
            for li in items.find_all("ul")[listIndex].find_all("p"):
                extrasList.append(li.get_text())

            itemType = extrasList[0][6:]
            print(itemType)

            if(itemType.lower() == "active" or itemType.lower() == "active/passive item"): 
                charge = extrasList[1][15:]
                activeItemRecharge.append([itemID, charge])
                print(charge)
            else:
                if itemType != PASSIVE_STRING: # if the item type has multiple types
                    passiveTags = itemType.split(",") # put types in a list
                    for tag in passiveTags:
                        if tag != PASSIVE_STRING: 
                            passiveItemTags.append([itemID, tag.lstrip().title()]) # put types into separate list
                            print(tag)
                    itemType = PASSIVE_STRING # removes tags as they're no longer required

            itemPool = extrasList[-1][11:] # skip the first 11 characters of string
            tempPool = itemPool.split(",")
            #tempPool = [x.strip() for x in itemPool.split(',')]
            for item in tempPool:
                itemPools.append([itemID, item.lstrip()])
                print(item)

            for x in extrasList: itemDetails.pop() # remove items from list as they are no longer required

            if(itemDetails[-1].startswith('UNLOCK:')):
                if "challenge" in itemDetails[-1].lower().split(): # string *must* be singular; not plural
                    challengeUnlocks = challengeUnlock(itemID, itemDetails, challengeUnlocks)
                elif "defeating" in itemDetails[-1].lower() or "beating" in itemDetails[-1].lower():
                    bossUnlocks = bossUnlock(itemID, itemDetails, bossUnlocks)
                else:
                    miscUnlocks = miscUnlock(itemID, itemDetails, miscUnlocks)
                itemDetails.pop()
            if(itemDetails[-1].startswith(REPENTANCE.upper())):
                itemDetails.pop()

            itemTransformations = checkForTrans(itemDetails, itemID, itemTransformations)

            itemList.append([itemID, itemName, itemPickup, itemQuality, itemType, game])

            #print(" ")
            spanIndex += 1
            listIndex += 1
        except:
            found = False

    bossUnlocks = filterBosses(bossUnlocks)

    outputToCSV(itemList, "ITEMS.csv", HEADER_ITEMS)
    outputToCSV(activeItemRecharge, "ACTIVE_ITEM_CHARGES.csv", HEADER_ACTIVE_ITEM)
    outputToCSV(passiveItemTags, "PASSIVE_ITEM_TAGS.csv", HEADER_PASSIVE_TAGS)
    outputToCSV(itemPools, "ITEM_POOLS.csv", HEADER_ITEM_POOLS)
    outputToCSV(itemTransformations, "ITEM_TRANSFORMATIONS.csv", HEADER_ITEM_TRANSFORMATIONS)
    outputToCSV(bossUnlocks, "BOSS_ITEM_UNLOCKS.csv", HEADER_BOSS_ITEM)
    outputToCSV(challengeUnlocks, "CHALLENGE_ITEM_UNLOCKS.csv", HEADER_CHALLENGE_ITEM)
    outputToCSV(miscUnlocks, "MISC_ITEM_UNLOCKS.csv", HEADER_MISC_ITEM)

# Scrapes Website for Game Trinkets
def scrapeTrinkets(game, div):
    trinketList = []
    bossUnlocks = []
    challengeUnlocks = []
    miscUnlocks = []


    # Repentance and Afterbirth Plus items denote the number of them using a span tag
    if game == REPENTANCE or AFTERBIRTH_PLUS: spanIndex = 1
    else: spanIndex = 0

    # Repentance trinkets div shares the same class as the items container
    if game == REPENTANCE: trinkets = soup.find_all("div", {"class": div})[1]
    else: trinkets = soup.find("div", {"class": div})

    found = True 

    while found == True:
        try:
            trinketDetails = []
            for li in trinkets.find_all("span")[spanIndex].find_all("p"):
                trinketDetails.append(li.get_text())

            trinketDetails.pop() # last paragraph is always the "tags"

            trinketName = trinketDetails[0]
            print(trinketName)

            trinketID = trinketDetails[1][11:]
            print(trinketID)

            trinketPickup = re.sub('"', "", trinketDetails[2])
            print(trinketPickup)

            if(trinketDetails[-1].startswith('UNLOCK:')):
                if "challenge" in trinketDetails[-1].lower().split(): # string *must* be singular; not plural
                    challengeUnlocks = challengeUnlock(trinketID, trinketDetails, challengeUnlocks)
                elif "defeating" in trinketDetails[-1].lower() or "beating" in trinketDetails[-1].lower():
                    bossUnlocks = bossUnlock(trinketID, trinketDetails, bossUnlocks)
                else:
                    miscUnlocks = miscUnlock(trinketID, trinketDetails, miscUnlocks)
                trinketDetails.pop()
            if(trinketDetails[-1].startswith(REPENTANCE.upper())):
                trinketDetails.pop()

            trinketList.append([trinketID, trinketName, trinketPickup, game])

            print(" ")
            spanIndex += 1
        except:
            found = False

    bossUnlocks = filterBosses(bossUnlocks)

    outputToCSV(trinketList, "TRINKETS.csv", HEADER_TRINKETS)
    outputToCSV(bossUnlocks, "BOSS_TRINKET_UNLOCKS.csv", HEADER_BOSS_TRINKET)
    outputToCSV(challengeUnlocks, "CHALLENGE_TRINKET_UNLOCKS.csv", HEADER_CHALLENGE_TRINKET)
    outputToCSV(miscUnlocks, "MISC_TRINKET_UNLOCKS.csv", HEADER_MISC_TRINKET)

try: 
    deleteFiles()
    page = urlopen(URL)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    scrapeItems(REBIRTH, "items-container")
    scrapeItems(AFTERBIRTH, "afterbirthitems-container")
    scrapeItems(AFTERBIRTH_PLUS, "afterbirthplusitems-container")
    scrapeItems(REPENTANCE, "repentanceitems-container")

    scrapeTrinkets(REBIRTH, "trinkets-container")
    scrapeTrinkets(AFTERBIRTH, "afterbirthtrinkets-container")
    scrapeTrinkets(AFTERBIRTH_PLUS, "afterbirthplustrinkets-container")
    scrapeTrinkets(REPENTANCE, "repentanceitems-container")
except:
    showError()


#for i in repentence_items:
 #     print(i)

#for i in activeItemRecharge:
 #     print(i)

#for i in itemPools:
 #     print(i)


#repentence_trinkets = soup.find_all("div", {"class": "repentanceitems-container"})[1]

