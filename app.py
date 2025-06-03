from flask import Flask, request, redirect, url_for, jsonify
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)
load_dotenv()
CORS(app)

mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)

db = client.get_database("task_db")
todos = db.todos

@app.route('/', methods=['GET'])
def index():
        filters = {}
        for key in ['member', 'task_type', 'status', 'entity', 'contact']:
            value = request.args.get(key)
            if value:
                field_map = {
                    'member': 'contactPerson',
                    'task_type': 'type',
                    'status': 'status',
                    'entity': 'entity',
                    'contact': 'contactPerson'
                }
                filters[field_map[key]] = value

        tasks = []
        for task in todos.find(filters):
            task['_id'] = str(task['_id'])  
            tasks.append(task)

        return jsonify(tasks)

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    print(data)

    required_fields = [ "contactPerson", "type", "status", "date", "entity"]

    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "success": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    
    createdTime = datetime.now().strftime("%I:%M %p")

    task = {
        "contactPerson": data["contactPerson"],
        "type": data["type"],
        "status": data["status"],
        "date": data["date"],
        "entity": data["entity"],
        "notes": data.get("notes", ""),
        "createdTime": createdTime
    }

    todos.insert_one(task)
    return jsonify({"success": True}), 200


@app.route('/edit/<string:task_id>', methods=['POST'])
def edit(task_id):
    data = request.get_json()
    update_fields = {}
    allowed_fields = ['contactPerson', 'type', 'status', 'date', 'entity', 'notes']

    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    todos.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': update_fields}
    )

    return jsonify({"success": True}), 200



@app.route('/delete/<string:task_id>',  methods=['DELETE'])
def delete(task_id):
    todos.delete_one({'_id': ObjectId(task_id)})
    return jsonify({"message": "Task deleted successfully"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)