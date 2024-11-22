// File to route the loading of the recipe form to the server.
// Shows a loading screen until the requet to the server is complete.

async function fetchRecipes() {
    const params = new URLSearchParams();
    params.set('number', 5)
    url = `https://4017-128-195-97-190.ngrok-free.app/api/v1/fetch_recipes?` + params.toString()
    const response = await fetch(url, {
        method: "get",
        headers: new Headers({
            "ngrok-skip-browser-warning": "69420",
        }),
    })
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log(data)
    return data
}

async function generateRecipe(query) {
    const params = new URLSearchParams();
    params.set('query', query)

    url = `https://4017-128-195-97-190.ngrok-free.app/api/v1/generate_recipes?` + params.toString()
    console.log(url)
    const response = await fetch(url, {
        method: "get",
        headers: new Headers({
            "ngrok-skip-browser-warning": "69420",
        }),
    })
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log(data)
    return data

}

async function editRecipe(recipeName, query) {
    const params = new URLSearchParams();
    params.set('selected_recipe', recipeName)
    params.set('query', query)
    

    url = `https://4017-128-195-97-190.ngrok-free.app/api/v1/edit_recipe?` + params.toString()
    const response = await fetch(url, {
        method: "get",
        headers: new Headers({
            "ngrok-skip-browser-warning": "69420",
        }),
    })
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log(data)
    return data
}

function load(url) {
    // Make the loading gif visible...
    document.getElementById('loading-element').style.visibility = 'visible';
    document.getElementById('loading-animation').style.visibility = 'visible';
    
    // Request the data here

    // Once request is complete (HTTP 200), redirect to the recipe builder page
    // Use AJAX to call the recipe builder file, then have it return a local path to redirect the user to
        // return to:
        // var new_page_path = <python output here>

    // Hide the loading gif and the transparent background block
        // document.getElementById('loading-element').style.visibility = 'hidden';
        // document.getElementById('loading-animation').style.visibility = 'hidden';

    // Redirect to the newly created html page created by the recipe builder.
        // window.location.href = new_page_path;
}

document.addEventListener('DOMContentLoaded', function() {
    var recipeForm = document.getElementById('recipeForm');
    recipeForm.addEventListener('submit', load);
}); 