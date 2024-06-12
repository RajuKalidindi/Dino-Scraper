from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient

# Establish a connection to the MongoDB server
client = MongoClient('mongodb://localhost:27017/')

# Select the database and collection
db = client['dinosaur_db']
collection = db['dinosaur_collection']

base_url = 'https://www.nhm.ac.uk'
html_text = requests.get(base_url + '/discover/dino-directory/name/name-az-all.html').text
soup = BeautifulSoup(html_text, 'lxml')

dinosaurs_list = soup.find_all('p', class_='dinosaurfilter--name')

for dinosaur in dinosaurs_list:
    dinosaur_name = dinosaur.text.strip()

    dinosaur_link = base_url + dinosaur.find_parent('a')['href']
    
    dinosaur_page_text = requests.get(dinosaur_link).text
    dinosaur_page_soup = BeautifulSoup(dinosaur_page_text, 'lxml')

    try:
        dinosaur_name_info = dinosaur_page_soup.find('dl', class_='dinosaur--name-description')
        dinosaur_pronunciation = dinosaur_name_info.find('dd', class_='dinosaur--pronunciation').text
        dinosaur_name_meaning = dinosaur_name_info.find('dd', class_='dinosaur--meaning').text
    except AttributeError:
        dinosaur_pronunciation = dinosaur_name_meaning = ''

    # Find the image tag
    try:
        dinosaur_image_tag = dinosaur_page_soup.find('img', class_='dinosaur--image')
        dinosaur_image_url = dinosaur_image_tag['src']
    except AttributeError:
        dinosaur_image_url = ''

    try:
        dinosaur_description_info = dinosaur_page_soup.find('dl', class_='dinosaur--description dinosaur--list')
        dd_elements = dinosaur_description_info.find_all('dd')
        dinosaur_type = dd_elements[0].text.strip().replace('\n', '') if len(dd_elements) > 0 else ''
        dinosaur_length = dd_elements[1].text.strip().replace('\n', '') if len(dd_elements) > 1 else ''
        dinosaur_weight = dd_elements[2].text.strip().replace('\n', '') if len(dd_elements) > 2 else ''
    except AttributeError:
        dinosaur_type = dinosaur_length = dinosaur_weight = ''

    try:
        dinosaur_info = dinosaur_page_soup.find('dl', class_='dinosaur--info dinosaur--list')
        dd_elements = dinosaur_info.find_all('dd')
        dinosaur_diet = dd_elements[0].text.strip().replace('\n', '') if len(dd_elements) > 0 else ''
        dinosaur_when_it_lived = dd_elements[1].text.strip().replace('\n', '') if len(dd_elements) > 1 else ''
        dinosaur_found_in = dd_elements[2].text.strip().replace('\n', '') if len(dd_elements) > 2 else ''
    except AttributeError:
        dinosaur_diet = dinosaur_when_it_lived = dinosaur_found_in = ''

    # Find and join all the paragraphs into one string
    try:
        dinosaur_description_div = dinosaur_page_soup.find('div', class_='dinosaur--content-container')
        dinosaur_description_paragraphs = dinosaur_description_div.find_all('p')
        dinosaur_description = ' '.join(paragraph.text for paragraph in dinosaur_description_paragraphs)
    except AttributeError:
        dinosaur_description = ''

    # Create a dictionary with the data
    dinosaur_data = {
        'name': dinosaur_name,
        'pronunciation': dinosaur_pronunciation,
        'name_meaning': dinosaur_name_meaning,
        'image_url': dinosaur_image_url,
        'type': dinosaur_type,
        'length': dinosaur_length,
        'weight': dinosaur_weight,
        'diet': dinosaur_diet,
        'when_it_lived': dinosaur_when_it_lived,
        'found_in': dinosaur_found_in,
        'description': dinosaur_description
    }

    # Filter out parameters with empty strings
    dinosaur_data = {k: v for k, v in dinosaur_data.items() if v != ''}

    # Update the document if it exists, insert it if it doesn't
    collection.update_one({'name': dinosaur_name}, {'$set': dinosaur_data}, upsert=True)

    



