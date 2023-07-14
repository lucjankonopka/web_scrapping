from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


# Functions for getting detail data
# Function to extract restaurant name
def get_name(soup):
    try:
        link_cityzone = soup.find("section", class_="block befi-address")
        restaurant_name_tag = link_cityzone.find("div")
        restaurant_name = restaurant_name_tag.text.strip()

    except AttributeError:
        restaurant_name = ""

    return restaurant_name


# Function to extract restaurant address
def get_address(soup):
    try:
        link_cityzone = soup.find("section", class_="block befi-address")
        restaurant_name_tag = link_cityzone.find("div")
        restaurant_address_tag = restaurant_name_tag.find_next("div")
        restaurant_address = restaurant_address_tag.text.strip()

    except AttributeError:
        restaurant_address = ""

    return restaurant_address


# Function to extract restaurant zip
def get_zip(soup):
    try:
        link_cityzone = soup.find("section", class_="block befi-address")
        restaurant_zip_tag = link_cityzone.find("span")
        restaurant_zip = restaurant_zip_tag.text.strip()

    except AttributeError:
        restaurant_zip = ""

    return restaurant_zip


# Function to extract restaurant phone
def get_phone(soup):
    try:
        link_cityzone = soup.find("section", class_="block befi-address")
        restaurant_zip_tag = link_cityzone.find("span")
        restaurant_phone_tag = restaurant_zip_tag.find_next("a")
        restaurant_phone = restaurant_phone_tag.text.strip()
        if not restaurant_phone.startswith("("):
            restaurant_phone = "None"

    except AttributeError:
        restaurant_phone = "None"

    return restaurant_phone


# Function to extract restaurant type
def get_type(link):
    try:
        # Finding the restaurant type in http address (link)
        text = (link.split("adressen/", 1)[1]).split("/", 1)[0]

        # Splitting and merging text to get correct string type
        splittet_text = text.split("-", 1)
        if len(splittet_text) == 1:
            restaurant_type = splittet_text[0].capitalize()
        else:
            restaurant_type = (
                splittet_text[0].capitalize() + " " + splittet_text[1].capitalize()
            )

    except AttributeError:
        restaurant_type = "None"

    return restaurant_type


###

if __name__ == "__main__":
    # Headers for request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5",
    }

    # Selecting main page
    page_url = "https://www.berlin.de/restaurants/stadtteile/"
    page = requests.get(page_url, headers=HEADERS)

    soup = BeautifulSoup(page.content, "html.parser")

    # Finding links for each cityzone
    page_list_zones = soup.find_all("h3", class_="title")

    # Iterate over the <h3> elements and find the nested <a> elements
    # and creating sublinks for each cityzone
    zone_sublinks = []

    for h3 in page_list_zones:
        a_elements = h3.find_all("a")
        for a in a_elements:
            zone_sublinks.append(a["href"])

    # Getting all subzones placed just in Berlin
    zone_sublinks = zone_sublinks[:23]

    # Creating complete links for each cityzone
    zone_links = []

    for zone in zone_sublinks:
        zone_page_url = "https://www.berlin.de" + zone
        zone_links.append(zone_page_url)

    # Creating empty list for links of all restaurant separately
    all_restaurants_list = []

    # Finding links for each restaurant in each cityzone
    def find_restaurant_links(zone_link):
        # Opening page of each restaurant
        zone_page = requests.get(zone_link)
        local_soup = BeautifulSoup(zone_page.content, "html.parser")
        # print(local_soup.prettify())
        # Finding links for each restarant from each zone by searching specific "text" in hrefs
        restaurant_sublink = local_soup.find_all(
            "a",
            href=lambda href: href
            and "restaurants/adressen" in href
            and "html" in href,
        )

        # Creating temporary list of sublinks for each zone
        subzone_sublinks = []

        # Adding all sublinks info list
        for el in restaurant_sublink:
            subzone_sublinks.append(el["href"])

        # Adding "htpps - prefix" for each link
        for zone in subzone_sublinks:
            zone_page_url = "https://www.berlin.de" + zone
            all_restaurants_list.append(zone_page_url)
        # print(len(all_restaurants_list))

        return all_restaurants_list

    # Looping through all zones
    for link in zone_links:
        find_restaurant_links(link)

    # Number of the restaurants
    len(all_restaurants_list)

    # Creating the dictionary schema
    result: Dict[str, List[str]] = {
        "Name": [],
        "Restaurant_Type": [],
        "Address": [],
        "Zip_Code": [],
        "Phone": [],
    }

    # Looping for extracting details from each link
    for link in all_restaurants_list:
        new_page = requests.get(link, headers=HEADERS)
        new_soup = BeautifulSoup(new_page.content, "html.parser")

        result["Name"].append(get_name(new_soup))
        result["Restaurant_Type"].append(get_type(link))
        result["Address"].append(get_address(new_soup))
        result["Zip_Code"].append(get_zip(new_soup))
        result["Phone"].append(get_phone(new_soup))

    # Creating pandas dataframe
    dataset_restaurants = pd.DataFrame.from_dict(result)

    # Exporting dataset as .csv file
    dataset_restaurants.to_csv("dataset_berlin_restaurants.csv", index=False)
