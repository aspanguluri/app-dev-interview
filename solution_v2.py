#FastAPI

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()

# Data model
class NoteCreate(BaseModel):
    title: str
    content: str

class Note(NoteCreate):
    id: int
    createdAt: datetime

# In-memory store
notes: List[Note] = []
next_id = 1

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    global next_id
    new_note = Note(id=next_id, title=note.title, content=note.content, createdAt=datetime.utcnow())
    notes.append(new_note)
    next_id += 1
    return new_note

@app.put("/notes/{id}", response_model=Note)
def update_note(id: int, content: str):
    for note in notes:
        if note.id == id:
            note.content = content
            return note
    raise HTTPException(status_code=400, detail="Note not found")

@app.delete("/notes/{id}")
def delete_note(id: int):
    global notes
    for note in notes:
        if note.id == id:
            notes = [n for n in notes if n.id != id]
            return {"message": "Note deleted"}
    raise HTTPException(status_code=400, detail="Note not found")

@app.get("/notes", response_model=List[Note])
def list_notes():
    return sorted(notes, key=lambda n: n.createdAt, reverse=True)

@app.get("/notes/search", response_model=List[Note])
def search_notes(query: str):
    return [n for n in notes if query.lower() in n.title.lower() or query.lower() in n.content.lower()]

#Flask Solution

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

notes = []
next_id = 1

@app.route("/notes", methods=["POST"])
def create_note():
    global next_id
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Missing title or content"}), 400

    note = {
        "id": next_id,
        "title": data["title"],
        "content": data["content"],
        "createdAt": datetime.utcnow().isoformat()
    }
    notes.append(note)
    next_id += 1
    return jsonify(note), 200

@app.route("/notes/<int:id>", methods=["PUT"])
def update_note(id):
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "Missing content"}), 400

    for note in notes:
        if note["id"] == id:
            note["content"] = data["content"]
            return jsonify(note), 200
    return jsonify({"error": "Note not found"}), 400

@app.route("/notes/<int:id>", methods=["DELETE"])
def delete_note(id):
    global notes
    for note in notes:
        if note["id"] == id:
            notes = [n for n in notes if n["id"] != id]
            return jsonify({"message": "Note deleted"}), 200
    return jsonify({"error": "Note not found"}), 400

@app.route("/notes", methods=["GET"])
def list_notes():
    sorted_notes = sorted(notes, key=lambda n: n["createdAt"], reverse=True)
    return jsonify(sorted_notes), 200

@app.route("/notes/search", methods=["GET"])
def search_notes():
    query = request.args.get("query", "").lower()
    results = [n for n in notes if query in n["title"].lower() or query in n["content"].lower()]
    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)
