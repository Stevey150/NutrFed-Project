from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Supabase configuration
SUPABASE_URL_MEALS = 'https://atkykbtixfrxjqnstuct.supabase.co'
SUPABASE_URL_USERS = 'https://voxgaptvwzjcobuoxhql.supabase.co'
SUPABASE_API_KEY_USERS = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZveGdhcHR2d3pqY29idW94aHFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkyMzc1NjgsImV4cCI6MjA2NDgxMzU2OH0.NzIXqskOyifHREdTIEEgfjymugcV8ytJwRL9MybuyOk'
SUPABASE_API_KEY_MEALS = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0a3lrYnRpeGZyeGpxbnN0dWN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkwODA0NTksImV4cCI6MjA2NDY1NjQ1OX0.oKM_7zHteNQ00J_dh8RyGvCMCIzWuHODeGOKVQA2V2I'
MEALS_TABLE = 'meals'
ACCOUNTS_TABLE = 'accounts'

@app.route('/')
def home():
    return render_template('get_started.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        headers = {
            'apikey': SUPABASE_API_KEY_USERS,
            'Authorization': f'Bearer {SUPABASE_API_KEY_USERS}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        data = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password)
        }

        response = requests.post(f"{SUPABASE_URL_USERS}/rest/v1/{ACCOUNTS_TABLE}", headers=headers, data=json.dumps(data))

        print("Status Code:", response.status_code)
        print("Response Body:", response.text)

        if response.status_code == 201:
            flash("Account created successfully! Please sign in.")
            return redirect(url_for('signin'))
        else:
            flash("Error creating account. Please try again.")

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        headers = {
            'apikey': SUPABASE_API_KEY_USERS,
            'Authorization': f'Bearer {SUPABASE_API_KEY_USERS}'
        }

        query_url = f"{SUPABASE_URL_USERS}/rest/v1/{ACCOUNTS_TABLE}?email=eq.{email}&select=*"
        response = requests.get(query_url, headers=headers)

        try:
            users = response.json()
            print("DEBUG - Supabase response:", users)  # Log to see the response
        except Exception as e:
            flash(f"Error decoding response: {e}")
            return render_template('signin.html')

        #  Check if the list is empty BEFORE trying to access [0]
        if not isinstance(users, list) or len(users) == 0:
            flash("No account found with that email.")
            return render_template('signin.html')

        user = users[0]
        stored_hash = user.get('password')

        if stored_hash and check_password_hash(stored_hash, password):
            session['user'] = user.get('name', 'User')
            flash("Signed in successfully!")
            return redirect(url_for('categories'))
        else:
            flash("Incorrect password.")
            return render_template('signin.html')

    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('signin'))

@app.before_request
def make_session_permanent():
    session.permanent = True

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

    query_url = f"{SUPABASE_URL_MEALS}/rest/v1/{MEALS_TABLE}?select=Title,Cleaned_Ingredients"
    headers = {
        'apikey': SUPABASE_API_KEY_MEALS,
        'Authorization': f'Bearer {SUPABASE_API_KEY_MEALS}'
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
    query_url = f"{SUPABASE_URL_MEALS}/rest/v1/{MEALS_TABLE}?Title=eq.{title}&select=Title,Ingredients,Instructions,Image_Name"
    headers = {
        'apikey': SUPABASE_API_KEY_MEALS,
        'Authorization': f'Bearer {SUPABASE_API_KEY_MEALS}'
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

@app.route('/find_grocery_stores')
def find_grocery_stores():
    return render_template('find_grocery_stores.html')

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
            query_url = f"{SUPABASE_URL_MEALS}/rest/v1/recipes?total_time=lte.{max_time}&select=recipe_name,total_time"
            headers = {
                'apikey': SUPABASE_API_KEY_MEALS,
                'Authorization': f'Bearer {SUPABASE_API_KEY_MEALS}'
            }
            response = requests.get(query_url, headers=headers)
            if response.status_code == 200:
                meals = response.json()
    return render_template('quick_meals.html', meals=meals)

@app.route('/quick_meals/<meal_name>')
def quick_meal_detail(meal_name):
    query_url = f"{SUPABASE_URL_MEALS}/rest/v1/recipes?recipe_name=eq.{meal_name}&select=*"
    headers = {
        'apikey': SUPABASE_API_KEY_MEALS,
        'Authorization': f'Bearer {SUPABASE_API_KEY_MEALS}'
    }
    response = requests.get(query_url, headers=headers)
    if response.status_code == 200 and response.json():
        meal = response.json()[0]
        return render_template('quick_meal_detail.html', meal=meal)
    else:
        return "Meal not found", 404

@app.route('/vegan_meals')
def vegan_meals():
    return "<h2>Vegan meals - Coming soon!</h2>"

if __name__ == '__main__':
    app.run(debug=True)
