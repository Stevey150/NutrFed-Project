from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = 'https://atkykbtixfrxjqnstuct.supabase.co'
SUPABASE_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0a3lrYnRpeGZyeGpxbnN0dWN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkwODA0NTksImV4cCI6MjA2NDY1NjQ1OX0.oKM_7zHteNQ00J_dh8RyGvCMCIzWuHODeGOKVQA2V2I'  # Replace with your actual anon key
SUPABASE_TABLE = 'meals'

@app.route('/')
def home():
    return render_template('get_started.html')

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search_by_ingredient')
def search_by_ingredient():
    return render_template('ingredients.html')

@app.route('/api/search_meals', methods=['POST'])
def search_meals_by_ingredient():
    data = request.get_json()
    ingredients_input = data.get('ingredients', '')
    input_ingredients = [i.strip().lower() for i in ingredients_input.split(',')]

    # Fetch all meals from Supabase
    query_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=Title,Cleaned_Ingredients"

    headers = {
        'apikey': SUPABASE_API_KEY,
        'Authorization': f'Bearer {SUPABASE_API_KEY}',
    }

    try:
        response = requests.get(query_url, headers=headers)
        meals = response.json()

        matching_meals = []
        for meal in meals:
            if 'Cleaned_Ingredients' in meal and meal['Cleaned_Ingredients']:
                meal_ingredients = meal['Cleaned_Ingredients'].lower().replace(',', ' ').split()
                if any(ingredient in meal_ingredients for ingredient in input_ingredients):
                    matching_meals.append(meal['Title'])

        return jsonify({"results": matching_meals})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/meal/<title>')
def view_meal(title):
    query_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?Title=eq.{title}&select=Title,Ingredients,Instructions,Image_Name"

    headers = {
        'apikey': SUPABASE_API_KEY,
        'Authorization': f'Bearer {SUPABASE_API_KEY}',
    }

    try:
        response = requests.get(query_url, headers=headers)
        meals = response.json()

        if meals:
            return render_template('recipe_detail.html', meal=meals[0])
        else:
            return f"<h2>Meal '{title}' not found.</h2>", 404

    except Exception as e:
        return f"<h2>Error fetching meal: {e}</h2>", 500

@app.route('/search_meals')
def search_meals():
    return "<h2>Search meals - Coming soon!</h2>"

@app.route('/suggested_meals')
def suggested_meals():
    return "<h2>Suggested meals - Coming soon!</h2>"

@app.route('/quick_meals', methods=['GET', 'POST'])
def quick_meals():
    meals = []
    if request.method == 'POST':
        max_time = request.form.get('max_time')
        if max_time:
            query_url = f"{SUPABASE_URL}/rest/v1/recipes?total_time=lte.{max_time}&select=recipe_name,total_time"
            headers = {
                'apikey': SUPABASE_API_KEY,
                'Authorization': f'Bearer {SUPABASE_API_KEY}'
            }
            response = requests.get(query_url, headers=headers)
            if response.status_code == 200:
                meals = response.json()
    return render_template('quick_meals.html', meals=meals)


@app.route('/quick_meals/<meal_name>')
def quick_meal_detail(meal_name):
    query_url = f"{SUPABASE_URL}/rest/v1/recipes?recipe_name=eq.{meal_name}&select=*"
    headers = {
        'apikey': SUPABASE_API_KEY,
        'Authorization': f'Bearer {SUPABASE_API_KEY}'
    }
    response = requests.get(query_url, headers=headers)
    if response.status_code == 200 and response.json():
        meal = response.json()[0]
        return render_template('quick_meal_detail.html', meal=meal)
    else:
        return "Meal not found", 404



@app.route('/find_grocery_stores')
def find_grocery_stores():
    return render_template('find_grocery_stores.html')

@app.route('/vegan_meals')
def vegan_meals():
    return "<h2>Vegan meals - Coming soon!</h2>"

if __name__ == '__main__':
    app.run(debug=True)
