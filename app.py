from bson.objectid import ObjectId
from flask import Flask, request, redirect, render_template, jsonify
import json
from pymongo import MongoClient
import bson.json_util as json_utils
# import datetime so we can have timestamps on things entered into database
from datetime import datetime
from bson.objectid import ObjectId
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import jsonify

# create the app
app = Flask(__name__, static_folder='static', static_url_path='/public')
# connect to the MongoDB database and create a collectoin
# 1 param - host: "Localhost"
# 2 param - port number: 27017
client = MongoClient('localhost', 27017)
db = client.flask_app  # database name is flask_app
# collections - users, orders, items

# print the database names
# print('list database names ->', client.list_database_names())

# collections - users, orders, items
users = db['users']
orders = db['orders']
items = db['items']
flights = db['flights']
get_flight_details = db['get_flight_details']


@app.route('/')
def hello():
    return json_utils.dumps({"message": 'Welcome to my Flask API'})


@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'POST':
        # users information: first_name, last_name, email, phone_number, address, city, state, zipcode
        print('first_name ->', request.form['first_name'])
        # create a dict that will then be send to the users collection
        payload = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number'],
            "address": request.form['address'],
            "city": request.form['city'],
            "state": request.form['state'],
            "zipcode": request.form['zipcode'],
        }

        # Insert a user into database
        new_users = users.insert_one(payload)
        print('id ->', new_users.inserted_id)

        return json_utils.dumps({"user": new_users.inserted_id})
    else:
        # return all of the users in the database
        found_users = users.find()
        return json_utils.dumps({"user": found_users})

# route for orders '/orders' - GET, POST
# order - order_num, first_name, last_name, date (use datatime), total
# create and get orders


@app.route('/orders', methods=['GET', 'POST'])
def get_orders():
    if request.method == 'POST':
        # orders information: order_num, first_name, last_name, date (use datatime), total
        print('order_num ->', request.form['order_num'])
        # create a dict that will then be send to the orders collection
        payload = {
            "order_num": request.form['order_num'],
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "date": datetime.now(),
            "total": request.form['total'],
        }

        # Insert a order into database
        new_orders = orders.insert_one(payload)
        print('id ->', new_orders.inserted_id)

        return json_utils.dumps({"order": new_orders.inserted_id})
    else:
        # return all of the orders in the database
        found_orders = orders.find()
        return json_utils.dumps({"order": found_orders})


# route for items '/items' - GET, POST
# item - item_name, description, price, quantity, in_stock (boolean)
# create and get items

@app.route('/items', methods=['GET', 'POST'])
def get_items():
    if request.method == 'POST':
        # items information: item_name, description, price, quantity, in_stock (boolean)
        print('item_name ->', request.form['item_name'])
        # Convert the string representation of the boolean to Python boolean
        in_stock = request.form['in_stock'].lower() == 'true'

        # Create a dict that will then be sent to the items collection
        payload = {
            "item_name": request.form['item_name'],
            "description": request.form['description'],
            "price": request.form['price'],
            "quantity": request.form['quantity'],
            "in_stock": in_stock,
        }

        # Insert an item into the database
        new_items = items.insert_one(payload)
        print('id ->', new_items.inserted_id)

        return json_utils.dumps({"item": new_items.inserted_id})
    else:
        # Return all of the items in the database
        found_items = list(items.find())
        return json_utils.dumps({"item": found_items})


# create and get flight
@app.route('/flights', methods=['GET', 'POST'])
def get_flights():
    if request.method == 'POST':
        print('flight_num ->', request.form['flight_num'])

        payload = {
            "flight_num": request.form['flight_num'],
            "airline": request.form['airline'],
            "seat": request.form['seat'],
            "airport": request.form['airport'],
            "aircraftType": request.form['aircraftType'],
        }

        new_flights = flights.insert_one(payload)
        print('id ->', new_flights.inserted_id)

        return json_utils.dumps({"flight": new_flights.inserted_id})
    else:
        found_flights = flights.find()
        return json_utils.dumps({"flight": found_flights})

# create a get route for flight using selenium
# http://127.0.0.1:5000/get_flight_details


@app.route('/get_flight_details', methods=['GET'])
def get_flight_details():
    # Assuming you have the data available in variables, replace these with your actual data
    departure_airport_code = "OAK"
    arrival_airport_code = "DCA"
    departure_time = "6:00am"
    arrival_time = "4:00pm"
    date = "Wed, Aug 9, 2023"
    basic_cabin_remaining_seats = "0"
    basic_cabin_class_price = "Sold Out"
    main_cabin_class_remaining_seats = "4"
    main_cabin_class_price = "$634"
    comfort_cabin_class_remaining_seats = "1"
    comfort_cabin_class_price = "$874"
    first_cabin_class_remaining_seats = "1"
    first_cabin_class_price = "$1,842"

    # Create the dictionary with the flight details
    flight_details = {
        "departure_airport_code": departure_airport_code,
        "arrival_airport_code": arrival_airport_code,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "date": date,
        "basic_cabin_class": {
            "remaining_seats": basic_cabin_remaining_seats,
            "price": basic_cabin_class_price,
        },
        "main_cabin_class": {
            "remaining_seats": main_cabin_class_remaining_seats,
            "price": main_cabin_class_price,
        },
        "comfort_cabin_class": {
            "remaining_seats": comfort_cabin_class_remaining_seats,
            "price": comfort_cabin_class_price,
        },
        "first_cabin_class": {
            "remaining_seats": first_cabin_class_remaining_seats,
            "price": first_cabin_class_price,
        }
    }

    # Return the flight details in JSON format
    return jsonify(flight_details)


