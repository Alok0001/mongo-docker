from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
api = Api(app)

# MongoDB connection setup
client = MongoClient('mongodb://db:27017/')
db = client.books_db
books = db.books

parser = reqparse.RequestParser()
parser.add_argument('title', type=str, required=True, help="Title cannot be blank!")
parser.add_argument('author', type=str, required=True, help="Author cannot be blank!")


class BookResource(Resource):
    def get(self, book_id=None):  # Corrected the method name to 'get'
        if book_id:
            book = books.find_one({"_id": ObjectId(book_id)})  # Corrected the method and parameter
            if book:
                book['_id'] = str(book['_id'])  # Convert the ObjectId to string
                return book, 200
            return {"message": "Book not found"}, 404
        else:
            all_books = list(books.find())
            for book in all_books:
                book['_id'] = str(book['_id'])
            return all_books, 200

    def post(self):
        args = parser.parse_args()
        result = books.insert_one({"title": args['title'], "author": args['author']})
        return {"id": str(result.inserted_id), "title": args['title'], "author": args['author']}, 201

    def put(self, book_id):
        args = parser.parse_args()
        result = books.update_one({"_id": ObjectId(book_id)},
                                  {"$set": {"title": args['title'], "author": args['author']}})
        if result.matched_count == 0:
            return {"message": "Book not found"}, 404  # Added status code 404 for not found
        return {"id": book_id, "title": args['title'], "author": args['author']}, 200

    def delete(self, book_id):
        result = books.delete_one({"_id": ObjectId(book_id)})
        if result.deleted_count == 0:
            return {"message": "Book not found"}, 404
        return {"message": "Book deleted"}, 200


api.add_resource(BookResource, '/book', '/book/<string:book_id>')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
