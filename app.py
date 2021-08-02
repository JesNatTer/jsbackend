import hmac
import sqlite3
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, email, username, password):
        self.id = email
        self.username = username
        self.password = password


class DatabaseTest:
    def __init__(self):
        self.conn = sqlite3.connect('posbe.db')
        self.cursor = self.conn.cursor()

    def execute(self, query, value):
        self.cursor.execute(query, value)
        self.conn.commit()
        return self.cursor


def fetch_users():
    with sqlite3.connect('posbe.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[4], data[5]))
    return new_data


users = fetch_users()


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
                     "product_quantity INTEGER NOT NULL,"
                     "product_price TEXT NOT NULL)")
    print("product table created successfully.")


def createshoppingcart():
    with sqlite3.connect('posbe.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS shoppingcart (item_no INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_id TEXT NOT NULL,"
                     "product_name TEXT NOT NULL,"
                     "quantity INTEGER NOT NULL,"
                     "tprice TEXT NOT NULL,"
                     "email TEXT NOT NULL,"
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

jwt = JWT(app, authenticate, identity)


@app.route('/protected/')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

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
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/addtocatalogue/', methods=["POST"])
@jwt_required()
def newproduct():
    response = {}

    if request.method == "POST":
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        product_quantity = request.form['product_quantity']
        product_price = request.form['product_price']

        query = "INSERT INTO products(product_id, product_name, product_quantity,product_price) VALUES(?, ?, ?, ?)"
        values = (product_id, product_name, product_quantity, product_price)
        DatabaseTest().execute(query, values)

        response["status_code"] = 201
        response['description'] = "product added succesfully"
        return response


@app.route('/viewcatalogue/', methods=["GET"])
def get_products():
    response = {}
    with sqlite3.connect("posbe.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_quantity>0")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


@app.route("/delete-product/<productid>/")
@jwt_required()
def delete_post(productid):
    response = {}
    with sqlite3.connect("posbe.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id='" + str(productid) + "'")
        conn.commit()
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


