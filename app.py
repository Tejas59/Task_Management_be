from flask import Flask, request, redirect, url_for, jsonify
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

app = Flask(__name__)
load_dotenv()

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
                    'member': 'assigned_to',
                    'task_type': 'type',
                    'status': 'status',
                    'entity': 'entity',
                    'contact': 'contact_person'
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
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    task = {
        "title": data.get("title"),
        "assigned_to": data.get("assigned_to"),
        "type": data.get("type"),
        "status": data.get("status"),
        "date": data.get("date"),
        "entity": data.get("entity"),
        "contact_person": data.get("contact_person")
    }

    todos.insert_one(task)

@app.route('/edit/<string:task_id>', methods=['POST'])
def edit(task_id):
    todos.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': {
            'title': request.form['title'],
            'assigned_to': request.form['assigned_to'],
            'type': request.form['type'],
            'status': request.form['status'],
            'date': request.form['date'],
            'entity': request.form['entity'],
            'contact_person': request.form['contact_person']
        }}
    )
    return redirect(url_for('index'))


@app.route('/delete/<string:task_id>', methods=['GET'])
def delete(task_id):
    todos.delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)