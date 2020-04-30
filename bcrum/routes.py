from bcrum import app, db, current_user,login_user, logout_user,login_required
import os
import secrets
from bcrum.models import *
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, url_for, render_template, redirect, flash


@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def index():
    if request.method=='POST' and request.form['name'] and request.form['email'] and request.form['gender'] and request.form['message']:
            req = Requests(name=request.form['name'], email=request.form['email'], gender=request.form['gender'], message=request.form['message'])
            db.session.add(req)
            db.session.commit()
            flash("Your request have been received. We'll contact you soon", "success")
            return redirect(url_for('index'))
    elif request.method =='POST' and request.form['subs']:
            subcribe = Subscription(email = request.form['subs'])
            db.session.add(subcribe)
            db.session.commit()
            flash("You have subscribe successfully","success")
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/<int:p_id>/order', methods= ['GET', 'POST'])
@login_required
def order(p_id):
    product = Product.query.filter_by(id=p_id).first()
    if request.method == 'POST':
        if request.form['quantity']:
            product_price = product.product_price.split(",")
            product_price = product_price[0] + product_price[1]
            quantity = int(product_price) * int(request.form['quantity'])
            quantity = "{:,}".format(quantity)
            order = Order(user_id=current_user.id, product_id=product.id, order_quantity=request.form['quantity'], total_price=quantity)
            db.session.add(order)
            db.session.commit()
            flash(f'order processed sucessfully', 'success')
            return redirect(url_for('order_list'))
        else:
            flash(f'Please Enter The Quantity', 'danger')
            return redirect(url_for('order'))
    return render_template('order.html', product=product, current_user=current_user, title="Order")

@app.route('/<int:p_id>/single_product')
def single_product(p_id):
    product = Product.query.filter_by(id=p_id)
    return render_template('single_product.html', product=product, title="Product Details")

@app.route('/orders')
@login_required
def order_list():
    return render_template('orders.html', current_user=current_user,title="Cart") 

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    db.session.delete(order)
    db.session.commit()
    flash('Order Successfully Cancelled!','success')
    return redirect(url_for('order_list'))

@app.route('/products')
def get_all_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.id.desc()).paginate(page=page,per_page=12)
    return render_template('products.html', products=products, title="All Products") 

