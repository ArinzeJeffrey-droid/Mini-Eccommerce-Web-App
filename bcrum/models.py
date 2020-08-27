from datetime import datetime
from bcrum import db, login_manager, UserMixin


@login_manager.user_loader
def admin(user_id):
    return Users.query.get(int(user_id))


#database models
class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    category = db.Column('category', db.Unicode, nullable=False)
    products = db.relationship('Product', backref='category')
    
    
    def __repr__(self):
        return self.category

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(200))
    product_description = db.Column(db.String(200), default='No Description Yet')
    product_price = db.Column(db.String(200))
    teller = db.relationship('Order', backref='products')

    def __repr__(self):
        return self.product_name
    
    @classmethod
    def find_by_id( cls, int:id):
        return cls.query.filter_by(id=id).first()



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True)
    user_role = db.Column(db.String(200), default="customer")
    password = db.Column(db.String(200))
    mobile_number = db.Column(db.String(200))
    address = db.Column(db.String(200))
    order_status = db.Column(db.String(200), default='Pending')
    orders = db.relationship('Order', backref='customer')

    def __repr__(self):
        return self.first_name

    @classmethod
    def find_by_email(cls, str:email):
        return cls.query.filter_by(email=email).first()

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    order_date = db.Column(db.String(200), default=datetime.utcnow)
    order_quantity = db.Column(db.String(200))
    total_price = db.Column(db.String(200))
    
    
    
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(200), unique=True)
    
    def __repr__(self):
        return f"Subscription('{self.email}')"
    
class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    gender = db.Column(db.String(200))
    message = db.Column(db.String(200))
    
    def __repr__(self):
        return f"Requests('{self.id}', '{self.name}', '{self.email}', '{self.gender}')"
