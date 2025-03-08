# Recipe Project
# Overview
The Recipe Project is a data-driven application that scrapes, cleans, analyzes, and models recipe data to gain insights about ingredients, nutritional values, and costs. The project is structured to facilitate data collection, database management, and machine learning applications.

# Project Structure
```recipe_project/
│── data/               # Stores raw & cleaned CSV files
│── sql/                # SQL scripts to create & populate database
│── src/
│   ├── __init__.py     # init file
│   ├── main.py         # Main
│   ├── scraper.py      # Web scraping logic
│   ├── data_cleaner.py # Cleaning functions
│   ├── db_manager.py   # Handles SQL database connection
│   ├── analysis.py     # SQL & Pandas analysis
│   ├── model.py        # Machine learning models
│── notebooks/          # Jupyter notebooks for exploration
│── docker/             # Docker setup files
│── requirements.txt    # Python dependencies
│── README.md           # Project documentation
```
# Features

Web Scraping: Extracts recipe data from websites.
Data Cleaning: Removes duplicates, handles missing values.
SQL Database Management: Stores recipes in a structured format.
Data Analysis: Uses SQL and Pandas for insights.
Machine Learning Models: Predicts recipe characteristics.
Jupyter Notebooks: Exploratory data analysis.
