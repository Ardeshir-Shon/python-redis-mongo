from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import redis

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/mydb"

mongo = PyMongo(app)
redis_client = redis.Redis(host="redis", port=6379)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = mongo.db.users.insert_one(data)
    return jsonify(str(user.inserted_id)), 201

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    cached_user = redis_client.get(user_id)
    
    if cached_user:
        return jsonify(eval(cached_user.decode()))
    else:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            redis_client.set(user_id, str(user))
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['GET'])
def get_users_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name query parameter is required"}), 400

    users_cursor = mongo.db.users.find({"name": name})
    users = [{"_id": str(user["_id"]), "name": user["name"], "age": user["age"]} for user in users_cursor]

    return jsonify(users)

#caching by name added
# @app.route('/users', methods=['GET'])
# def get_users_by_name():
#     name = request.args.get('name')
#     if not name:
#         return jsonify({"error": "Name query parameter is required"}), 400

#     cache_key = f"name:{name}"
#     cached_users = redis_client.get(cache_key)

#     if cached_users:
#         users = eval(cached_users.decode())
#         return jsonify(users)
#     else:
#         users_cursor = mongo.db.users.find({"name": name})
#         users = [{"_id": str(user["_id"]), "name": user["name"], "age": user["age"]} for user in users_cursor]

#         if users:
#             redis_client.set(cache_key, str(users))

#         return jsonify(users)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