# update a user


@app.route('/users/<email>', methods=['PUT', 'GET'])
def update_user(email):
    if request.method == 'PUT':
        my_query = {"email": email}
        # Use my_query to find the user with the given email
        found_user = users.find_one(my_query)

        if found_user:
            new_values = {
                "$set": {
                    "first_name": request.form['first_name'] if 'first_name' in request.form else found_user['first_name'],
                    "last_name": request.form['last_name'] if 'last_name' in request.form else found_user['last_name'],
                    "email": request.form['email'] if 'email' in request.form else found_user['email'],
                    "phone_number": request.form['phone_number'] if 'phone_number' in request.form else found_user['phone_number'],
                    "address": request.form['address'] if 'address' in request.form else found_user['address'],
                    "city": request.form['city'] if 'city' in request.form else found_user['city'],
                    "state": request.form['state'] if 'state' in request.form else found_user['state'],
                    "zipcode": request.form['zipcode'] if 'zipcode' in request.form else found_user['zipcode'],
                }
            }

            update_user = users.update_one(my_query, new_values)
            print('updated', update_user.raw_result)
            return json_utils.dumps({"message": "User updated successfully"})
        else:
            return {"message": "email does not exist"}
    elif request.method == 'GET':
        my_query = {"email": email}
        found_user = users.find_one(my_query)

        if found_user:
            return json_utils.dumps({"user": found_user})
        else:
            return {"message": "email does not exist"}


# update order


@app.route('/orders/<order_id>', methods=['PUT', 'GET'])
def update_order(order_id):
    if request.method == 'PUT':
        # Convert the order_id from string to ObjectId
        my_query = {"_id": ObjectId(order_id)}
        found_order = orders.find_one(my_query)

        if found_order:
            new_order_values = {
                "$set": {
                    "order_num": request.form['order_num'] if 'order_num' in request.form else found_order['order_num'],
                    "first_name": request.form['first_name'] if 'first_name' in request.form else found_order['first_name'],
                    "last_name": request.form['last_name'] if 'last_name' in request.form else found_order['last_name'],
                    "date": datetime.now(),  # Update with the current UTC date and time
                    "total": request.form['total'] if 'total' in request.form else found_order['total'],
                }
            }

            update_order = orders.update_one(my_query, new_order_values)
            print('updated', update_order.raw_result)
            return json_utils.dumps({"message": "Order updated successfully"})
        else:
            return {"message": "Order does not exist"}
    elif request.method == 'GET':
        # Convert the order_id from string to ObjectId
        my_query = {"_id": ObjectId(order_id)}
        found_order = orders.find_one(my_query)

        if found_order:
            return json_utils.dumps({"order": found_order})
        else:
            return {"message": "Order does not exist"}


# update item
@app.route('/items/<item_id>', methods=['PUT', 'GET'])
def update_item(item_id):
    if request.method == 'PUT':
        my_query = {"_id": ObjectId(item_id)}
        found_item = items.find_one(my_query)

        if found_item:
            new_item_values = {
                "$set": {
                    "item_name": request.form['item_name'] if 'item_name' in request.form else found_item['item_name'],
                    "description": request.form['description'] if 'description' in request.form else found_item['description'],
                    "price": request.form['price'] if 'price' in request.form else found_item['price'],
                    "quantity": request.form['quantity'] if 'quantity' in request.form else found_item['quantity'],
                    "in_stock": request.form['in_stock'] if 'in_stock' in request.form else found_item['in_stock'],
                }
            }

            update_item = items.update_one(my_query, new_item_values)
            print('updated', update_item.raw_result)
            return json_utils.dumps({"message": "Item updated successfully"})
        else:
            return {"message": "Item does not exist"}
    elif request.method == 'GET':
        my_query = {"_id": ObjectId(item_id)}
        found_item = items.find_one(my_query)

        if found_item:
            return json_utils.dumps({"item": found_item})
        else:
            return {"message": "Item does not exist"}

# update flight


@app.route('/flights/<flight_id>', methods=['PUT', 'GET'])
def update_flight(flight_id):
    if request.method == 'PUT':
        my_query = {"_id": ObjectId(flight_id)}
        found_flight = flights.find_one(my_query)

        if found_flight:
            new_flight_values = {
                "$set": {
                    "flight_num": request.form['flight_num'] if 'flight_num' in request.form else found_flight['flight_num'],
                    "airline": request.form['airline'] if 'airline' in request.form else found_flight['airline'],
                    "seat": request.form['seat'] if 'seat' in request.form else found_flight['seat'],
                    "airport": request.form['airport'] if 'airport' in request.form else found_flight['airport'],
                    "aircraftType": request.form['aircraftType'] if 'aircraftType' in request.form else found_flight['aircraftType'],
                }
            }

            update_flight = flights.update_one(my_query, new_flight_values)
            print('updated', update_flight.raw_result)
            return json_utils.dumps({"message": "Flight updated successfully"})
        else:
            return {"message": "Flight does not exist"}
    elif request.method == 'GET':
        my_query = {"_id": ObjectId(flight_id)}
        found_flight = flights.find_one(my_query)

        if found_flight:
            return json_utils.dumps({"flight": found_flight})
        else:
            return {"message": "Flight does not exist"}


# when a file is the entry point file of a project, we use the global property
# call __name__ and we will check to see if that is equal to __main__
if __name__ == "__main__":
    app.run()
