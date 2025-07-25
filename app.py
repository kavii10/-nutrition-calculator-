from flask import Flask, request, jsonify
import pandas as pd
import re
from thefuzz import process

# ------------------- Load Data at Startup ------------------- #

food_df = pd.read_csv('food.csv')
nutrient_df = pd.read_csv('nutrient.csv')
food_nutrient_df = pd.read_csv('food_nutrient.csv', low_memory=False)
xls = pd.read_excel('Recipe App Dataset.xlsx', sheet_name=None)

food_df['desc_clean'] = food_df['description'].str.lower().str.strip()
nutrient_df = nutrient_df[nutrient_df['rank'] != 999999].copy()
nutrient_map = nutrient_df.set_index('id')[['name', 'unit_name']].to_dict('index')

focus_nutrients = [
    "Energy", "Energy (Atwater General Factors)", "Energy (Atwater Specific Factors)",
    "Protein", "Total lipid (fat)", "Carbohydrate, by difference", "Fiber, total dietary",
    "Sugars, total including NLEA", "Cholesterol", "Sodium, Na",
    "Calcium, Ca", "Iron, Fe", "Potassium, K"
]
name_alias = {
    "Energy": "Calories", "Energy (Atwater General Factors)": "Calories",
    "Energy (Atwater Specific Factors)": "Calories", "Protein": "Protein",
    "Total lipid (fat)": "Fat", "Carbohydrate, by difference": "Carbohydrates",
    "Fiber, total dietary": "Fiber", "Sugars, total including NLEA": "Sugar",
    "Cholesterol": "Cholesterol", "Sodium, Na": "Sodium",
    "Calcium, Ca": "Calcium", "Iron, Fe": "Iron", "Potassium, K": "Potassium"
}

# Multilingual output translation
nutrient_name_translations = {
    'en': {'Calories': 'Calories','Protein':'Protein','Fat':'Fat','Carbohydrates':'Carbohydrates',
        'Fiber':'Fiber','Sugar':'Sugar','Cholesterol':'Cholesterol','Sodium':'Sodium','Calcium':'Calcium','Iron':'Iron','Potassium':'Potassium'},
    'ta': {'Calories': 'கேலரிகள்','Protein': 'புரதம்','Fat': 'கொழுப்பு','Carbohydrates': 'கார்போஹைட்ரேட்டுகள்','Fiber': 'நார்','Sugar': 'சர்க்கரை','Cholesterol': 'கொலஸ்ட்ரால்','Sodium': 'சோடியம்','Calcium': 'கால்சியம்','Iron': 'இரும்பு','Potassium': 'பொட்டாசியம்'},
    'hn': {'Calories':'कैलोरी','Protein':'प्रोटीन','Fat':'वसा','Carbohydrates':'कार्बोहाइड्रेट','Fiber':'रेशा','Sugar':'शुगर','Cholesterol':'कोलेस्ट्रॉल','Sodium':'सोडियम','Calcium':'कैल्शियम','Iron':'लोहा','Potassium':'पोटैशियम'},
    'te': {'Calories':'కాలొరీలు','Protein':'ప్రోటీన్','Fat':'కొలెస్టరాల్','Carbohydrates':'కార్బోహైడ్రేట్లు','Fiber':'ఫైబర్','Sugar':'చక్కెర','Cholesterol':'కొలెస్ట్రాల్','Sodium':'సోడియం','Calcium':'కాల్షియం','Iron':'ఉక్కు','Potassium':'పొటాషియం'},
    'kn': {'Calories':'ಕ್ಯಾಲೋರಿ','Protein':'ಪ್ರೋಟೀನ್','Fat':'ಕಬ್ಬು','Carbohydrates':'ಕಾರ್ಬೋಹೈಡ್ರೇಟ್‌ಗಳು','Fiber':'ನಾರು','Sugar':'ಬೆಲ್ಲ','Cholesterol':'ಕೋಲೆಸ್ಟ್ರಾಲ್','Sodium':'ಸೋಡಿಯಂ','Calcium':'ಕ್ಯಾಲ್ಸಿಯಂ','Iron':'ಇರೀಚು','Potassium':'ಪೋಟಾಶಿಯಂ'},
    'kl': {'Calories':'ക്യാലറി','Protein':'പ്രോട്ടീൻ','Fat':'കൊളസ്ട്രാള്','Carbohydrates':'കാർബോഹൈഡ്രേറ്റുകൾ','Fiber':'നാരം','Sugar':'പഞ്ചസാര','Cholesterol':'കൊളസ്ട്രാൾ','Sodium':'സോഡിയം','Calcium':'കാല്ഷ്യം','Iron':'ലോഹം','Potassium':'പൊട്ടാസ്യം'},
    'french': {'Calories':'Calories','Protein':'Protéines','Fat':'Lipides','Carbohydrates':'Glucides','Fiber':'Fibres','Sugar':'Sucres','Cholesterol':'Cholestérol','Sodium':'Sodium','Calcium':'Calcium','Iron':'Fer','Potassium':'Potassium'},
    'spanish': {'Calories':'Calorías','Protein':'Proteínas','Fat':'Grasa','Carbohydrates':'Carbohidratos','Fiber':'Fibra','Sugar':'Azúcar','Cholesterol':'Colesterol','Sodium':'Sodio','Calcium':'Calcio','Iron':'Hierro','Potassium':'Potasio'},
    'german': {'Calories':'Kalorien','Protein':'Eiweiß','Fat':'Fett','Carbohydrates':'Kohlenhydrate','Fiber':'Ballaststoffe','Sugar':'Zucker','Cholesterol':'Cholesterin','Sodium':'Natrium','Calcium':'Kalzium','Iron':'Eisen','Potassium':'Kalium'}
}

