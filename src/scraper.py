import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from datetime import datetime
from requests.exceptions import RequestException
import xml.etree.ElementTree as ET

class RecipeScraper:
    """Class for scraping full details of a recipe from Nosalty."""

    BASE_URL = "https://www.nosalty.hu/recept/"

    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()
        
    def extract_urls_from_xml(file_path, check_url_format=False, date_range=None):
        """
        Extracts recipe URLs from an XML file, optionally checking format and date range.
        
        Args:
            file_path (str): Path to the XML file.
            check_url_format (bool): If True, checks if the URL is valid.
            date_range (tuple): Optional (start_date, end_date) for filtering URLs by lastmod.
                                Format: ('YYYY-MM-DD', 'YYYY-MM-DD').

        Returns:
            list: List of valid URLs.
        """
        def is_valid_url(url):
            """Validates URL format."""
            pattern = r"^(http|https)://[^\s/$.?#].[^\s]*$"
            return re.match(pattern, url) is not None

        def is_within_date_range(date_text, start_date, end_date):
            """Checks if the date falls within the specified range."""
            try:
                date = datetime.strptime(date_text, "%Y-%m-%d")
                return start_date <= date <= end_date
            except ValueError:
                return False

        # Define XML namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        urls = []
        base_url = "https://www.nosalty.hu/recept/"
        for url in root.findall('ns:url', namespace):
            loc = url.find('ns:loc', namespace)
            lastmod = url.find('ns:lastmod', namespace)

            if loc is not None:
                url_text = loc.text
                if not url_text.startswith(base_url):
                    continue
                if check_url_format and not is_valid_url(url_text):
                    continue
                if date_range and lastmod is not None:
                    start_date, end_date = map(lambda d: datetime.strptime(d, "%Y-%m-%d"), date_range)
                    if not is_within_date_range(lastmod.text, start_date, end_date):
                        continue
                urls.append(url_text)

        return urls
    
    def get_soup(self):
        """Fetch and parse the webpage."""
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code != 200:
                return None
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException:
            return None

    def get_title(self):
        """Extracts the recipe title, or returns None if unavailable."""
        title_tag = self.soup.find('h1', class_='p-article__title -recipe pt-10 px-3 mb-5 d-block')
        return title_tag.text.strip() if title_tag else 'N/A' 

    def get_additional_info(self):
        """Extracts additional metadata related to the recipe."""
        info = []
        classes = [
            'a-text -fontSize-9 -fontColorSenary d-none d-sm-block',
            'a-text -fontSize-9 -fontColorQuaternary d-none d-sm-block',
            'a-link -fontColorPrimary -fontSize-16 -recipe pr-3 pl-2'  # Now capturing <a> elements
        ]

        for class_name in classes:
            elements = self.soup.find_all(['span', 'a'], class_=class_name)  # Look for both <span> and <a>
            for element in elements:
                info.append(element.text.strip())

        return ', '.join(info)

    def get_recipe_details(self):
        """Extracts the available recipe details: Time, Cost, and Difficulty."""
        details = {}

        # Define mapping from Hungarian labels to English keys
        rename_map = {
            "Idő": "Time",
            "Költség": "Cost",
            "Nehézség": "Difficulty"
        }

        # Locate all sections containing the relevant details
        detail_sections = self.soup.find_all('div', class_='p-recipe__detailsBody d-print-flex justify-content-end text-center mb-1 w-100')

        for section in detail_sections:
            label_tag = section.find('span', class_='p-recipe__detailsHeading d-block text-uppercase')  # Find label
            value_tag = section.find('div') or section.find('time') or section.find('span')  # Find actual value

            if label_tag and value_tag:
                label_text = label_tag.text.strip()
                value_text = value_tag.text.strip()

                # Store the extracted data with correct English labels
                if label_text in rename_map:
                    details[rename_map[label_text]] = value_text  # Correctly stores the value now

        return details

    
    def get_preparation_and_baking_time(self):
        """Extracts preparation and baking time from the recipe details list."""
        details = {}

        # Define label mapping from Hungarian to English
        rename_map = {
            "Előkészítés ideje": "Preparation Time",
            "Sütés ideje": "Baking Time"
        }

        # Locate the container that holds preparation and baking times
        details_section = self.soup.find('div', class_='p-recipe__detailsList')
        if not details_section:
            return details  # Return empty if section is missing

        # Find the list containing preparation and baking times
        list_section = details_section.find('ul', class_='m-list__list')
        if not list_section:
            return details  # Return empty if no list is found

        # Find all list items with the relevant class
        list_items = list_section.find_all('li', class_='m-list__item -simple -fontSize-18')

        for item in list_items:
            # Find the label (first span)
            label_tag = item.find('span')
            # Find the value (last span in the item)
            value_tag = item.find_all('span')[-1] if item.find_all('span') else None

            if label_tag and value_tag:
                label_text = label_tag.text.strip()
                value_text = value_tag.text.strip()

                # Store data using mapped labels
                if label_text in rename_map:
                    details[rename_map[label_text]] = value_text

        return details

    def get_portions(self):
        """Extracts the portion size from the input field."""

        # Find portions (now inside an input field with id="adag")
        portion_input = self.soup.find('input', {'id': 'adag'})
        portion_value = portion_input['value'].strip() if portion_input and 'value' in portion_input.attrs else 'N/A'

        return portion_value

    def get_nutrition_data(self):
        """Extracts all available nutrition details (Protein, Fat, Carbs, Water, and Minerals)."""
        nutrition_data = {}

        # Define the section titles and their corresponding nutrient names
        nutrition_sections = {
            'Fehérje': ['Összesen'],  # Protein
            'Zsír': ['Összesen', 'Telített zsírsav', 'Egyszeresen telítetlen zsírsav', 'Többszörösen telítetlen zsírsav', 'Koleszterin'],  # Fats
            'Szénhidrátok': ['Összesen', 'Cukor', 'Élelmi rost'],  # Carbs
            'VÍZ': ['Összesen'],  # Water
            'Ásványi anyagok': ['Cink', 'Szelén', 'Kálcium', 'Vas', 'Magnézium', 'Foszfor', 'Nátrium', 'Réz', 'Mangán'],  # Minerals
            'Vitaminok': ['A vitamin', 'B6 vitamin', 'B12 Vitamin', 'E vitamin', 'C vitamin', 'D vitamin', 'K vitamin',
                          'Tiamin - B1 vitamin', 'Riboflavin - B2 vitamin', 'Niacin - B3 vitamin', 'Pantoténsav - B5 vitamin',
                          'Folsav - B9-vitamin', 'Kolin', 'Retinol', 'α-karotin', 'β-karotin', 'β-crypt', 'Likopin', 'Lut-zea']  # Vitamins
        }

        # Loop through each section and extract relevant data
        for section, nutrients in nutrition_sections.items():
            tag = self.soup.find('h4', string=section)  # Find the section header (e.g., "Fehérje")

            if tag:
                list_section = tag.find_next('ul')  # Get the next <ul> after the section header

                if list_section:
                    for li in list_section.find_all('li'):  # Iterate through each <li> inside the section
                        for nutrient in (nutrients if isinstance(nutrients, list) else [nutrients]):
                            if nutrient in li.text:  # If the nutrient name appears in the text
                                value = li.find('div', class_='kc')  # Find the actual value
                                value_text = value.text.strip() if value else 'N/A'

                                # **Fix "Összesen" overwriting issue** by renaming it based on its section
                                if nutrient == "Összesen":
                                    renamed_nutrient = f"{section} - Összesen"  # Example: "Fehérje - Összesen"
                                else:
                                    renamed_nutrient = nutrient  # Keep other names unchanged

                                # Store the correctly named value
                                nutrition_data[renamed_nutrient] = value_text

        return nutrition_data


    def get_ingredients(self):
        """Extracts ingredient names, their full URLs, and amounts."""
        ingredients_list = []

        # Locate the correct section in the HTML
        ingredients_section = self.soup.find('ul', class_='m-list__list -nutrition')

        if ingredients_section:
            items = ingredients_section.find_all('li', class_='m-list__item p-2 -dotted -fontSize-18 d-flex justify-content-between pl-5')

            for item in items:
                # Extract quantity from span
                quantity_tag = item.find('span', class_='-fontSize-lg-16')
                quantity = quantity_tag.text.strip() if quantity_tag else 'N/A'

                # Extract ingredient name and URL from <a> tag
                ingredient_tag = item.find('a', class_='a-link -primaryHoverEffect -fontSize-18 -fontSize-lg-16')
                if ingredient_tag:
                    ingredient_name = ingredient_tag.text.strip()
                else:
                    ingredient_name = 'N/A'

                # Append as dictionary
                ingredients_list.append({
                    "Ingredient": ingredient_name,
                    "Quantity": quantity
                })
    
        return ingredients_list


    def to_dataframe(self):
        """Converts extracted recipe details to a pandas DataFrame."""
        return pd.DataFrame([{
            'Recipe name': self.get_title(),
             **self.get_recipe_details(),
            'Categories': self.get_additional_info(),
            **self.get_preparation_and_baking_time(),
            'Portions': self.get_portions(),           
            'Ingredients': self.get_ingredients(),
            **self.get_nutrition_data()
        }])