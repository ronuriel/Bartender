from application import db

users_cocktails_table = db.Table('users_cocktails',
                                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                 db.Column('cocktail_id', db.Integer, db.ForeignKey('cocktailDB.id'))
                                 )
