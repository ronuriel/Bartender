from application import db


class CocktailsIngredients(db.Model):
    cocktail_id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.String(80))