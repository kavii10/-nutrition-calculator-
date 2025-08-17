# Nutrition Finder

A multilingual nutrition information web application that lets users enter a recipe name and get a detailed nutrition breakdown of the recipe ingredients. The nutrient names are translated automatically based on the detected language of the recipe.

The app uses USDA nutrient and food datasets combined with a recipe Excel file containing recipes in multiple languages.

---

## Features

- Supports recipe names in multiple languages (English, Tamil, Hindi, Telugu, Kannada, Malayalam, French, Spanish, German)
- Automatically detects recipe language for accurate nutrition data and nutrient name translation
- Uses fuzzy matching to link recipe ingredients to USDA food items
- Displays a clear nutrition table with translated nutrient names and units
- Easy web interface using Flask
- Supports CSV/Excel datasets for food and recipe data

---

## Project Structure

nutrition_finder/
├── app.py # Flask web server and API
├── nutrition_core.py # Core nutrition calculation & translation logic
├── food.csv # USDA food dataset
├── nutrient.csv # USDA nutrient definitions
├── food_nutrient.csv # USDA food-nutrient relations
├── Recipe App Dataset.xlsx # Recipe dataset (multilingual)
├── requirements.txt # Python dependencies
├── templates/
│ └── index.html # Frontend page
└── static/
└── style.css # Frontend styles 
---

## Installation

Make sure you have Python 3.7+ installed.

Install required libraries:
pip install -r requirements.txt

---

## Running Locally

Run the Flask app:
python app.py


Open a browser and visit:
http://127.0.0.1:5000


Enter a recipe name (in any supported language) and press "Find Nutrition".

---

## Deploying to Render

1. Push your project to GitHub.
2. Create a new Web Service on [Render.com](https://render.com).
3. Connect your GitHub repository.
4. Use `gunicorn app:app` as the start command.
5. Wait for deployment to complete.
6. Access your live URL to use the app.

---

## Usage Notes

- Ensure the USDA CSV files and Recipe Excel file are placed in the project root.
- Recipe names should exactly match entries in your recipe dataset for best results.
- Nutrient names will be displayed in the recipe’s language automatically.
- Modify `nutrition_core.py` to add support for additional languages or nutrients as needed.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- USDA Food and Nutrient Databases
- Flask Web Framework
- TheFuzz library for fuzzy matching
