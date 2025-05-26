# imports
import requests
import os
from dotenv import load_dotenv
load_dotenv()
import pprint
import json
from pyfiglet import Figlet
from termcolor import colored
from prettytable import PrettyTable
import random

main_menu_options = {1: 'I feel lucky', 2: 'Use my fresh pantry', 3: 'I am exploring my inner time keeper', 4: 'Exit'}
lucky_options = {1: "Yes, let's get cooking!", 2: 'No thanks, suggest something else', 3: 'Start over', 4: 'Exit'}
multiple_options = {1: '', 2: '', 3: '', 4: 'Start over', 5: 'Exit'}
again_options = {1: 'Yes!', 2: 'Nope, ciao for now'}

def show_welcome():
    f = Figlet(font='larry3d')
    print(f.renderText('welcome to lazy chef'))
    main_menu()

def get_valid_choice(text, options):
    while True:
        try:
            print()
            choice = int(input(text))
            print()
            if choice in options:
                return choice
            else: print('Please pick a number from the list.')
        except ValueError:
            print('That is not a number... please try again!')

def get_recipes(url, ingredients = None, maxReadyTime = None):
    params = {'apiKey': os.getenv('spoonacular_key')}
    if ingredients:
        params['ingredients'] = ",".join(ingredients)
        params['number'] = 3
        params['ranking'] = 1

    if maxReadyTime:
        params['maxReadyTime'] = maxReadyTime
        params['addRecipeInformation'] = True
        params['sort'] = 'time'
        params['sortDirection'] = 'desc'

    if not ingredients and not maxReadyTime:
        params['number'] = 1

    response = requests.get(url, params)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data:
            return data['results']
        elif 'recipes' in data:
            return data['recipes']
        else:
            return data
    else:
        print(f'Error {response.status_code}: Take it from the top')
        show_welcome()
        return None

def get_recipe_info_id(id):
    params = {'apiKey': os.getenv('spoonacular_key')}
    response = requests.get(f'https://api.spoonacular.com/recipes/{id}/information', params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f'Error {response.status_code}: Take it from the top')
        show_welcome()
        return None

def get_cocktail():
    response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/random.php')
    if response.status_code == 200:
        data = response.json()
    else:
        print(f'Error {response.status_code}: Bar is closed.')
        return None

    cocktail = data['drinks'][0]['strDrink']
    return cocktail

def get_music():
    response = requests.get('https://api.deezer.com/chart')
    if response.status_code == 200:
        data = response.json()
    else:
        print(f'Error {response.status_code}: No speakers available at the moment...')
        return None, None

    album = random.choice(data['albums']['data'])
    title = album['title']
    artist = album['artist']['name']
    return title, artist

def show_recipe(data):
    title = data['title']
    steps = data['analyzedInstructions'][0]['steps']
    instructions = []
    ingredients = []

    for ingredient in data['extendedIngredients']:
        ingredients.append(ingredient['original'])

    for step in steps:
        instructions.append((step['number'], step['step']))

    ingredients_table = PrettyTable()
    ingredients_table.field_names = ['Ingredients']
    for ingredient in ingredients:
        ingredients_table.add_row([ingredient])

    instructions_table = PrettyTable()
    instructions_table.field_names = ['Instructions']
    for step in steps:
        step_number = colored(f"Step {step['number']}:", 'cyan')
        instructions_table.add_row([f"{step_number} {step['step']}"])
        instructions_table.add_row([f" "])

    ingredients_table.align["Ingredients"] = "l"
    ingredients_table.max_width["Ingredients"] = 50
    instructions_table.align["Instructions"] = "l"
    instructions_table.max_width["Instructions"] = 50

    print(colored(title.upper(), 'yellow'))
    print(ingredients_table)
    print(instructions_table)

    print()
    print(colored('Ready for another round?', 'light_cyan'))
    for key, value in again_options.items():
        print(f'{key}: {value}')

    again_choice = get_valid_choice('Tough decision: ', again_options.keys())
    if again_choice == 1:
        main_menu()
    elif again_choice == 2:
        exit_program()

def main_menu():
    print(f"{colored('What do you feel like?', 'yellow')}")
    for key, value in main_menu_options.items():
        print(f'{key}: {value}')

    main_choice = get_valid_choice('Your choice: ', main_menu_options.keys())

    if main_choice == 1:
        lucky()
    elif main_choice == 2:
        pantry()
    elif main_choice == 3:
        time_keeper()
    else:
        exit_program()

