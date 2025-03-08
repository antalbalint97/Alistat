import re

class DataProcessor:
    """Class for processing XML data and cleaning nutritional data."""

    def __init__(self):
        """Initialize the DataProcessor class."""
        pass  # No instance variables needed, as all methods are static

    @staticmethod
    def clean_value(value):
        """
        Cleans individual value by:
        - Removing unwanted characters
        - Converting to appropriate numeric format

        Args:
            value (str): The value to clean.

        Returns:
            float or str: Cleaned numeric value if applicable, otherwise original string.
        """
        if isinstance(value, str):
            value = value.strip().lower()
            has_number = any(char.isdigit() for char in value)

            if has_number:
                if 'mg' in value:
                    return float(value.replace('mg', '').strip()) / 1000
                elif 'µg' in value:
                    return float(value.replace('µg', '').strip()) / 1_000_000
                elif 'micro' in value:
                    return float(value.replace('micro', '').strip()) / 1_000_000
                elif 'g' in value:
                    return float(value.replace('g', '').strip())
                elif 'perc' in value:
                    return float(value.replace('perc', '').strip())
                elif '°c' in value:
                    return float(value.replace('°c', '').strip())

        return value  # Return unchanged if not numeric

    @staticmethod
    def clean_ingredient_value(value):
        """
        Cleans an individual value by:
        - Removing units ('g', 'mg', 'µg', 'micro', 'mcg')
        - Converting to float and scaling appropriately
        - Handling cases where unexpected characters appear

        Args:
        value (str): The original value.

        Returns:
        float or original value if conversion fails.
        """
        if isinstance(value, str):
            value = value.strip().lower()

            # Extract numeric part using regex
            num_match = re.search(r"[-+]?\d*\.?\d+", value)
            if not num_match:
                return value  # Return as-is if no number is found

            num = float(num_match.group())  # Extract the numerical value

            # Check for unit and scale accordingly
            if "mg" in value:
                return num / 1000  # Convert mg to g
            elif "µg" in value or "mcg" in value or "micro" in value:
                return num / 1000000  # Convert µg/micro/mcg to g
            elif "g" in value:
                return num  # Already in g, no change needed

            return num  # If no unit is found, assume the number is correct

        return value  # Return original if not a string


    @staticmethod
    def clean_nutrition_data(df):
        """
        Cleans the nutrition data by:
        - Removing 'g', 'mg', 'micro', 'perc', and '°C'
        - Converting appropriate units to float

        Args:
            df (pd.DataFrame): DataFrame containing nutritional data.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        excluded_indexes = [0, 1, 3, 4, 5, 10]
        excluded_columns = ['Fogás', 'Konyha', 'Nehézség', 'Elkészítési idő', 'Szakács elkészítette', 
                            'Speciális étrendek', 'Vegetáriánus', 'Alkalom', 'Költség egy főre', 
                            'Konyhatechnológia']
        
        for index, col in enumerate(df.columns):
            if index in excluded_indexes or col in excluded_columns:
                continue
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: DataProcessor.clean_value(x))
        
        return df
   
    @staticmethod
    def clean_nutrition_data_ingredients(df):
        """
        Cleans numerical nutrition data by:
        - Removing units like 'g', 'mg', 'µg', 'micro'
        - Converting to float and scaling appropriately
        - Keeping non-numeric columns unchanged

        Args:
        df (pd.DataFrame): The dataframe containing nutritional data.

        Returns:
        pd.DataFrame: Cleaned dataframe with corrected values.
        """
        excluded_columns = ['Alapanyag neve', 'Elsődleges kategória', 'Másodlagos kategória']

        for col in df.columns:
            if col in excluded_columns:
                continue  # Skip non-numeric columns
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: DataProcessor.clean_value(x))
        return df