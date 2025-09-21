#fastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

tasks: Dict[int, Dict] = {}
class Task(BaseModel):
    id: int
    title: str
    done: bool = False 
    
@app.post("/create", response_model=Task)
def create_task(task: Task):
    if task.id in tasks:
        raise HTTPException(status_code=400, detail="Task with this ID already exists.")
    tasks[task.id] = task.dict()
    return tasks[task.id]

@app.put("/complete/{id}", response_model=Task)
def complete_task(id: int):
    if id not in tasks:
        raise HTTPException(status_code=400, detail="Task with this ID does not exist.")
    tasks[id]['done'] = True
    return tasks[id]

@app.delete("/delete/{id}")
def delete_task(id: int):
    if id not in tasks:
        raise HTTPException(status_code=400, detail="Task with this ID does not exist.")
    del tasks[id]
    return {"detail": "Task deleted successfully."}

@app.get("/fetch/{id}", response_model=Task)
def fetch_task(id: int):
    if id not in tasks:
        raise HTTPException(status_code=400, detail="Task with this ID does not exist.")
    return tasks[id]
# To ensure data persistence, we could use a database (like SQLite, PostgreSQL, etc.) instead of an in-memory dictionary.
# For scaling to millions of users, we could implement load balancing, database sharding, and caching strategies.
# To handle concurrent requests to the same record, we could implement optimistic or pessimistic locking mechanisms in the database layer. 

#now with flask:
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

tasks = {}
class Task:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.done = False

    def to_dict(self):
        return {"id": self.id, "title": self.title, "done": self.done}
    
@app.route('/create', methods=['POST'])
def create_task():
    data = request.json
    if 'id' not in data or 'title' not in data:
        abort(400, description="Missing id or title")
    if data['id'] in tasks:
        abort(400, description="Task with this ID already exists.")
    task = Task(data['id'], data['title'])
    tasks[data['id']] = task
    return jsonify(task.to_dict()), 201

@app.route('/complete/<int:id>', methods=['PUT'])
def complete_task(id):
    if id not in tasks:
        abort(400, description="Task with this ID does not exist.")
    tasks[id].done = True
    return jsonify(tasks[id].to_dict())

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_task(id):
    if id not in tasks:
        abort(400, description="Task with this ID does not exist.")
    del tasks[id]
    return jsonify({"detail": "Task deleted successfully."})

@app.route('/fetch/<int:id>', methods=['GET'])
def fetch_task(id):
    if id not in tasks:
        abort(400, description="Task with this ID does not exist.")
    return jsonify(tasks[id].to_dict())