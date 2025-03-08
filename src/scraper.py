import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from datetime import datetime
import xml.etree.ElementTree as ET


class RecipeScraper:
    """Class for scraping full details of a recipe from Nosalty."""

    BASE_URL = "https://www.nosalty.hu/recept/"

    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    @staticmethod
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
        for url in root.findall('ns:url', namespace):
            loc = url.find('ns:loc', namespace)
            lastmod = url.find('ns:lastmod', namespace)

            if loc is not None:
                url_text = loc.text
                if not url_text.startswith(RecipeScraper.BASE_URL):
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
            response.raise_for_status()  # Raise HTTP errors
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException:
            return None

    def get_title(self):
        """Extracts the recipe title."""
        if not self.soup:
            return 'N/A'
        title_tag = self.soup.find('h1', class_='p-article__title -recipe pt-10 px-3 mb-5 d-block')
        return title_tag.text.strip() if title_tag else 'N/A'

    def get_recipe_details(self):
        """Extracts the available recipe details (Time, Cost, Difficulty)."""
        details = {}
        rename_map = {
            "Idő": "Time",
            "Költség": "Cost",
            "Nehézség": "Difficulty"
        }

        if not self.soup:
            return details

        detail_sections = self.soup.find_all('div', class_='p-recipe__detailsBody')

        for section in detail_sections:
            label_tag = section.find('span', class_='p-recipe__detailsHeading')
            value_tag = section.find('div') or section.find('time') or section.find('span')

            if label_tag and value_tag:
                label_text = label_tag.text.strip()
                value_text = value_tag.text.strip()
                if label_text in rename_map:
                    details[rename_map[label_text]] = value_text

        return details

    def to_dataframe(self):
        """Converts extracted recipe details to a pandas DataFrame."""
        return pd.DataFrame([{
            'Recipe name': self.get_title(),
            **self.get_recipe_details()
        }])


class IngredientScraper:
    """Class for scraping full details of an ingredient from Nosalty."""

    BASE_URL = "https://www.nosalty.hu/alapanyag/"

    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    @staticmethod
    def extract_urls_from_xml(file_path, check_url_format=False, date_range=None):
        """
        Extracts ingredient URLs from an XML file, optionally checking format and date range.

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
        for url in root.findall('ns:url', namespace):
            loc = url.find('ns:loc', namespace)
            lastmod = url.find('ns:lastmod', namespace)

            if loc is not None:
                url_text = loc.text
                if not url_text.startswith(IngredientScraper.BASE_URL):
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
        """Fetch and parse the ingredient webpage."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException:
            return None

    def get_ingredient_name(self):
        """Extracts the ingredient name from metadata."""
        if not self.soup:
            return "N/A"
        meta_tag = self.soup.find("meta", property="og:title")
        return meta_tag["content"] if meta_tag and "content" in meta_tag.attrs else "Unknown Ingredient"

    def to_dataframe(self):
        """Converts extracted ingredient details into a pandas DataFrame."""
        return pd.DataFrame([{
            "Ingredient Name": self.get_ingredient_name()
        }])
