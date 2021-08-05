import hmac
import sqlite3
from flask import Flask, request, jsonify, redirect
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message
import re





class User(object):
    def __init__(self, email, username, password):
        self.id = email
        self.username = username
        self.password = password


class Product(object):
    def __init__(self, product_id, product_name, product_type, product_quantity, product_price, product_image):
        self.product_id = product_id
        self.product_name = product_name
        self.product_type = product_type
        self.product_quantity = product_quantity
        self.product_price = product_price
        self.product_image = product_image


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('posbe.db')
        self.cursor = self.conn.cursor()

    def addpro(self, value):
        query = "INSERT INTO products (product_id, product_name, product_type, product_quantity, product_price," \
                "product_image) VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, value)

    def delpro(self, value):
        query = "DELETE FROM products WHERE product_id='" + value + "'"
        self.cursor.execute(query, value)

    def editpro(self, pro_id, value):
        query = "UPDATE products SET product_id=?, product_name=?, product_type=?, product_quantity=?, product_price=?," \
                "product_image=? WHERE product_id='" + pro_id + "'"
        self.cursor.execute(query, value)

    def selectproduct(self, value):
        query = "SELECT * FROM products WHERE product_id='" + value + "'"
        self.cursor.execute(query, value)
        return self.cursor.fetchall()

    def viewcat(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()


db = Database()


def fetch_users():
    with sqlite3.connect('posbe.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[4], data[5]))
    return new_data


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


def createproducttable():
    with sqlite3.connect('posbe.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products (product_id TEXT PRIMARY KEY,"
                     "product_name TEXT NOT NULL,"
                     "product_type TEXT NOT NULL,"
                     "product_quantity INTEGER NOT NULL,"
                     "product_price TEXT NOT NULL,"
                     "product_image TEXT NOT NULL)")
    print("product table created successfully.")


def createshoppingcart():
    with sqlite3.connect('posbe.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS shoppingcart (item_no INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_id TEXT NOT NULL,"
                     "product_name TEXT NOT NULL,"
                     "quantity INTEGER NOT NULL,"
                     "tprice TEXT NOT NULL,"
                     "email TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "FOREIGN KEY (product_id)"
                     "REFERENCES products(product_id),"
                     "FOREIGN KEY (product_name)"
                     "REFERENCES products(product_name),"
                     "FOREIGN KEY (email)"
                     "REFERENCES user(email))")
    print("cart table created successfully.")


createusertable()
createproducttable()
createshoppingcart()

username_table = {u.username: u for u in users}
useremail_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return useremail_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lottoemail123@gmail.com'
app.config['MAIL_PASSWORD'] = 'MonkeyVillage123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


jwt = JWT(app, authenticate, identity)


@app.route('/protected/')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    if request.method == "POST":

        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
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

            return redirect("/emailsent/%s" % email)
        else:
            return "Email not valid. Please enter a valid email address"


@app.route('/emailsent/<email>', methods=['GET'])
def sendemail(email):
    mail = Mail(app)

    msg = Message('Hello Message', sender='lottoemail123@gmail.com', recipients=[email])
    msg.body = "This is the email body after making some changes"
    mail.send(msg)

    return "sent"


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


@app.route('/addtocatalogue/', methods=["POST"])
@jwt_required
def newproduct():
    dbb = Database()
    response = {}

    if request.method == "POST":
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        product_quantity = request.form['product_quantity']
        product_price = request.form['product_price']
        product_image = request.form['product_image']
        if (product_id == '' or product_name == '' or product_type == ''
                or product_quantity == '' or product_price == '' or product_image == ''):
            return "Please fill in all entry fields"
        else:
            if int(product_quantity):
                values = (product_id, product_name, product_type, product_quantity, product_price, product_image)
                dbb.addpro(values)

                response["status_code"] = 201
                response['description'] = 'product added'
                return response
            else:
                return "Please enter product quantity as an number"
    else:
        return "Method Not Allowed"


@app.route('/viewcatalogue/', methods=["GET"])
def get_products():
    dtb = Database()
    response = {}
    items = dtb.viewcat()
    response['status_code'] = 200
    response['data'] = items
    return response


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
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


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
            product_quantity = request.form['product_quantity']
            product_price = request.form['product_price']
            values = (product_id, product_name, product_quantity, product_price)
            dtb.editpro(productid, values)
            response['message'] = 200
            return response
        else:
            return "Method not allowed"


# @app.route("/addtocart/", methods=["POST"])
# @jwt_required()
# def addtocart():
#     # usernameget = list(username_table.keys())
#     # getindex = list(username_table.values())
#     # currently = getindex.index(current_identity)
#     # currentuser = usernameget[currently]
#
#     response = {}
#     if request.method == "POST":
#         product_id = request.form['product_id']
#         product_name = request.form['product_name']
#         quantity = request.form['quantity']
#         pprice1 = "SELECT product_price FROM products WHERE product_id='" + product_id + "'"
#         tprice = float(Database().getprice(pprice1).fetchone()[0]) * int(quantity)
#
#         query = "INSERT INTO shoppingcart(product_id, product_name, quantity, tprice, email) VALUES(?, ?, ?, ?, ?)"
#         values = (product_id, product_name, quantity, tprice, currentuser)
#         Database().execute(query, values)
#
#         response["status_code"] = 201
#         response['description'] = "Cart updated"
#         return response


# @app.route('/viewcart/', methods=["GET"])
# def get_cart():
#     response = {}
#     with sqlite3.connect("posbe.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM shoppingcart")
#         posts = cursor.fetchall()
#
#     response['status_code'] = 200
#     response['data'] = posts
#     return response


if __name__ == '__main__':
    app.run(debug=True)