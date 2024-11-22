import urllib.parse
import urllib.request
import urllib.response
import urllib

import redis
from redis.commands.search.field import (NumericField, TagField, TextField, VectorField)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

import numpy as np
from openai import OpenAI
from pydantic import BaseModel
import json
import copy

from dotenv import load_dotenv
import os

load_dotenv()

class RecipeSchema(BaseModel):
    recipe_name: str
    description: str
    ingredients: list[str]
    instructions: list[str]
    cuisine_tags: list[str]
    difficulty: int
    prep_time: int
    cooking_tools: list[str]

class DataGenerator():

    def __init__(self):
        
        self.client = OpenAI()
        self.llm_model = 'gpt-4o-mini'
        self.embedding_model = 'text-embedding-3-small'
        self.vector_dimension = 1536

        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_URL'),
            port=15817,
            password=os.getenv('REDIS_PASSWORD')
        )
        self.redis_index = None

        self.history = []
        self.recipe_book = {}
        self.selected_recipe = None

    def set_redis_schema(self):

        ''' Sets up the schema in the Redis database. '''

        recipe_schema = (
            TextField(name='recipe_name'),
            TextField(name='description'),
            TextField(name='ingredients'),
            TextField(name='instructions'),
            TextField(name='cuisine_tags'),
            NumericField(name='difficulty'),
            NumericField(name='prep_time'),
            TextField(name='cooking_tools'),
        )

        self.redis_index = self.redis_client.ft('idx:document')
        self.redis_index.create_index(recipe_schema, definition=IndexDefinition(prefix=['document:'], index_type=IndexType.HASH))

    def load_recipes_to_redis(self) -> None:

        ''' Loads the recipe_book attribute dictionary into Redis database. '''

        if not self.recipe_book:
            raise ValueError('No recipes to load into Redis.')
        
        for recipe in self.recipe_book.values():

            temp_recipe = copy.deepcopy(recipe)

            for key, value in temp_recipe.items():
                
                if not value:
                    raise ValueError('Recipe is missing a value.')
                
                if type(value) == list:
                    temp_recipe[key] = json.dumps(value)
                
            self.redis_client.hset('document:' + temp_recipe['recipe_name'], mapping=temp_recipe)
            print(f'{recipe['recipe_name']} loaded into Redis.')

    def fetch_redis_db(self, max_recipes: int) -> None:

        ''' Fetches all recipes in the redis index and reformats strings to list if needed. '''

        redis_keys = self.redis_client.keys('document:*')
        current = 0

        for key in redis_keys:

            if current == max_recipes:
                break

            document = self.redis_client.hgetall(key)
            recipe = {}
            listable_strings = ['ingredients', 'instructions', 'cuisine_tags', 'cooking_tools']

            for key, item in document.items():
                key_name = key.decode('utf-8')
                if key_name == 'recipe_embedding':
                    pass
                    #recipe[key_name] = np.frombuffer(item)
                elif key_name in listable_strings:
                    item = item.decode('UTF-8')
                    item = json.loads(item)
                    for i in range(len(item)):
                        try:
                            item[i] = item[i].decode('UTF-8')
                        except:
                            pass
                    recipe[key_name] = item
                else:
                    recipe[key_name] = str(item.decode('UTF-8'))

            self.recipe_book[recipe['recipe_name']] = recipe

            current += 1

        return self.recipe_book

    def set_selected_recipe(self, name: str) -> None:
        
        ''' Sets the selected recipe to the recipe with the name provided. '''

        if not name in self.recipe_book:
            raise ValueError('Recipe not found in recipe book.')
        
        self.selected_recipe = self.recipe_book[name]

    def add_history(self, messages: list) -> None:

        ''' Adds a list of messages to the history of the data generator. '''

        self.history.extend(messages)

    def clear_history(self):
        
        ''' Clears the history of the data generator. '''

        self.history = []

    def generate_recipe(self, query: str, max_recipe_count: int):

        ''' Prompts OpenAI LLM for max_recipe_count number of recipes based on the query provided. Follows structured output in RecipeSchema. '''

        previous_recipes = []
        prompt = 'Generate a recipe for the following: ' + query + '.'

        for i in range(max_recipe_count):

            system_role = f'''
            Instructions:

            You are the best chef in the whole world that knows every recipe, who is flexible to adapting the recipe to any customers need. 
            Be detailed for instructions and ingredients. 
            Ensure proper grammer is used and capitalization is used for names.
            Do not repeat similar recipes.
            
            Instruction Format:
            recipe_name: Clear and concise name of the recipe in string format.
            description: Clear and concise description of the recipe in string format.
            ingredients: List of ingredients and their quantities in string format.
            instructions: List of clear, detailed, and easy to follow instructions in string format.
            cuisine_tags: Max of 5 tags indicating the cuisine of the recipe in string format.
            difficulty: Integer value from 1 to 5 indicating the difficulty level of the recipe.
            prep_time: Integer value indicating the preparation time of the recipe in minutes.
            cooking_tools: List of cooking tools required for the recipe in string format.

            Ensure that the instructions only use ingredients and cooking tools previously generated.

            You have currently generated {','.join(previous_recipes)} recipes.
            '''
            
            new_message = [
                { 'role': 'system', 'content': system_role },
                { 'role': 'user', 'content': prompt }
            ]

            self.add_history(new_message)

            response = self.client.beta.chat.completions.parse(
                model=self.llm_model,
                messages=self.history,
                response_format=RecipeSchema
            )
            
            recipe = json.loads(response.choices[0].message.content)            
            recipe['image_link'] = self.get_recipe_photo(recipe)
            #recipe['image_link'] = 'LOL'

            if recipe['image_link']:
                previous_recipes.append(recipe['recipe_name'])

            self.create_recipe_embedding(recipe)
            self.recipe_book[recipe['recipe_name']] = recipe

        return self.recipe_book

    def get_recipe_photo(self, recipe: RecipeSchema) -> str:

        ''' Returns a photo of the recipe generated from Google Search on SerpAPI. '''

        print(recipe['recipe_name'])

        recipe['image_link'] = None
        base_url = 'https://serpapi.com/search'
        query_encoding = urllib.parse.urlencode({'q': recipe['recipe_name'], 'api_key': os.getenv('SERPAPI_ACCESS_KEY')})

        request_object = urllib.request.Request(
            url = base_url + '?' + query_encoding,
        )

        with urllib.request.urlopen(request_object) as response:

            response = json.load(response)
            best_image_link = response['recipes_results'][0]['thumbnail']
            return best_image_link

        return None

    def edit_recipe(self, feedback: str):
        
        ''' Edits the recipe based on user feedback string.  '''

        if not self.selected_recipe:
            raise ValueError('No recipe selected for editing.')
        
        system_role = f'''
        Instructions:

        You are the best chef in the whole world that knows every recipe, who is flexible to adapting the recipe to any customers need. 
        Be detailed for instructions and ingredients. 
        Ensure proper grammer is used and capitalization is used for names.

        You are tasked to edit the recipe below with the following instructions: {feedback}
        
        Instruction Format:
        recipe_name: Clear and concise name of the recipe in string format.
        description: Clear and concise description of the recipe in string format.
        ingredients: List of ingredients and their quantities in string format.
        instructions: List of clear, detailed, and easy to follow instructions in string format.
        cuisine_tags: Max of 5 tags indicating the cuisine of the recipe in string format.
        difficulty: Integer value from 1 to 5 indicating the difficulty level of the recipe.
        prep_time: Integer value indicating the preparation time of the recipe in minutes.
        cooking_tools: List of cooking tools required for the recipe in string format.

        Previous Instructions:
        recipe_name: {self.selected_recipe['recipe_name']}
        description: {self.selected_recipe['description']}
        ingredients: {self.selected_recipe['ingredients']}
        instructions: {self.selected_recipe['instructions']}
        cuisine_tags: {self.selected_recipe['cuisine_tags']}
        difficulty: {self.selected_recipe['difficulty']}
        prep_time: {self.selected_recipe['prep_time']}
        cooking_tools: {self.selected_recipe['cooking_tools']}

        Ensure that the instructions only use ingredients and cooking tools previously generated.

        '''

        prompt = 'Edit the recipe below with the following instructions: ' + feedback + '.'

        new_message = [
            { 'role': 'system', 'content': system_role },
            { 'role': 'user', 'content':  prompt }
        ]

        self.add_history(new_message)

        response = self.client.beta.chat.completions.parse(
            model=self.llm_model,
            messages=self.history,
            response_format=RecipeSchema
        )

        new_recipe = json.loads(response.choices[0].message.content)

        self.selected_recipe['ingredients'] = new_recipe['ingredients']
        self.selected_recipe['description'] = new_recipe['description']
        self.selected_recipe['instructions'] = new_recipe['instructions']
        self.selected_recipe['cuisine_tags'] = new_recipe['cuisine_tags']
        self.selected_recipe['difficulty'] = new_recipe['difficulty']
        self.selected_recipe['prep_time'] = new_recipe['prep_time']
        self.selected_recipe['cooking_tools'] = new_recipe['cooking_tools']

        return self.selected_recipe
        
    def list_all_recipes(self):

        ''' Lists all recipes in the recipe book. '''

        for i in range(len(self.recipe_book)):
            print(f'{i+1}. {list(self.recipe_book.keys())[i]}')

    def create_recipe_embedding(self, recipe: RecipeSchema):
        
        ''' Generates completed recipe document with vector embeddings for a recipe that can be used for similarity comparison and recommendations. '''

        recipe['recipe_embedding'] = np.array(self.generate_vector_embedding(recipe['description'])).tobytes()

    def generate_vector_embedding(self, text: str) -> list[float]:

        ''' Given a string of text, it will use the OpenAI text embedding model to convert it to vector with dimensions attribute. '''

        return self.client.embeddings.create(input=[text.strip()], model=self.embedding_model).data[0].embedding
        

if __name__ == '__main__':
    data_generator = DataGenerator()
    data_generator.generate_recipe('Japanese', 5)
    data_generator.load_recipes_to_redis()
    #data_generator.fetch_redis_db()
    #print('Recipes:')
    #data_generator.list_all_recipes()
    #data_generator.set_selected_recipe(str(input('Enter which recipe you would like to select: ')).strip())
    #data_generator.edit_recipe(str(input('Enter your recipe edit prompt: ')))
    #query_encoding = urllib.parse.urlencode({'selected_recipe': "Witch's Brew Punch", 'query': 'Add more fruits'})
    #print('https://4017-128-195-97-190.ngrok-free.app/api/v1/edit_recipe?' + query_encoding)