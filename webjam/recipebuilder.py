"""

Module used to dynamically generate HTML pages for recipes, which populates the page
using jinja2 templating, which makes it easy to populate pages with the relevant content
as-needed. 

When run, the module looks at the page_content list, which contains dictionaries of the 
recipe data. For each recipe, the module reads the recipe_template.html file, which contains
the HTML structure of the recipe page, and populates it with the recipe data. The populated
data is them written to a new HTML file, which can be viewed in a web browser.

"""

from jinja2 import Template
import os

# instead of page content, fetch the data from the api call here.

PAGE_CONTENT = [
    {"page_title": "Japanese Curry Recipe", 
     "recipe_title": "Japanese Curry", 
     "instructions_text": ["Step 1: Boil the vegetables", "Step 2: Add the curry roux", "Step 3: Simmer for 20 minutes"],
     "ingredients_list": ["1 potato", "1 carrot", "1 onion", "1/2 lb beef", "2 cups water", "1 box curry roux"],
     "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Beef_curry_rice_003.jpg/1200px-Beef_curry_rice_003.jpg"},
]

def build_page():
    # change path as-needed to accommodate for changes in file structure
    with open("templates/recipe_template.html", "r") as f:
        template = Template(f.read())

    for page in PAGE_CONTENT:
        rendered_html = template.render(page)
        recipe_title = page["recipe_title"].replace(" ", "_")
        target_dir = "recipe_pages"

        # ensure that a file can be created without overwriting an existing file
        recipe_path = _search_if_file_exists(target_dir, recipe_title)

        with open(recipe_path, "w") as f:
            f.write(rendered_html)

def _search_if_file_exists(target_dir: str, recipe_title: str):
    """
    Helper function to check if a file already exists in the recipe_pages directory.
    """
    duplicate_number = 0
    file_exists = False

    while not file_exists:
        if os.path.exists(f"{target_dir}/{recipe_title}{duplicate_number}.html"):
            duplicate_number += 1
        else:
            file_exists = True
    
    return f"{target_dir}/{recipe_title}{duplicate_number}.html"

if __name__ == "__main__":
    build_page()
    # print("Recipe pages have been built!")