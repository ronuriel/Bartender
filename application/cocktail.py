from . import db
from .ingredient import CocktailIngredient


# from .dbModels.cocktail_ingredient_table import cocktails_ingredients_table


# dict.get("field_name")

class Cocktail:

    def __init__(self, json_cocktail):
        self.name = json_cocktail["strDrink"]
        self.category = json_cocktail["strCategory"]
        self.ingredients = get_ingredients(json_cocktail)
        self.instructions = json_cocktail["strInstructions"]
        self.picture_url = json_cocktail["strDrinkThumb"]

    def __dict__(self):
        ans = {'name': self.name, 'category': self.category, 'instructions': self.instructions}
        ingredients = []
        for ingredient in self.ingredients:
            ingredients.append((ingredient.ingredient, ingredient.measure))

        ans['ingredients'] = ingredients

        return ans

    # def cocktail_string(self):
    #    string = ""
    #    string += "1. Name: " + self.name + "\n"
    #    string += "2. Category: " + self.category + "\n"
    #    string += "3. Ingredients: " + "\n"
    #    for tuple in self.ingredients:
    #        string += "# " + tuple[0]
    #        if tuple[1] is None:
    #            string += "\n"
    #        else:
    #            string += " - " + tuple[1] + "\n"
    #
    #    string += "4. Instructions: " + self.instructions + "\n"
    #
    #    return string


class CocktailDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(30))
    # ingredients = db.relationship('IngredientDB', secondary=cocktails_ingredients_table,
    #                                  backref=db.backref('cocktails', lazy='dynamic'))
    instructions = db.Column(db.Text, nullable=False)
    picture_url = db.Column(db.String(100))

    def __repr__(self):
        return f"Cocktail('{self.name}'. '{self.instructions}')"


def get_ingredients(json_cocktail):
    base_ingredient_key_str = "strIngredient"
    base_measure_key_str = "strMeasure"
    ingredients = []
    for i in range(1, 15):
        ingredient = json_cocktail[base_ingredient_key_str + str(i)]
        measure = json_cocktail[base_measure_key_str + str(i)]
        if (ingredient is None and measure is None) or (ingredient == ""):
            break
        else:
            cocktail_ingredient = CocktailIngredient(ingredient, measure)
            ingredients.append(cocktail_ingredient)

    return ingredients