LANGUAGE_SUFFIX = {
    "TamilName": "ta", "hindiName": "hn", "malayalamName": "kl",
    "kannadaName": "kn", "teluguName": "te", "frenchName": "french",
    "spanishName": "spanish", "germanName": "german"
}

def translate_nutrient_name(nutrient, lang_code):
    return nutrient_name_translations.get(lang_code, {}).get(nutrient, nutrient)

def detect_language(recipe_name):
    for sheet_name, df in xls.items():
        for lang_col in LANGUAGE_SUFFIX:
            if lang_col in df.columns:
                match = df[df[lang_col].astype(str).str.lower().str.strip() == recipe_name.lower()]
                if not match.empty:
                    return sheet_name, lang_col, LANGUAGE_SUFFIX[lang_col], match
        for col in ["name", "Name"]:
            if col in df.columns:
                match = df[df[col].astype(str).str.lower().str.strip() == recipe_name.lower()]
                if not match.empty:
                    return sheet_name, col, "en", match
    return None, None, None, None

def parse_ingredient_line(line):
    items = [i.strip() for i in re.split(r",|\n", str(line)) if i.strip()]
    result = []
    for item in items:
        match = re.match(r"([\d\.\/]+)?\s*([a-zA-Z]*)\s*(.+)", item)
        if match:
            qty = match.group(1)
            try:
                amount = eval(qty) if qty else 1
            except:
                amount = 1
            result.append({
                "amount": amount,
                "unit": match.group(2).strip(),
                "name": match.group(3).strip(),
                "formattedAmount": f"{round(amount, 2)}"
            })
    return result

def find_english_ingredient_column(row):
    for col in row.index:
        if 'ingredient' in col.lower() and 'english' in col.lower():
            return col
    for col in row.index:
        if col.lower() == 'ingredients_en':
            return col
    return None

def convert_to_grams(qty, unit):
    u = unit.lower()
    if u in ['g', 'gram', 'grams']:
        return qty
    elif u in ['kg', 'kilogram', 'kilograms']:
        return qty * 1000
    elif u in ['mg', 'milligram', 'milligrams']:
        return qty / 1000
    else:
        return qty

def fuzzy_match(ingredient, choices, threshold=60):
    result = process.extractOne(ingredient, choices, score_cutoff=threshold)
    return result[0] if result else None

def get_nutrition(ingredient, quantity, unit):
    cleaned_name = ingredient.lower().strip()
    best_match = fuzzy_match(cleaned_name, food_df['desc_clean'])
    if not best_match:
        return {}
    matched_rows = food_df[food_df['desc_clean'] == best_match]
    best_fdc_id = None
    best_score = 0
    for fid in matched_rows['fdc_id'].values:
        f_nutr = food_nutrient_df[food_nutrient_df['fdc_id'] == fid]
        count = sum(1 for _, r in f_nutr.iterrows() if nutrient_map.get(r['nutrient_id'], {}).get('name') in focus_nutrients)
        if count > best_score:
            best_score = count
            best_fdc_id = fid
    if not best_fdc_id:
        return {}
    f_nutr = food_nutrient_df[food_nutrient_df['fdc_id'] == best_fdc_id]
    grams = convert_to_grams(quantity, unit)
    scale = grams / 100.0
    result = {}
    for _, row in f_nutr.iterrows():
        nid = row['nutrient_id']
        info = nutrient_map.get(nid)
        if info and info['name'] in focus_nutrients:
            value = row['amount'] * scale
            name = name_alias.get(info['name'], info['name'])
            result[name] = result.get(name, 0.0) + value
    return result

# ----------------- Flask API -------------------
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/nutrition', methods=['GET'])
def nutrition():
    recipe_name = request.args.get('recipe')
    if not recipe_name:
        return jsonify({"error": "Pass a recipe name via the 'recipe' parameter"}), 400
    sheet, lang_col, lang_code, match = detect_language(recipe_name)
    if match is not None and not match.empty:
        row = match.iloc[0]
        col_name = find_english_ingredient_column(row)
        if not col_name:
            return jsonify({"error": "English ingredients column not found in this recipe row."}), 500
        ing_text = str(row[col_name])
        ingredient_lines = [x.strip() for x in ing_text.split(',') if x.strip()]
        total_nutrition = {}
        for line in ingredient_lines:
            parsed = parse_ingredient_line(line)[0]
            ing = parsed['name']
            qty = parsed['amount']
            unit = parsed['unit']
            nut = get_nutrition(ing, qty, unit)
            for k, v in nut.items():
                total_nutrition[k] = total_nutrition.get(k, 0.0) + v
        if not total_nutrition:
            return jsonify({"error": "No nutrition data found for any ingredient."}), 404
        translated_nutrition = {
            translate_nutrient_name(k, lang_code): round(v, 2) for k, v in total_nutrition.items()
        }
        return jsonify({
            "recipe": row[lang_col],
            "nutrition": translated_nutrition,
            "language": lang_code
        })
    else:
        return jsonify({"error": "Recipe not found."}), 404

# ---- Render/Gunicorn Entrypoint -----
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
