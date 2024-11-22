from flask import Flask, request, jsonify
from flask_cors import CORS

import data_generator

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/generate_recipes', methods=['GET'])
def generate_recipes():

    query = request.args.get('query', None)

    if not query:
        return 'Please provide a query parameter.'
    
    DataGenerator = data_generator.DataGenerator()
    recipes = DataGenerator.generate_recipe(query, 5)
    
    for recipe in recipes.values():
        if 'recipe_embedding' in recipe:
            del recipe['recipe_embedding']

    return jsonify(recipes)

@app.route('/api/v1/fetch_recipes', methods=['GET'])
def fetch_recipes():

    query = request.args.get('number', 1)

    DataGenerator = data_generator.DataGenerator()
    recipes = DataGenerator.fetch_redis_db(int(query))

    return jsonify(recipes)

@app.route('/api/v1/edit_recipe', methods=['GET'])
def edit_recipe():

    selected_recipe = request.args.get('selected_recipe', None)
    query = request.args.get('query', None)

    if not query or not selected_recipe:
        return 'Please provide a query parameter.'
    
    DataGenerator = data_generator.DataGenerator()
    DataGenerator.fetch_redis_db(10000)
    DataGenerator.set_selected_recipe(selected_recipe)

    new_recipe = DataGenerator.edit_recipe(query)

    return jsonify(new_recipe)

if __name__ == '__main__':
    app.run(debug=True, port=5000)