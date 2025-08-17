from flask import Flask, render_template, request, jsonify
from nutrition_core import get_recipe_nutrition

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/nutrition', methods=['POST'])
def nutrition():
    data = request.get_json()
    recipe = data.get("recipe", "").strip()
    if not recipe:
        return jsonify({"error": "Please enter a recipe name."})
    nutrition = get_recipe_nutrition(recipe)
    return jsonify(nutrition)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