@app.route('/products/<cat>')
def get_category(cat):
    cat = Categories.query.filter_by(category=cat).first()
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(product_category_id=cat.id).order_by(Product.id.desc()).paginate(page=page,per_page=12)
    return render_template('products.html', products=products,title=cat.category) 

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        if current_user.user_role == 'admin':
            return redirect(url_for('view_all_customers'))
        elif current_user.user_role == 'customer':
            return redirect(url_for('order_list'))
    if request.method == 'POST':
        if request.form['first_name'] and request.form['last_name'] and request.form['email'] and request.form['mobile_number'] and request.form['address'] and request.form['password'] and request.form['confirm_password']:
            if request.form['password'] == request.form['confirm_password']:
                user = Users(first_name=request.form['first_name'], last_name=request.form['last_name'], email=request.form['email'], user_role="customer",mobile_number=request.form['mobile_number'], address=request.form['address'], password=request.form['password'])
                db.session.add(user)
                db.session.commit()
                flash("Registration Sucessful!. You can Log In Now", "success")
                return redirect(url_for('user_login'))
            else:
                flash("Password must match!", "danger")
                return redirect(url_for('register'))
        else:
            flash("All Fields Must Be Filled", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')

#admin routes
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        if current_user.user_role == 'admin':
            return redirect(url_for('view_all_customers'))
        elif current_user.user_role == 'customer':
            return redirect(url_for('index'))
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:
            if user.user_role == 'admin':
                login_user(user)
                next_page = request.args.get('next') 
                flash('Login Successful!','success')
                return redirect(next_page) if next_page else redirect(url_for('view_all_customers'))
            else:
                login_user(user)
                next_page = request.args.get('next') 
                flash('Login Successful!','success')
                return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Check Email And Password', 'danger')
    return render_template('admin_login.html') 

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


@app.route('/admin_customers')
@login_required
def view_all_customers():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    users = Users.query.all()
    return render_template('admin_customers.html', users=users) 

@app.route('/order_status/<int:cus_id>')
def change_order_status(cus_id):
    user = Users.query.filter_by(id=cus_id).first()
    if user.order_status == 'Pending':
        user.order_status = 'Delivered'
        db.session.commit()
        return redirect('view_all_customers')
    elif user.order_status == "Delivered":
        user.order_status == 'Pending'
        db.session.commit()
        return redirect(url_for('view_all_customers'))
    

@app.route('/admin_products')
@login_required
def view_all_products():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('view_all_products.html', products=products) 


@app.route('/admin_customer_orders/<int:cus_id>/')
@login_required
def admin_customerOrders(cus_id):
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    user = Users.query.filter_by(id=cus_id).first()
    return render_template('admin_customerOrders.html', user=user)

def save_picture(product_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(product_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/product_img', picture_fn)
    product_picture.save(picture_path)
    
    return picture_fn



@app.route('/admin_addProducts', methods=['GET','POST'])
@login_required
def add_product():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    image_file = url_for('static', filename='product_img/')
    categories = Categories.query.all()
    if request.method == 'POST':
        if request.form['product_name'] and request.files['product_image'] and request.form['product_category'] and request.form['product_price']:
            product_image = save_picture(request.files['product_image'])
            product = Product(product_category_id=request.form['product_category'], product_name=request.form['product_name'], product_image=product_image, product_description=request.form['product_description'], product_price=request.form['product_price'])
            db.session.add(product)
            db.session.commit()
            flash("Product Created Successfully.", "success")
            return redirect(url_for('add_product'))
        else:
            flash("All fields Must Be Filled", "danger")
    return render_template('addProduct.html', categories=categories, image_file=image_file) 

@app.route('/edit_product/<int:p_id>/', methods=['GET', 'POST'])
@login_required
def edit_product(p_id):
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    categories = Categories.query.all()
    product = Product.query.filter_by(id=p_id).first()
    if request.method == 'POST':
        if request.form['product_name'] and request.files['product_image'] and request.form['product_description'] and request.form['product_category'] and request.form['product_price']:
            product_image = save_picture(request.files['product_image'])
            product.product_name = request.form['product_name']
            product.product_description = request.form['product_description']
            product.product_image = product_image
            product.product_category_id = request.form['product_category']
            product.product_price = request.form['product_price']
            db.session.commit()
            flash('Product Updated!', 'success')
            return redirect(url_for('view_all_products'))
        elif request.form['product_name'] and request.form['product_category'] and request.form['product_description'] and request.form['product_price']:
            product.product_name = request.form['product_name']
            product.product_description = request.form['product_description']
            product.product_category_id = request.form['product_category']
            product.product_price = request.form['product_price']
            db.session.commit()
            flash('Product Updated!', 'success')
            return redirect(url_for('view_all_products'))
    return render_template('edit_product.html', categories=categories, product=product) 

@login_required
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    user = Users.query.filter_by(id=current_user.id).first()
    if request.method == "POST":
        if request.form['email'] and request.form['fname'] and request.form['lname'] and request.form['address']:
            user.email = request.form['email']
            user.first_name = request.form['fname']
            user.last_name = request.form['lname']
            user.address = request.form['address']
            db.session.commit()
            flash('Profile Updated Sucessfully', 'success')
            return redirect(url_for("edit_profile"))
    return render_template('edit_profile.html', current_user=current_user)

@login_required
@app.route('/profile', methods=['GET','POST'])
def profile():
    user = Users.query.filter_by(id=current_user.id).first()
    if request.method == "POST":
        if request.form['email'] and request.form['fname'] and request.form['phoneNo'] and request.form['lname'] and request.form['address']:
            user.email = request.form['email']
            user.first_name = request.form['fname']
            user.last_name = request.form['lname']
            user.address = request.form['address']
            db.session.commit()
            flash('Profile Updated Sucessfully', 'success')
            return redirect(url_for("profile"))
    return render_template('profile.html', current_user=current_user,title="Profile")

@app.route('/delete_product/<int:p_id>/')
def delete_product(p_id):
    product = Product.query.filter_by(id=p_id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('view_all_products'))
    

@app.route('/admin_addcategory', methods=['GET','POST'])
@login_required
def add_category():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    if request.method =='POST':
        category = Categories(category=request.form['category_name'])
        db.session.add(category)
        db.session.commit()
        flash('Category Added!', 'success')
        return redirect(url_for('view_all_categories'))
    return render_template('add_category.html') 

@app.route('/admin_editcategory/<int:cat_id>/', methods=['GET', 'POST'])
@login_required
def edit_category(cat_id):
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    category = Categories.query.filter_by(id=cat_id).first()
    if request.method == 'POST':
        category.category = request.form['category_name']
        db.session.commit()
        flash('Category Updated!', 'success')
        return redirect(url_for('view_all_categories'))
    return render_template('edit_category.html', category=category) 


@app.route('/delete_category/<int:cat_id>/')
def delete_category(cat_id):
    category = Categories.query.filter_by(id=cat_id).first()
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('view_all_categories'))


@app.route('/admin_product_categories')
@login_required
def view_all_categories():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    categories = Categories.query.all()
    return render_template('view_all_category.html', categories=categories) 


@app.route('/admin_users')
@login_required
def view_all_users():
    users = Users.query.filter_by(user_role='admin')
    return render_template('admin_users.html', users=users) 

@app.route('/admin_add_admin', methods=['GET', 'POST'])
def add_admin():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    if request.method == 'POST':
        if request.form['password'] == request.form['confirm_password']:
            # hashed_pwd = generate_password_hash(request.form['password'], method='sha256')
            admin = Users(username=request.form['username'], user_role='admin' ,email=request.form['email'], password=request.form['password'])
            db.session.add(admin)
            db.session.commit()
            flash("Admin Created Successfully", "success")
            return redirect(url_for('view_all_users'))
        else:
            flash("Check Password!!", "danger")
    return render_template('admin_addUser.html') 

@app.route('/admin_requests')
@login_required
def view_all_request():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    req = Requests.query.all()
    return render_template('admin_request.html', req=req) 

@app.route('/admin_subscribers')
@login_required
def subscribers():
    if current_user.is_authenticated:
        if current_user.user_role != 'admin':
            return redirect(url_for('index'))
    subs = Subscription.query.all()
    return render_template('subscribers.html', subs=subs) 
