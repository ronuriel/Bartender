from . import db


class CocktailIngredient:
    def __init__(self, ingredient, measure):
        self.ingredient = ingredient
        self.measure = measure


class IngredientDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"Ingredient('{self.name}')"
