# from flask import Flask, request, jsonify
# from flask_cors import CORS
# # import mysql.connector
# import bcrypt
# import mariadb
# app = Flask(__name__)
# CORS(app, supports_credentials=True)  # Allow cross-origin requests with credentials

# # Database Connection
# db = mariadb.connect(
#     host="localhost",
#     user="root",
#     password="66028811Jojo.",
#     database="cashless"
# )

# # db = mysql.connector.connect(
# #     host="localhost",
# #     user="root",
# #     password="66028811Jojo.",
# #     database="cashless_fare_collection"
# # )
# cursor = db.cursor(dictionary=True)

# # User Registration
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     name, email, password, role = data['name'], data['email'], data['password'], data['role']

#     # Check if the user already exists
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     existing_user = cursor.fetchone()
#     if existing_user:
#         return jsonify({"error": "User already exists"}), 409

#     # Hash password
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#     # Insert new user
#     cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
#                    (name, email, hashed_password, role))
#     db.commit()

#     return jsonify({"message": "User registered successfully!"}), 201

# # User Login
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json(force=True)

#     if not data:
#         return jsonify({"error": "Invalid JSON"}), 400
    
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({"error": "Missing email or password"}), 400

#     # Fetch user from DB
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     user = cursor.fetchone()

#     if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
#         return jsonify({"message": "Login successful!", "role": user["role"]})
#     else:
#         return jsonify({"error": "Invalid credentials"}), 401

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)  # Allow connections on all interfaces



from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import mariadb

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Allow cross-origin requests with credentials

# Database Connection
try:
    db = mariadb.connect(
        host="localhost",
        user="root",
        password="66028811Jojo.",
        database="cashless"
    )
    cursor = db.cursor(dictionary=True)
    print("Database connected successfully.")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    exit(1)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not all(k in data for k in ("name", "email", "password", "role")):
        return jsonify({"error": "Missing fields"}), 400

    name, email, password, role = data['name'], data['email'], data['password'], data['role']

    # Check if the user already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert new user
    cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                   (name, email, hashed_password.decode('utf-8'), role))
    db.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    # Fetch user from DB
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        return jsonify({"message": "Login successful!", "role": user["role"]})
    return jsonify({"error": "Invalid credentials"}), 401

# Get Total Fare Collection
@app.route('/get_fare_summary', methods=['GET'])
def get_fare_summary():
    cursor.execute("SELECT bus_id, SUM(amount) as total_fare_collected FROM payments GROUP BY bus_id")
    fares = cursor.fetchall()
    return jsonify(fares), 200

# Get Bus Locations
@app.route('/get_bus_locations', methods=['GET'])
def get_bus_locations():
    cursor.execute("SELECT bus_id, latitude, longitude FROM bus_tracking")
    buses = cursor.fetchall()
    return jsonify(buses), 200

# Get Tout's Fare Collection
@app.route('/get_tout_fare', methods=['GET'])
def get_tout_fare():
    tout_id = request.args.get("tout_id")
    if not tout_id:
        return jsonify({"error": "Missing tout_id"}), 400

    cursor.execute("SELECT SUM(amount) as total_fare_collected FROM payments WHERE user_id = %s", (tout_id,))
    total_fare = cursor.fetchone()
    return jsonify(total_fare or {"total_fare_collected": 0}), 200

# Calculate Fare
@app.route('/calculate_fare', methods=['GET'])
def calculate_fare():
    pickup = request.args.get("pickup")
    destination = request.args.get("destination")
    if not pickup or not destination:
        return jsonify({"error": "Missing pickup or destination"}), 400

    cursor.execute("SELECT fare FROM routes WHERE pickup_point = %s AND destination = %s", (pickup, destination))
    fare = cursor.fetchone()

    if fare:
        return jsonify({"fare": fare["fare"]}), 200
    return jsonify({"error": "Route not found"}), 404

# Run Server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Allow connections on all interfaces

