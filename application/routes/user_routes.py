from flask import request
import requests
from .. import app, db
from application.static.consts import *
from application.dbModels.user_cocktails_table import *
from application.cocktail import Cocktail, CocktailDB
from application.user import User
from application.ingredient import IngredientDB
from application.dbModels.cocktails_ingredients_table import CocktailsIngredients


# from application.dbModels.cocktail_ingredient_table import cocktails_ingredients_table


@app.route('/<user_id>/random', methods=["GET"])
def random_cocktail(user_id):
    user = user_validation(user_id)
    if user is None:
        return {'success': False,
                'data': invalid_user}

    respond = requests.request("GET", base_url + random_url)
    # respond = dbObject.getRandom()
    # verify there is drinks field
    json_cocktail = respond.json()["drinks"]

    cocktail = Cocktail(json_cocktail[0])
    add_cocktail(cocktail)
    return {'success': True,
            'data': get_cocktail_struct_dictionary(json_cocktail, 0)
            }


@app.route('/name', methods=["GET"])
def cocktail_by_name():
    name = request.args.get('name')
    respond = requests.request("GET", base_url + by_name_url + name)
    json_cocktails = respond.json()["drinks"]
    if json_cocktails is None:
        return {'success': False,
                'data': invalid_cocktail
                }

    cocktails = {}
    for i in range(len(json_cocktails)):
        add_cocktail(Cocktail(json_cocktails[i]))
        cocktails[i + 1] = get_cocktail_struct_dictionary(json_cocktails, i)

    return {'success': True,
            'data': cocktails
            }


@app.route('/ingredients', methods=["GET"])
def cocktails_by_ingredients():
    ingredients = request.args.get('ingredients').split(',')
    cocktails_id_groups = []
    for ingredient in ingredients:
        respond = requests.request("GET", base_url + by_ingredient_url + ingredient)
        json_cocktails = respond.json()["drinks"]
        cocktails_id_by_ingredient = []
        for cocktail in json_cocktails:
            cocktails_id_by_ingredient.append(cocktail["idDrink"])

        cocktails_id_groups.append(cocktails_id_by_ingredient)

    cocktails_id_intersection = cocktails_id_groups[0]
    for i in range(1, len(cocktails_id_groups)):
        cocktails_id_intersection = list(set(cocktails_id_intersection) & set(cocktails_id_groups[i]))

    cocktails = {}
    count = 1
    for cocktail_id in cocktails_id_intersection:
        respond = requests.request("GET", base_url + by_id_url + cocktail_id)
        json_cocktail = respond.json()["drinks"]
        cocktail = Cocktail(json_cocktail[0])
        add_cocktail(cocktail)
        cocktails[count] = get_cocktail_struct_dictionary(json_cocktail, 0)
        count += 1

    return {'success': True,
            'data': cocktails
            }


@app.route('/users', methods=["GET"])
def get_all_users():
    users = User.query.all()
    count = 1
    user_dict = {}
    for user in users:
        user_dict[count] = user.dictionary()
        count += 1

    return user_dict


@app.route('/adduser', methods=["POST"])
def add_user():

    data = request.json

    username = data['username']
    user_search = User.query.filter_by(username=username).first()
    if user_search is not None:
        return {'success': False,
                'data': username_exits
                }

    email = data['email']
    user_search = User.query.filter_by(email=email).first()
    if user_search is not None:
        return {'success': False,
                'data': email_exists
                }

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return {'success': True,
            'data': new_user.dictionary()
            }


@app.route('/id=<user_id>/addtofavorites', methods=["POST"])
def add_cocktail_to_user_favorites(user_id):
    user = user_validation(user_id)
    if user is None:
        return {'success': False,
                'data': invalid_user
                }

    data = request.json
    cocktail = cocktail_validation(data['cocktail_name'])
    if cocktail is None:
        return {'success': False,
                'data': invalid_cocktail
                }

    if db.session.query(users_cocktails_table).filter_by(user_id=user_id, cocktail_id=cocktail.id).first() is not None:
        return {'success': False,
                'data': cocktail_user_exist
                }

    cocktail.users.append(user)
    db.session.commit()
    return {'success': True,
            'data': f"{cocktail.name} added to {user.username}'s favorites"
            }


@app.route('/id=<user_id>/removefromfavorites', methods=["DELETE"])
def remove_cocktail_from_user_favorites(user_id):
    user = user_validation(user_id)
    if user is None:
        return {'success': False,
                'data': invalid_user
                }

    data = request.json
    cocktail = cocktail_validation(data['cocktail_name'])
    if cocktail is None:
        return {'success': False,
                'data': invalid_cocktail
                }

    record_to_delete = db.session.query(users_cocktails_table).filter_by(user_id=user_id,
                                                                         cocktail_id=cocktail.id).first()
    if record_to_delete is None:
        return {'success': False,
                'data': cocktail_user_doesnt_exist
                }

    cocktail.users.remove(user)
    db.session.commit()
    return {'success': True,
            'data': f"{cocktail.name} was deleted from {user.username}'s favorites"
            }


@app.route('/id=<user_id>/getfavorites', methods=["GET"])
def get_all_user_favorites(user_id):
    user = user_validation(user_id)
    if user is None:
        return {'success': False,
                'data': invalid_user
                }

    touples_user_cocktail = db.session.query(users_cocktails_table).filter_by(user_id=user_id).all()
    cocktails = {}
    for i in range(len(touples_user_cocktail)):
        current_id = touples_user_cocktail[i][1]
        cocktail_db = CocktailDB.query.filter_by(id=current_id).first()
        respond = requests.request("GET", base_url + by_name_url + cocktail_db.name)
        json_cocktails = respond.json()["drinks"]
        cocktails[i + 1] = get_cocktail_struct_dictionary(json_cocktails, 0)

    return cocktails


def add_cocktail(cocktail):
    cocktail_db = cocktail_validation(cocktail.name)
    if cocktail_db is not None:
        return {'success': False,
                'data': cocktail_exists
                }

    cocktail_db = CocktailDB(name=cocktail.name, category=cocktail.category, instructions=cocktail.instructions,
                             picture_url=cocktail.picture_url)
    db.session.add(cocktail_db)
    db.session.commit()

    for ingredient in cocktail.ingredients:
        ingredient_name = ingredient.ingredient
        ingredient_measure = ingredient.measure

        ingredient_db = ingredient_validation(ingredient_name)
        if ingredient_db is None:
            ingredient_db = IngredientDB(name=ingredient_name)
            db.session.add(ingredient_db)
            db.session.commit()

        cocktail_ingredient_obj = CocktailsIngredients(cocktail_id=cocktail_db.id, ingredient_id=ingredient_db.id, amount=ingredient_measure)
        db.session.add(cocktail_ingredient_obj)
        db.session.commit()

    return {"success": True,
            "data": cocktail_db}


def get_cocktail_struct_dictionary(respond_json, index):
    json_cocktail = respond_json[index]
    return Cocktail(json_cocktail).__dict__()


def user_validation(user_id):
    return User.query.filter_by(id=user_id).first()


def cocktail_validation(cocktail_name):
    return CocktailDB.query.filter_by(name=cocktail_name).first()


def ingredient_validation(ingredient_name):
    return IngredientDB.query.filter_by(name=ingredient_name).first()



# Wrap db with Object in order to get flexabilty and do things behind scene
# return status code
