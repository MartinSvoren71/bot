from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

def load_users():
    with open('user.json', 'r') as file:
        users = json.load(file)
    return users

def save_users(users):
    with open('user.json', 'w') as file:
        json.dump(users, file)

@app.route('/')
def index():
    return render_template('create_user.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    username = request.form['username']
    password = request.form['password']

    user = {
        "username": username,
        "password": password
    }

    users = load_users()
    users.append(user)
    save_users(users)

    return jsonify({"status": "success", "message": "User created successfully."})

@app.route('/get_users', methods=['GET'])
def get_users():
    users = load_users()
    return jsonify(users)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.json['username']
    users = load_users()
    user_to_delete = None

    for user in users:
        if user['username'] == username:
            user_to_delete = user
            break

    if user_to_delete:
        users.remove(user_to_delete)
        save_users(users)
        return jsonify({"status": "success", "message": "User deleted successfully."})
    else:
        return
#runn app as local on port 5000 , accesible on private and public AWS IP
app.run(host='0.0.0.0', port=5000)
