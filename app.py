from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
from thefuzz import process

app = Flask(__name__)

# --- Load datasets and all your existing functions here ---
# (Load food_df, nutrient_df, food_nutrient_df, xls, your helper functions,
# get_nutrition, detect_language, find_english_ingredient_column,
# translate_nutrient_name, etc.)

@app.route('/')
def home():
    # Render the simple frontend form
    return render_template('index.html')

@app.route('/nutrition', methods=['GET'])
def nutrition_api():
    recipe_name = request.args.get('recipe')
    if not recipe_name:
        return jsonify({"error": "Please provide a recipe name"}), 400
    # Your existing logic to get nutrition JSON for recipe_name...
    sheet, lang_col, lang_code, match = detect_language(recipe_name)
    if match is not None and not match.empty:
        row = match.iloc[0]
        col_name = find_english_ingredient_column(row)
        if not col_name:
            return jsonify({"error": "English ingredients column not found"}), 500
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
            return jsonify({"error": "Nutrition data not found"}), 404
        translated_nutrition = {
            translate_nutrient_name(k, lang_code): round(v, 2) for k, v in total_nutrition.items()
        }
        return jsonify({
            "recipe": row[lang_col],
            "nutrition": translated_nutrition,
            "language": lang_code
        })
    else:
        return jsonify({"error": "Recipe not found"}), 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