def lucky():
    while True:
        data_recipe = get_recipes('https://api.spoonacular.com/recipes/random', None, None)
        title = data_recipe[0]['title']
        cocktail = get_cocktail()
        album, artist = get_music()

        print(f"Nice, today on the menu: {colored(title, 'green')}")
        print(f"Maybe sip on a {colored(cocktail, 'yellow')} while cooking?")
        print(f"And why not move a little to the tunes of {colored(album, 'blue')} by {colored(artist, 'magenta')} while cooking?")
        print('')

        for key, value in lucky_options.items():
            print(f'{key}: {value}')

        lucky_choice = get_valid_choice('Your choice: ', lucky_options.keys())

        if lucky_choice == 1:
            show_recipe(data_recipe[0])
            return
        elif lucky_choice == 2:
            continue
        elif lucky_choice == 3:
            main_menu()
            return
        elif lucky_choice == 4:
            exit_program()
            return

def pantry():
    print("Time to check your fridge!")
    ingredients = set()
    while True:
        new_ingredient = input(f"Add {colored('- ONE -', 'red')} ingredient at a time, or press enter when done: \n").strip()
        if not new_ingredient:
            break
        ingredients.add(new_ingredient)

    data_recipes = get_recipes('https://api.spoonacular.com/recipes/findByIngredients', ingredients, None)

    if not data_recipes:
        print(f"No ingredients found, so here's a random selection {colored('ESPECIALLY', 'light_red')} for you")
        lucky()
        return

    multiple_options[1] = f'Show recipe for {data_recipes[0]['title']} (uses {data_recipes[0]['usedIngredientCount']} of your ingredients)'
    multiple_options[2] = f'Show recipe for {data_recipes[1]['title']} (uses {data_recipes[1]['usedIngredientCount']} of your ingredients)'
    multiple_options[3] = f'Show recipe for {data_recipes[2]['title']} (uses {data_recipes[2]['usedIngredientCount']} of your ingredients)'

    for key, value in multiple_options.items():
        print(f'{key}: {value}')

    pantry_choice = get_valid_choice('Your choice: ', multiple_options.keys())

    if pantry_choice in [1, 2, 3]:
        recipe_id = data_recipes[pantry_choice - 1]['id']
        full_recipe = get_recipe_info_id(recipe_id)
        show_recipe(full_recipe)
    elif pantry_choice == 4:
        main_menu()
        return
    elif pantry_choice == 5:
        exit_program()

def time_keeper():
    print('Ready, steady....cook. Remember Ainsley?')
    while True:
        try:
            time = int(input(f"{colored('How many minutes are you investing in this succulent meal? ', 'light_yellow')}"))
            break
        except ValueError:
            print(f'Easy, buddy. That was not a number! Try again')

    data_recipes = get_recipes('https://api.spoonacular.com/recipes/complexSearch', None, time)

    multiple_options[1] = f'Show recipe for {data_recipes[0]['title']} (ready in {data_recipes[0]['readyInMinutes']} minutes)'
    multiple_options[2] = f'Show recipe for {data_recipes[1]['title']} (ready in {data_recipes[1]['readyInMinutes']} minutes)'
    multiple_options[3] = f'Show recipe for {data_recipes[2]['title']} (ready in {data_recipes[2]['readyInMinutes']} minutes)'

    for key, value in multiple_options.items():
        print(f'{key}: {value}')

    time_keeper_choice = get_valid_choice('Your choice: ', multiple_options.keys())

    if time_keeper_choice in [1, 2, 3]:
        recipe_id = data_recipes[time_keeper_choice - 1]['id']
        full_recipe = get_recipe_info_id(recipe_id)
        show_recipe(full_recipe)
    elif time_keeper_choice == 4:
        main_menu()
        return
    elif time_keeper_choice == 5:
        exit_program()

def exit_program():
    url = 'https://api.adviceslip.com/advice'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print('Thanks for using Lazy Chef!')
        print(f"And remember: {colored(data['slip']['advice'], 'red', attrs=['bold'])} {'\U0001F643'}")
        print()
        exit()
    else:
        print(f'Error {response.status_code}: too lazy to fetch you any advice.')
        exit()

show_welcome()