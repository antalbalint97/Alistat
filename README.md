# Vitastat Project
# Overview
Alistat is a data-driven project that analyzes Hungarian gastroculture using recipe and ingredient data scraped from nosalty.hu. The project combines over 70,000 recipes and 1,500 unique ingredients with detailed nutritional information to explore trends, build a recipe cost estimation model using daily price data, and eventually develop a lightweight interactive dashboard with Streamlit. Future goals include implementing a recommendation system and experimenting with custom health and cost metrics.

# Project Structure
```recipe_project/
│── data/               # Stores raw & cleaned CSV files
│── src/
│   ├── __init__.py     # init file
│   ├── main.py         # Main
│   ├── scraper.py      # Web scraping logic
│   ├── data_cleaner.py # Cleaning functions
│── notebooks/          # Jupyter notebooks for exploration
│── requirements.txt    # Python dependencies
│── README.md           # Project documentation
```
