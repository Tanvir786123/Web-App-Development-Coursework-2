from flask import render_template, flash, redirect, url_for, make_response,\
                  request
import requests
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .forms import *
from .models import *
from flask_login import login_user, logout_user, login_required, current_user
import os
import json


COOKIE_MANAGER_ID_KEY = 'id'
PNG = 1
JPG = 2
JPEG = 3

@app.route('/', methods=['GET', 'POST'])
def index():
    init_admin()
    init_manager()
    if current_user.is_authenticated:
        if current_user.account_type() == Account.MANAGER_ACCOUNT:
            return redirect(url_for('manager'))
        elif current_user.account_type() == Account.USER_ACCOUNT:
            pass
        elif current_user.account_type() == Account.STAFF_ACCOUNT:
            pass
        elif current_user.account_type() == Account.CONTROLLER_ACCOUNT:
            return redirect(url_for('admin.index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_form.username.data = login_form.username.data.lower()
        admin = Controller.query.filter_by(username=login_form.username.data)\
                                .first()
        manager = Manager.query.filter_by(username=login_form.username.data)\
                               .first()
        staff = Staff.query.filter_by(username=login_form.username.data)\
                           .first()
        user = User.query.filter_by(username=login_form.username.data)\
                         .first()
        if admin and admin.verify_password(login_form.password.data):
            login_user(admin, remember=login_form.remember_me.data)
            return redirect(url_for('admin.index'))
        elif manager and manager.verify_password(login_form.password.data):
            login_user(manager, remember=login_form.remember_me.data)
            return redirect(url_for('manager'))
        elif staff and staff.verify_password(login_form.password.data):
            login_user(staff, remember=login_form.remember_me.data)
            flash('You are a staff member')
        elif user and user.verify_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect(url_for('user_home'))
        else:
            flash("Incorrect username or password")
    return render_template('index.html', title='Cafè Noir', form=login_form)

@app.route('/user/order', methods=['POST'])
@login_required
def user_order():
    if not current_user.account_type() == Account.USER_ACCOUNT:
        return redirect(url_for('logout'))
    order_form = QuantityForm()
    if order_form.validate_on_submit():
        product = Product.query.get(order_form.product_id.data)
        if not product:
            return json.dumps({'status': 'Server error'}), 500
        else:
            if product.product_quantity >= order_form.quantity.data:
                return json.dumps({'status': 'OK'}), 200
            else:
                return json.dumps({'status': 'Insufficient stock available'})\
                                    ,400

    return json.dumps({'status': 'Server error'}), 500


@app.route('/user/home', methods=['GET', 'POST'])
@login_required
def user_home():
    if not current_user.account_type() == Account.USER_ACCOUNT:
        return redirect(url_for('logout'))
    form = QuantityForm()
    products = Product.query.all()
    return render_template('user_index.html', title='Cafè Noir',
                            products=products, form=form)

@app.route('/manager/add_products', methods=['GET', 'POST'])
@login_required
def add_products():
    if not current_user.account_type() == Account.MANAGER_ACCOUNT:
        return redirect(url_for('logout'))
    add_products_form = AddProductsForm()
    if add_products_form.validate_on_submit():
        image_id = Product.query.count()
        image_id = image_id + 1
        try:
            file_name = str(image_id)
            if ".png" in add_products_form.product_thumbnail_link.data:
                file_name = file_name + ".png"
                type = PNG
            elif ".jpg" in add_products_form.product_thumbnail_link.data:
                file_name = file_name + ".jpg"
                type = JPG
            elif ".jpeg" in add_products_form.product_thumbnail_link.data:
                file_name = file_name + ".jpeg"
                type = JPEG
            response = requests.get(add_products_form.\
                                    product_thumbnail_link.data)
            path = os.path.join(app.root_path, 'static', 'product_images',
                                str(file_name))
            file = open(path, "wb")
            file.write(response.content)
            file.close()
        except:
            flash('Product thumbnail image could not be downloaded.')
            return render_template('manager_add_products.html',
                                    title='Cafè Noir', form=add_products_form,
                                    status=0)
        product = Product(product_id=image_id,
                          product_name=add_products_form.product_name.data,
                          product_description=add_products_form\
                                              .product_description.data,
                          product_quantity=add_products_form\
                                           .product_current_quantity\
                                           .data,
                          product_reorder_level=add_products_form.\
                                                product_reorder_level.data,
                          product_thumbnail_link=add_products_form.\
                                                 product_thumbnail_link.data,
                          product_thumbnail_type=type)
        db.session.add(product)
        db.session.commit()
        flash("The product was added successfully.")
        return render_template('manager_add_products.html',
                                title='Cafè Noir', form=add_products_form,
                                status=1)
    else:
        return render_template('manager_add_products.html', title='Cafè Noir',
                                form=add_products_form, status=0)

@app.route('/change_manager_password/<user_id>', methods=['GET', 'POST'])
@login_required
def change_manager_password(user_id):
    if not current_user.account_type() == Account.MANAGER_ACCOUNT:
        return redirect(url_for('logout'))
    change_password_form = ChangeMyPasswordForm()
    if change_password_form.validate_on_submit():
        cookie_id = request.cookies.get(COOKIE_MANAGER_ID_KEY)
        if cookie_id and cookie_id == user_id:
            manager = Manager.query.filter_by(username=cookie_id).first()
            if manager:
                manager.password = manager.generate_new_password_hash(
                                           change_password_form.password.data)
                db.session.commit()
                flash('Your password has been updated.')
                return render_template('manager_change_password.html',
                                        title='Cafè Noir',
                                        form=change_password_form, status=1)
            else:
                flash('An unknown error has occured, you will be directed to\
                       the login page in 10 seconds.\
                       Please ensure cookies are enabled.')
                return render_template('manager_change_password.html',\
                                        form=change_password_form, status=0),\
                                        {"Refresh": "10; url=/logout"}
        else:
            flash('An unknown error has occured, you will be directed to the\
                   login page in 10 seconds.\
                   Please ensure cookies are enabled.')
            return render_template('manager_change_password.html',\
                                    form=change_password_form, status=0),\
                                    {"Refresh": "10; url=/logout"}
    return render_template('manager_change_password.html', title='Cafè Noir',
                            form=change_password_form, status=0)

@app.route('/manager')
@login_required
def manager():
    if current_user.account_type() == Account.MANAGER_ACCOUNT:
        cookie_id = request.cookies.get(COOKIE_MANAGER_ID_KEY)
        if not cookie_id:
            res = make_response(render_template('manager_index.html',
                                                 title='Cafè Noir'))
            res.set_cookie(COOKIE_MANAGER_ID_KEY, current_user.get_id(),
                           httponly=True)
            return res
        else:
            return render_template('manager_index.html', title='Cafè Noir')
    else:
        return redirect(url_for('logout'))

@app.route('/manager/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    if current_user.account_type() == Account.MANAGER_ACCOUNT:
        add_staff_form = AddStaffForm()
        if add_staff_form.validate_on_submit():
            add_staff_form.username.data = add_staff_form.username.data.lower()
            admin = Controller.query.filter_by(username=add_staff_form\
                                    .username.data).first()
            manager = Manager.query.filter_by(username=add_staff_form\
                                    .username.data).first()
            staff = Staff.query.filter_by(username=add_staff_form.username.data\
                                          ).first()
            user = User.query.filter_by(username=add_staff_form.username.data)\
                             .first()
            if admin or manager or staff or user:
                flash('This username has been taken, please try again.')
            else:
                staff = Staff(add_staff_form.username.data, add_staff_form\
                              .password.data)
                db.session.add(staff)
                db.session.commit()
                flash('Staff member was added successfully.')
                return render_template('manager_add_staff.html',
                                        title='Cafè Noir',
                                        form=add_staff_form,
                                        status=1)
        return render_template('manager_add_staff.html', title='Cafè Noir',
                                form=add_staff_form,
                                status=0)
    else:
        return redirect(url_for('logout'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    sign_up_form = SignUpForm()
    if sign_up_form.validate_on_submit():
        sign_up_form.username.data = sign_up_form.username.data.lower()
        admin = Controller.query.filter_by(username=sign_up_form.username.data)\
                                .first()
        manager = Manager.query.filter_by(username=sign_up_form.username.data)\
                               .first()
        staff = Staff.query.filter_by(username=sign_up_form.username.data)\
                           .first()
        user = User.query.filter_by(username=sign_up_form.username.data)\
                         .first()
        if admin or manager or staff or user:
            flash('This username has been taken, please try again.')
        else:
            user = User(sign_up_form.username.data, sign_up_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Sign up was successfull.')
            return render_template('signup.html', title='Cafè Noir',
                                    form=sign_up_form,
                                    status=1)
    return render_template('signup.html', title='Cafè Noir', form=sign_up_form,
                            status=0)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    cookie_id = request.cookies.get(COOKIE_MANAGER_ID_KEY)
    if cookie_id:
        res = make_response(redirect(url_for('index')))
        res.set_cookie(COOKIE_MANAGER_ID_KEY, '', expires=0)
        return res
    return redirect(url_for('index'))

def init_admin():
    rows = Controller.query.count()
    if rows == 0:
        admin = Controller('admin', '79A4BD7FB9')
        db.session.add(admin)
        db.session.commit()

def init_manager():
    rows = Manager.query.count()
    if rows == 0:
        manager = Manager('alan123', '79A4BD7FB9')
        db.session.add(manager)
        db.session.commit()
