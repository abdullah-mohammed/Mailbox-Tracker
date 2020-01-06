import requests
from bs4 import BeautifulSoup
import re
import urlparse


class Coordinates():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


def getZipCodes (stateAbbreviation):
    # Add headers to make it seem like request coming from chrome browser otherwise request gets rejected
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    result = requests.get("https://www.unitedstateszipcodes.org/" + stateAbbreviation + "/",
                          headers=headers)  # make arr w states and sub into the state section for more
    src = result.content
    soup = BeautifulSoup(src, 'lxml')

    zipCodes = []
    prevVal = '-1' # the same href val was repeating 3 times so this eliminates that redundancy
    counter = 0  # keeps track of how many elements to remove from end of arr
    lastHttps = 0
    for div_tag in soup.find_all("div"):
        a_tag = div_tag.find('a')

        if a_tag is not None and "href" in a_tag.attrs:  # get href val if it exists
            href_val = a_tag.get("href")

            if "https" not in href_val and "#zips-list" not in href_val:  # filter out random href vals that arent zip codes
                href_val = re.sub('[/\\\\]', '', href_val)
                if href_val == prevVal:
                    continue

                if href_val is not '':  # make sure href is not nothing
                    # convert prev and cur to num and see which is greater
                    tempCurr = int(href_val)
                    tempPrev = int(prevVal)
                    if tempCurr < tempPrev:
                        break
                    zipCodes.append(href_val)
                    counter += 1
                    prevVal = href_val
            elif "https" in href_val:
                lastHttps = counter

    while (len(zipCodes) != lastHttps):  # removes the random numerical href values that were added to zipCodes
        zipCodes.pop()

    return zipCodes


def getCoordinates(zipCode): #returns array filled w Coordinate objects containing the latitude and longitude of each location
    coordinates = []
    websiteUrl = "https://tools.usps.com/go/POLocatorAction!input.action?address=" + zipCode + "&sWithin=100"
    #print websiteUrl

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    result = requests.get(websiteUrl, headers=headers)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')

    for tr_tag in soup.find_all("tr", {"class": "result"}):
        td_tag = tr_tag.find("td", {"class": "location"})
        div_tag = td_tag.find("div", {"class": "link"})
        a_tag = div_tag.find('a')
        href_val = a_tag.get("href")

        url = href_val
        parsed = urlparse.urlparse(url)
        latitude = urlparse.parse_qs(parsed.query)['latitude']
        longitude = urlparse.parse_qs(parsed.query)['longitude']

        coordinate = Coordinates(latitude, longitude)
        #print "latitude: " + str(coordinate.latitude)
        #print "longitude: " + str(coordinate.longitude)
        coordinates.append(coordinate)

    #print len(coordinates)
    return coordinates


def getAllCoordinates(zipCodes):
    all_coordinates = []

    for zipCode in zipCodes:
        coordinate_arr = getCoordinates(zipCode)
        all_coordinates.append(coordinate_arr)

    #print len(all_coordinates)
    return all_coordinates


def getStateAbbreviation(name):
    all_states = {
        "alabama": "al",
        "alaska": "ak",
        "arizona": "az",
        "arkansas": "ar",
        "california": "ca",
        "colorado": "co",
        "connecticut": "ct",
        "delaware": "de",
        "florida": "fl",
        "georgia": "ga",
        "hawaii": "hi",
        "idaho": "id",
        "illinois": "il",
        "indiana": "in",
        "iowa": "ia",
        "kansas": "ks",
        "kentucky": "ky",
        "louisiana": "la",
        "maine": "me",
        "maryland": "md",
        "massachusetts": "ma",
        "michigan": "mi",
        "minnesota": "mn",
        "mississippi": "ms",
        "missouri": "mo",
        "montana": "mt",
        "nebraska": "ne",
        "nevada": "nv",
        "new hampshire": "nh",
        "new jersey": "nj",
        "new mexico": "nm",
        "new york": "ny",
        "north carolina": "nc",
        "north dakota": "nd",
        "ohio": "oh",
        "oklahoma": "ok",
        "oregon": "or",
        "pennsylvania": "pa",
        "rhode island": "ri",
        "south carolina": "sc",
        "south dakota": "sd",
        "tennessee": "tn",
        "texas": "tx",
        "utah": "ut",
        "vermont": "vt",
        "virginia": "va",
        "washington": "wa",
        "west virginia": "wv",
        "wisconsin": "wi",
        "wyoming": "wy",
        "american samoa": "as",
        "district of columbia": "dc",
        "federated states of micronesia": "fm",
        "guam": "gu",
        "marshall islands": "mh",
        "northern mariana islands": "mp",
        "palau": "pw",
        "puerto rico": "pr",
        "virgin islands": "vi"
    }

    name = name.lower()
    return all_states[name]


def mainClass():
    name = getStateAbbreviation("Rhode Island")
    zipCodes = getZipCodes(name)
    all_coordinates = getAllCoordinates(zipCodes)


mainClass()
