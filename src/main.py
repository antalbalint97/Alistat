import time
import pandas as pd
import traceback
from datetime import datetime
from src.scraper import RecipeScraper
from src.scraper import IngredientScraper
from src.data_cleaner import DataProcessor

# Define XML file paths
file_paths = [
    r'C:\Users\Bálint\Desktop\Asztal\Projekt\inputs\receptek_url.xml',
    r'C:\Users\Bálint\Desktop\Asztal\Projekt\inputs\receptek_url_2.xml',
    r'C:\Users\Bálint\Desktop\Asztal\Projekt\inputs\receptek_url_3.xml'
]

# Extract and categorize URLs
recipe_urls = []
ingredient_urls = []

for file_path in file_paths:
    recipe_urls.extend(RecipeScraper.extract_urls_from_xml(file_path, check_url_format=True))
    ingredient_urls.extend(IngredientScraper.extract_urls_from_xml(file_path, check_url_format=True))

# Function to process URLs and scrape data
def process_scraping(urls, scraper_class, category):
    """Scrape URLs using the given scraper class and store results."""    
    scraped_data = []
    success_count = 0
    total_count = len(urls)

    print(f"Starting to scrape {total_count} {category} URLs...")

    for i, url in enumerate(urls, start=1):
        try:
            scraper = scraper_class(url)
            scraped_df = scraper.to_dataframe()

            if scraped_df is not None and not scraped_df.empty:
                scraped_data.append(scraped_df)
                success_count += 1  # Count only successful scrapes

        except Exception as e:
            print(f"Error processing {url}: {e}")
            print(traceback.format_exc())

        # Print periodic progress updates
        if i % 500 == 0 or i == total_count:
            elapsed_time = time.time() - start_time
            print(f"Processed {i}/{total_count} {category} URLs. "
                  f"Successful: {success_count}. Elapsed time: {elapsed_time:.2f} seconds.")

    return scraped_data

start_time = time.time()
current_date = datetime.now().strftime("%Y_%m_%d")
# Process and scrape recipe data
recipe_data = process_scraping(recipe_urls, RecipeScraper, "recipe")

# Convert and clean recipe data
if recipe_data:
    final_recipe_df = pd.concat(recipe_data, ignore_index=True)
    final_recipe_df_cleaned = DataProcessor.clean_nutrition_data(final_recipe_df)

    # Save to CSV
    recipe_output_path = rf"C:\Users\Bálint\Desktop\Asztal\Projekt\outputs\recipes_scraping_{current_date}.csv"
    final_recipe_df_cleaned.to_csv(recipe_output_path, index=False)
    print(f"Saved cleaned recipe data to {recipe_output_path}")


# Process and scrape ingredient data
ingredient_data = process_scraping(ingredient_urls, IngredientScraper, "ingredient")

# Convert and clean ingredient data
if ingredient_data:
    final_ingredient_df = pd.concat(ingredient_data, ignore_index=True)
    final_ingredient_df_cleaned = DataProcessor.clean_nutrition_data_ingredients(final_ingredient_df)

    # Save to CSV
    ingredient_output_path = rf"C:\Users\Bálint\Desktop\Asztal\Projekt\outputs\ingredients_scraping_{current_date}.csv"
    final_ingredient_df_cleaned.to_csv(ingredient_output_path, index=False)
    print(f"Saved cleaned ingredient data to {ingredient_output_path}")

# Final execution time
end_time = time.time()
print(f"Total execution time: {end_time - start_time:.2f} seconds")
