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
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import datetime
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

COOKIE_MANAGER_ID_KEY = 'id'
COOKIE_USER_ID_KEY = 'user_id'
COLUMN_NUMBER = 4
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

@app.route('/user/view_purchases')
@login_required
def view_purchases():
    if not current_user.account_type() == Account.USER_ACCOUNT:
        return redirect(url_for('logout'))
    else:
        user_cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
        return render_template('user_view_purchases.html', title='Cafè Noir')

@app.route('/delete/basket', methods=['GET', 'POST'])
@login_required
def delete_basket():
    if not current_user.account_type() == Account.USER_ACCOUNT:
        return redirect(url_for('logout'))
    user_cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
    basket = Basket.query.filter_by(owner_id=user_cookie_id).all()
    for item in basket:
        db.session.delete(item)
    outfilename = str(user_cookie_id) + ".pdf"
    path = os.path.join(app.root_path, 'static', 'receipts',
                        str(outfilename))
    try:
        os.remove(path)
    except:
        pass
    db.session.commit()
    return redirect(url_for('user_home'))

@app.route('/confirm/basket', methods=['POST'])
@login_required
def confirm_basket():
    if not current_user.account_type() == Account.USER_ACCOUNT:
        return redirect(url_for('logout'))
    else:
        if request.method == "POST":
            datetime_object = datetime.datetime.now()
            executed = False
            user_cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
            rows = Basket.query.filter_by(owner_id=user_cookie_id).count()
            user = User.query.filter_by(username=user_cookie_id).first()
            if not user:
                return json.dumps({'status': 'Server error'}),500
            current_cost = 0
            for i in range(rows):
                data = request.form[str(i)]
                id = data.split('-')
                product = Product.query.filter_by(product_id=id[1]).first()
                basket = Basket.query.filter_by(product_id=id[1]).first()
                if not product:
                    return json.dumps({'status': 'Server error'}),500
                if product.product_quantity < int(id[0]):
                    return json.dumps({'status': 'Insufficient stock available\
                                                  for ' + str(product\
                                                              .product_name)
                                        }),400
                else:
                    current_cost = current_cost\
                                   + float(id[0]) * float(product.product_price)
                    basket.quantity = id[0]
                    product.product_quantity = int(product.product_quantity)\
                                                   - int(id[0])
                    if current_cost == 0:
                        continue
                    if executed == False:
                        executed = True
                    current_cost = round(current_cost, 2)
                    statement = transaction_table.insert().values(\
                                product_id=product.product_id,
                                username=user_cookie_id, quantity=id[0],
                                sub_cost=current_cost, date=datetime_object)
                    #db.session.execute(statement)
            db.session.commit()
            remember = request.form['remember']
            if remember == 'true' and executed == True:
                basket = Basket.query.filter_by(owner_id=user_cookie_id).all()
                array = []
                array.append(["Date" , "Product name", "Quantity", "Price (£)"])
                temp_list = []
                temp_cost = 0
                sum = 0
                today_date = date.today().strftime('%Y-%m-%d')
                for item in basket:
                    if item.quantity == 0:
                        continue
                    temp_cost = item.product_price * item.quantity
                    temp_cost = round(temp_cost, 2)
                    temp_list = [str(today_date), str(item.product_name),
                                                  str(item.quantity),
                                                  str(temp_cost)]
                    sum = sum + temp_cost
                    array.append(temp_list)
                vat = sum * 0.2
                total = vat + sum
                total = round(total, 2)
                sum = round(sum, 2)
                vat = round(vat, 2)
                array.append(["Sub Total", "", "", str(sum)])
                array.append(["VAT", "", "", str(vat)])
                array.append(["Total", "", "", str(total)])
                outfilename = str(user_cookie_id) + ".pdf"
                path = os.path.join(app.root_path, 'static', 'receipts',
                                    str(outfilename))
                pdf = SimpleDocTemplate(path, pagesize = A4)
                styles = getSampleStyleSheet()
                title_style = styles[ "Heading1" ]
                title_style.alignment = 1
                title = Paragraph("Cafè Noir" , title_style)
                style = TableStyle([
                        ( "BOX" , ( 0, 0 ), ( -1, -1 ), 1 , colors.black),
                        ( "GRID" , ( 0, 0 ), ( 4 , 4 ), 1 , colors.black),
                        ( "BACKGROUND" , ( 0, 0 ), ( 3, 0 ), colors.gray),
                        ( "TEXTCOLOR" , ( 0, 0 ), ( -1, 0 ), colors.whitesmoke),
                        ( "ALIGN" , ( 0, 0 ), ( -1, -1 ), "CENTER" ),
                        ( "BACKGROUND" , ( 0 , 1 ) , ( -1 , -1 ), colors.beige),
                    ])
                table = Table(array , style=style)
                pdf.build([title, table])
                fromaddr = "alan.ashford.786123@gmail.com"
                toaddr = str(user.email)
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Cafè Noir receipt"
                body = "Please see your Cafè Noir receipt attached for the "\
                        + "transaction which occured on: " + str(today_date)\
                        + "."
                msg.attach(MIMEText(body, 'plain'))
                filename = outfilename
                attachment = open(path, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s"\
                              % filename)
                msg.attach(p)
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(fromaddr, "Laughing522")
                text = msg.as_string()
                s.sendmail(fromaddr, toaddr, text)
                s.quit()
            if executed == True:
                return json.dumps({'status': 'Transaction is complete.\
                                              Total: ' + "£"+ str(current_cost)\
                                              + ". You will be redirected to the\
                                              home page in 10 seconds."})\
                                              ,200
            else:
                return json.dumps({'status': 'Basket is empty. You will be\
                                              redirected to the home page\
                                              in 10 seconds. Please do not\
                                              try to refresh or leave this\
                                              screen prior to this message\
                                              disappearing and being\
                                              redirected.'}), 400

@app.route('/user/view_basket')
@login_required
def view_basket():
    if not current_user.account_type() == Account.USER_ACCOUNT:
        return redirect(url_for('logout'))
    else:
        form = QuantityForm()
        receipt_form = ReceiptForm()
        user_cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
        products = Basket.query.filter_by(owner_id=user_cookie_id)
        return render_template('user_view_basket.html', title='Cafè Noir',
                                products=products, form=form,
                                receipt=receipt_form)

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
                user_cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
                basket = Basket.query.filter_by(owner_id=user_cookie_id)\
                         .filter_by(product_id=order_form.product_id.data)\
                         .first()
                if not basket:
                    basket = Basket(owner_id=user_cookie_id,
                                    product_id=order_form.product_id.data,
                                    product_name=product.product_name,
                                    product_description=product\
                                                        .product_description,
                                    product_price = product.product_price,
                                    product_thumbnail_type = product\
                                                        .product_thumbnail_type,
                                    quantity=order_form.quantity.data)
                    db.session.add(basket)
                    db.session.commit()
                    return json.dumps({'status': 'OK'}), 200
                else:
                    return json.dumps({'status': 'Item has already been placed\
                                                  inside the basket'}), 400
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
    cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
    if not cookie_id:
        res = make_response(render_template('user_index.html',
                                            title='Cafè Noir',
                                            products=products,
                                            form=form))
        res.set_cookie(COOKIE_USER_ID_KEY, current_user.get_id(),
                       httponly=True)
        return res
    return render_template('user_index.html', title='Cafè Noir',
                            products=products, form=form)

@app.route('/manager/add_products', methods=['GET', 'POST'])
@login_required
def add_products():
    if not current_user.account_type() == Account.MANAGER_ACCOUNT:
        return redirect(url_for('logout'))
    add_products_form = AddProductsForm()
    if add_products_form.validate_on_submit():
        temp = add_products_form.product_name.data.capitalize()
        product = Product.query.filter_by(product_name=temp).first()
        if product:
            flash('Product name is already in use.')
            return render_template('manager_add_products.html',
                                    title='Cafè Noir', form=add_products_form,
                                    status=0)
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
        add_products_form.product_name.data = add_products_form.product_name\
                                              .data.capitalize()
        add_products_form.product_description.data = add_products_form\
                                                     .product_description\
                                                     .data.capitalize()
        product = Product(product_id=image_id,
                          product_name=add_products_form.product_name.data,
                          product_description=add_products_form\
                                              .product_description.data,
                          product_price=add_products_form.product_price.data,
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
        sign_up_form.email.data = sign_up_form.email.data.lower()
        admin = Controller.query.filter_by(username=sign_up_form.username.data)\
                                           .all()
        manager = Manager.query.filter_by(username=sign_up_form.username.data)\
                                          .all()
        staff = Staff.query.filter_by(username=sign_up_form.username.data)\
                                      .all()
        user = User.query.filter_by(username=sign_up_form.username.data)\
                                    .all()
        if admin or manager or staff or user:
            flash('This username has been taken, please try again.')
        else:
            user_obj = User.query.filter_by(email=sign_up_form.email.data).all()
            if user_obj:
                flash('This email has been taken, please try again.')
            else:
                response = requests.get(
                           "https://isitarealemail.com/api/email/validate",
                           params = {'email': sign_up_form.email.data})

                status = response.json()['status']
                if not status == "valid":
                    flash('Invalid email address supplied.')
                else:
                    user = User(username=sign_up_form.username.data,
                                email=sign_up_form.email.data,
                                password=sign_up_form.password.data)
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
    cookie_id = request.cookies.get(COOKIE_USER_ID_KEY)
    if cookie_id:
        res = make_response(redirect(url_for('index')))
        res.set_cookie(COOKIE_USER_ID_KEY, '', expires=0)
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
