from application.dbModels.user_cocktails_table import *


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    favorite_cocktails = db.relationship('CocktailDB', secondary=users_cocktails_table,
                                         backref=db.backref('users', lazy='dynamic'))

    # ingredients_available = db.Column()

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def dictionary(self):
        dictionary = {'id': self.id, 'username': self.username, 'email': self.email}
        return dictionary
