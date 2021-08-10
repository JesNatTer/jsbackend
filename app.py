import hmac
import sqlite3
from flask import Flask, request, redirect
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader


# creating a user object
class User(object):
    def __init__(self, email, username, password):
        self.id = email
        self.username = username
        self.password = password


# creating a product object
class Product(object):
    def __init__(self, product_id, product_name, product_type, product_quantity, product_price, product_image):
        self.product_id = product_id
        self.product_name = product_name
        self.product_type = product_type
        self.product_quantity = product_quantity
        self.product_price = product_price
        self.product_image = product_image


# initializing the database
class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('posbe.db')
        self.cursor = self.conn.cursor()

    def addpro(self, value):
        query = "INSERT INTO products (product_id, product_name, product_type, product_quantity, product_price," \
                "product_image) VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, value)

    def delpro(self, value):
        proid = value
        query = "DELETE FROM products WHERE product_id='" + proid + "'"
        self.cursor.execute(query)

    def editpro(self, pro_id, value):
        proid = pro_id
        values = value
        query = "UPDATE products SET product_id=?, product_name=?, product_type=?, product_quantity=?, product_price=?, product_image=? WHERE product_id='" + proid + "'"
        self.cursor.execute(query, values)

    def selectproduct(self, value):
        proid = value
        query = "SELECT * FROM products WHERE product_id='" + proid + "'"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def viewcat(self):
        self.cursor.execute("SELECT * FROM products WHERE product_quantity > 0")
        data = self.cursor.fetchall()
        return data

    def commit(self):
        self.conn.commit()


# function to take image uploads and convert them into urls
def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name ='dlqxdivje', api_key='599819111725767',
                      api_secret='lTD-aqaoTbzVgmZqyZxjPThyaVg')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        product_image = request.files['product_image']
        app.logger.info('%s file_to_upload', product_image)
        if product_image:
            upload_result = cloudinary.uploader.upload(product_image)
            app.logger.info(upload_result)
            return upload_result['url']


db = Database()


# collecting all users from the database
def fetch_users():
    with sqlite3.connect('posbe.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[4], data[5]))
    return new_data


# collecting all products from the database
def fetch_products():
    with sqlite3.connect('posbe.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        allproducts = cursor.fetchall()

        new_data = []

        for data in allproducts:
            new_data.append(Product(data[0], data[1], data[2], data[3], data[4], data[5]))
    return new_data


users = fetch_users()
products = fetch_products()


# function to create the user table in the database
def createusertable():
    conn = sqlite3.connect('posbe.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(email TEXT PRIMARY KEY,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "address TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# function to create the products table in the database
def createproducttable():
    with sqlite3.connect('posbe.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products (product_id TEXT PRIMARY KEY,"
                     "product_name TEXT NOT NULL,"
                     "product_type TEXT NOT NULL,"
                     "product_quantity INTEGER NOT NULL,"
                     "product_price TEXT NOT NULL,"
                     "product_image TEXT NOT NULL)")
    print("product table created successfully.")


# calling the functions to create the tables
createusertable()
createproducttable()


username_table = {u.username: u for u in users}
useremail_table = {u.id: u for u in users}


# function to create the token during login
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return useremail_table.get(user_id, None)


# initializing the app
app = Flask(__name__)
# CORS(app)
# cors = CORS(app, resource={
#     r"/*":{
#         "origins":"*"
#     }
# })
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lottoemail123@gmail.com'
app.config['MAIL_PASSWORD'] = 'MonkeyVillage123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['TESTING'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
testthing = app.test_client()


jwt = JWT(app, authenticate, identity)


@app.route('/protected/')
@jwt_required()
def protected():
    return '%s' % current_identity


# app route for user registration
@app.route('/user-registration/', methods=["POST"])
@cross_origin()
def user_registration():
    response = {}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    if request.method == "POST":

        email = request.form['email']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        address = request.json['address']
        username = request.json['username']
        password = request.json['password']
        if (re.search(regex, email)):
            with sqlite3.connect("posbe.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "email,"
                               "first_name,"
                               "last_name,"
                               "address,"
                               "username,"
                               "password) VALUES(?, ?, ?, ?, ?, ?)", (email, first_name, last_name, address, username, password))
                conn.commit()

                response["message"] = "success. message sent"
                response["status_code"] = 201
                response.headers.add('Access-Control-Allow-Origin', '*')

            return redirect("/emailsent/%s" % email)
        else:
            return "Email not valid. Please enter a valid email address"


# app route that sends an email to users who registered
@app.route('/emailsent/<email>', methods=['GET'])
def sendemail(email):
    mail = Mail(app)

    msg = Message('Hello Message', sender='lottoemail123@gmail.com', recipients=[email])
    msg.body = "This is the email body after making some changes"
    mail.send(msg)

    return "Thank you for registering. An em"


# app route to view a profile
@app.route('/viewprofile/<username>/', methods=["GET"])
def viewownprofile(username):
    response = {}
    if request.method == "GET":
        with sqlite3.connect("posbe.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username='" + username + "'")
            data = cursor.fetchall()
            if data == []:
                return "User does not exit"
            else:
                response['message'] = 200
                response['data'] = data
        return response


# app route to add a product to the database
@app.route('/addtocatalogue/', methods=["POST"])
@jwt_required()
def newproduct():
    dtb = Database()
    response = {}

    if request.method == "POST":
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        product_quantity = request.form['product_quantity']
        product_price = request.form['product_price']
        if (product_id == '' or product_name == '' or product_type == ''
                or product_quantity == '' or product_price == ''):
            return "Please fill in all entry fields"
        else:
            if int(product_quantity):
                values = (product_id, product_name, product_type, product_quantity, product_price, upload_file())
                dtb.addpro(values)
                dtb.commit()

                response["status_code"] = 201
                response['description'] = 'product added'
                return response
            else:
                return "Please enter product quantity as an number"
    else:
        return "Method Not Allowed"


# app route to view all the products in the database
@app.route('/viewcatalogue/', methods=["GET"])
def get_products():
    dtb = Database()
    response = {}
    items = dtb.viewcat()
    response['status_code'] = 200
    response['data'] = items[0]
    return response


# app route to delete a product from the database
@app.route("/delete-product/<productid>/")
@jwt_required()
def delete_product(productid):
    response = {}
    dtb = Database()
    product = dtb.selectproduct(productid)
    if product == []:
        return "product does not exist"
    else:
        dtb.delpro(productid)
        dtb.commit()
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


# app route to edit a product in the database
@app.route("/edit-product/<productid>/", methods=["PUT"])
@jwt_required()
def edit_product(productid):
    response = {}
    dtb = Database()
    product = dtb.selectproduct(productid)
    if product == []:
        return "Product does not exist in the database"
    else:
        if request.method == "PUT":
            product_id = request.form['product_id']
            product_name = request.form['product_name']
            product_type = request.form['product_type']
            product_quantity = request.form['product_quantity']
            product_price = request.form['product_price']
            values = (product_id, product_name, product_type, product_quantity, product_price, upload_file())
            dtb.editpro(productid, values)
            dtb.commit()
            response['message'] = 200
            return response
        else:
            return "Method not allowed"


if __name__ == '__main__':
    app.run(debug=True)
