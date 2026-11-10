import itertools
import json
import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

DATA_FILE = "notes.json"


def load_notes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_notes(notes_list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes_list, f, ensure_ascii=False, indent=2)


notes = load_notes()

max_id = max((n["id"] for n in notes), default=0)
note_ids = itertools.count(max_id + 1)


def find_note(note_id):
    return next((n for n in notes if n["id"] == note_id), None)


@app.get("/")
def index():
    return "<h1>Гостевая книга v3</h1>"


@app.get("/notes")
def list_notes():
    author = request.args.get("author")
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    if sort not in ["id", "likes"]:
        return jsonify(error="параметр sort должен быть 'id' или 'likes'"), 400
    if order not in ["asc", "desc"]:
        return jsonify(error="параметр order должен быть 'asc' или 'desc'"), 400

    try:
        limit = int(request.args.get("limit", 10))
        if not (1 <= limit <= 100):
            raise ValueError
    except ValueError:
        return jsonify(error="limit должен быть числом от 1 до 100"), 400

    try:
        offset = int(request.args.get("offset", 0))
        if offset < 0:
            raise ValueError
    except ValueError:
        return jsonify(error="offset должен быть неотрицательным числом"), 400

    result = list(notes)

    if author is not None:
        result = [n for n in result if n["author"] == author]

    is_desc = (order == "desc")
    result.sort(key=lambda n: n[sort], reverse=is_desc)

    result = result[offset: offset + limit]
    return jsonify(result)


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="ожидается JSON"), 400

    text = data.get("text")
    author = data.get("author")

    if not isinstance(text, str) or not text.strip():
        return jsonify(error="field 'text' (non-empty string) is required"), 400
    if not isinstance(author, str) or not author.strip():
        return jsonify(error="field 'author' (non-empty string) is required"), 400

    note = {
        "id": next(note_ids),
        "author": author.strip(),
        "text": text.strip(),
        "likes": 0
    }
    notes.append(note)
    save_notes(notes)

    return jsonify(note), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    return jsonify(note)


@app.post("/notes/<int:note_id>/like")
def like_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    note["likes"] += 1
    save_notes(notes)
    return jsonify(note), 200


@app.put("/notes/<int:note_id>")
def update_note_put(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="ожидается JSON"), 400

    text = data.get("text")
    author = data.get("author")

    if not isinstance(text, str) or not text.strip():
        return jsonify(error="field 'text' (non-empty string) is required"), 400
    if not isinstance(author, str) or not author.strip():
        return jsonify(error="field 'author' (non-empty string) is required"), 400

    note["text"] = text.strip()
    note["author"] = author.strip()

    save_notes(notes)
    return jsonify(note), 200


@app.patch("/notes/<int:note_id>")
def update_note_patch(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="ожидается JSON"), 400

    if "text" in data:
        text = data["text"]
        if not isinstance(text, str) or not text.strip():
            return jsonify(error="field 'text' (non-empty string) is required"), 400
        note["text"] = text.strip()

    if "author" in data:
        author = data["author"]
        if not isinstance(author, str) or not author.strip():
            return jsonify(error="field 'author' (non-empty string) is required"), 400
        note["author"] = author.strip()

    save_notes(notes)
    return jsonify(note), 200


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    notes.remove(note)
    save_notes(notes)
    return "", 204


@app.delete("/notes")
def delete_notes_by_author():
    author = request.args.get("author")
    if not author or not author.strip():
        return jsonify(error="параметр author обязателен и не может быть пустым"), 400

    global notes
    notes_to_delete = [n for n in notes if n["author"] == author]
    deleted_count = len(notes_to_delete)

    notes = [n for n in notes if n["author"] != author]

    if deleted_count > 0:
        save_notes(notes)

    return jsonify({"deleted": deleted_count}), 200


@app.get("/authors")
def list_authors():
    stats = {}
    for n in notes:
        author = n["author"]
        if author not in stats:
            stats[author] = {"author": author, "notes": 0, "likes": 0}
        stats[author]["notes"] += 1
        stats[author]["likes"] += n["likes"]

    result = list(stats.values())

    result.sort(key=lambda x: x["author"])

    return jsonify(result), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="method not allowed"), 405


if __name__ == "__main__":
    app.run(debug=True)