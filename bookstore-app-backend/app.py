import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import datetime

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "bookstore")

app = Flask(__name__)

client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = client[MONGO_DB]
books_collection = db.books

def serialize_book(book):
    book['_id'] = str(book['_id'])
    return book

@app.route('/books', methods=['GET'])
def get_books():
    try:
        books = list(books_collection.find())
        return jsonify([serialize_book(book) for book in books])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.json
        new_book = {
            'title': data['title'],
            'author': data['author'],
            'isbn': data['isbn'],
            'genre': data['genre'],
            'price': float(data['price']),
            'quantity': int(data['quantity']),
            'description': data.get('description', ''),
            'created_at': datetime.datetime.utcnow()
        }
        result = books_collection.insert_one(new_book)
        return jsonify({'message': 'Book added successfully', 'id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = books_collection.find_one({'_id': ObjectId(book_id)})
        if book:
            return jsonify(serialize_book(book))
        return jsonify({'error': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.json
        update_data = {
            'title': data.get('title'),
            'author': data.get('author'),
            'isbn': data.get('isbn'),
            'genre': data.get('genre'),
            'price': float(data.get('price', 0)),
            'quantity': int(data.get('quantity', 0)),
            'description': data.get('description', ''),
            'updated_at': datetime.datetime.utcnow()
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = books_collection.update_one(
            {'_id': ObjectId(book_id)}, 
            {'$set': update_data}
        )
        
        if result.matched_count:
            return jsonify({'message': 'Book updated successfully'})
        return jsonify({'error': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        result = books_collection.delete_one({'_id': ObjectId(book_id)})
        if result.deleted_count:
            return jsonify({'message': 'Book deleted successfully'})
        return jsonify({'error': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ismaster')
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)