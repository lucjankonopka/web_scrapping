import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys


# Progress bar function
# Source: https://stackoverflow.com/questions/3160699/python-progress-bar

def progressbar(it, prefix="", size=60, out=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)



# Selecting main page using Beautiful Soup:
page_url = "https://www.berlin.de/restaurants/stadtteile/"
page = requests.get(page_url)

soup = BeautifulSoup(page.content, 'html.parser')
#print(soup.prettify())

# Finding links for each cityzone:
page_list_zones = soup.find('ul', class_ = 'decoda-list')
list_all_zones = page_list_zones.find_all('a', href=True)

# Creating sublinks for each cityzone:
zone_sublinks = []

for el in list_all_zones:
    zone_sublinks.append(el['href'])

zone_sublinks

# Creating complete links for each cityzone:
zone_links = []

for zone in zone_sublinks:
    zone_page_url = 'https://www.berlin.de' + zone
    zone_links.append(zone_page_url)

zone_links


# Creating empty list for dictionaries with restaurant informations:
all_restaurants_list = []


# Finding links for each restaurant in each cityzone:
def find_restaurant_links(zone_link):
    # Opening page of each restaurant:
    zone_page = requests.get(zone_link)
    local_soup = BeautifulSoup(zone_page.content, 'html.parser')
    #print(local_soup.prettify())
    # Finding links for each restarant from each zone by searching specific "text" in hrefs:
    restaurant_sublink = local_soup.find_all('a', href=lambda href: href and "restaurants/adressen" in href and "html" in href, title=False)

    # Creating temporary list of sublinks for each zone:
    subzone_sublinks = []

    # Adding all sublinks info list:
    for el in restaurant_sublink:
        subzone_sublinks.append(el['href'])

    # Adding "htpps - prefix" for each link:
    for zone in subzone_sublinks:
        zone_page_url = 'https://www.berlin.de' + zone
        all_restaurants_list.append(zone_page_url)
    #print(len(all_restaurants_list))

    return all_restaurants_list


# Looping through all zones:
for link in zone_links:
    find_restaurant_links(link)

# Number of the restaurants:
len(all_restaurants_list)

# Creating the empty main_list where all info dictionaries will be collected:
main_list = []


# Getting dictionaries data - name, type of restaurant, address, zip-code & phone: 
def restaurant_info(restaurant):
    
    # Exploring restaurant subpage:
    restaurant_page = requests.get(restaurant)
    local_soup = BeautifulSoup(restaurant_page.content, 'html.parser')
    #print(local_soup.prettify())
   
    # Finding data field:
    restaurant_data = local_soup.find('div', class_ = 'befi-address')

    # Excluding name, address, zip code and phone from field:
    restaurant_name_tag = restaurant_data.find('div')
    restaurant_name = restaurant_name_tag.text.strip()

    restaurant_address_tag = restaurant_name_tag.find_next('div')
    restaurant_address = restaurant_address_tag.text.strip()

    restaurant_zip_tag = restaurant_data.find('span')
    restaurant_zip = restaurant_zip_tag.text.strip()

    restaurant_phone_tag = restaurant_zip_tag.find_next('a')
    restaurant_phone = restaurant_phone_tag.text.strip()
    # Checking if the phone number exists, otherwise writing "None" as a value:
    if not restaurant_phone.startswith("("):
        restaurant_phone = 'None'

    # Finding the restaurant type in http address (link):
    text = (restaurant.split("adressen/",1)[1]).split("/",1)[0]

    # Splitting and merging text to get correct string type:
    splittet_text = text.split('-',1)
    if len(splittet_text) == 1:
        new_name = splittet_text[0].capitalize()
    else:
        new_name = splittet_text[0].capitalize() + ' ' + splittet_text[1].capitalize()


    # Creating dictionary with restaurant info according new created dataset:
    restaurant_data[restaurant] = {'Name': restaurant_name,
                        'Restaurant Type': new_name,
                        'Address': restaurant_address,
                        'Zip Code': restaurant_zip,
                        'Phone': restaurant_phone}
    
    return restaurant_data[restaurant]


# Looping through all restaurants and appending infos to new dataset:
start_time = time.time()

for i in progressbar(range(len(all_restaurants_list)), "Computing: ", 50):
    new_info = restaurant_info(all_restaurants_list[i])
    # Appending the dictionary to the main_list:
    main_list.append(new_info)

end_time =  time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {round(elapsed_time,2)}s")

# Checking list format and length:
main_list
len(main_list)

# Creating new dataset for restaurants:
table_view = {'Name': [], 'Restaurant_Type': [], 'Address': [], 'Zip_Code': [], 'Phone': []}

dataset_restaurants = pd.DataFrame.from_records(main_list)

# Exporting dataset as .csv file:
dataset_restaurants.to_csv('dataset_berlin_restaurants.csv', index=False)