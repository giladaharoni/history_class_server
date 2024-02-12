from datetime import datetime
import random
import time

from flask import Flask, jsonify, request
import inspect
app = Flask(__name__)
import questions_generator

members = inspect.getmembers(questions_generator)

# Filter functions from members
questions_list = [member[1] for member in members if inspect.isfunction(member[1])]


# Dummy data to simulate a database
books = [
    {'id': 1, 'title': 'Book 1', 'author': 'Author 1'},
    {'id': 2, 'title': 'Book 2', 'author': 'Author 2'},
    {'id': 3, 'title': 'Book 3', 'author': 'Author 3'}
]


# API endpoint to get all books
@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(books)


# API endpoint to get a specific book by ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({'message': 'Book not found'}), 404


# API endpoint to add a new book
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = {'id': len(books) + 1, 'title': data['title'], 'author': data['author']}
    books.append(new_book)
    return jsonify(new_book), 201


### scoreboard - return the top users with the highest score
@app.route('/api/scoreboard', methods=['GET'])
def scoreboard():
    ### execute query from the db
    scoreboard = []
    return jsonify({'board': scoreboard})


### login
@app.route('/api/login', methods=['GET'])
def login(nickname, password):
    ### execute query from the db
    user_id = 7
    if user_id != 0:
        return jsonify(user_id)
    return jsonify({'message': 'Book not found'}), 404


### register
@app.route('/api/register', methods=['POST'])
def register(email, nickname, password):
    ### execute query from the db
    user_id = 7
    if user_id != 0:
        return jsonify(user_id)
    return jsonify({'message': 'Book not found'}), 404


### learn mode
@app.route('/api/learn', methods=['GET'])
def learn():
    data = request.json
    countries = data['countries']
    start_year = data['start_year']
    end_year = data['end_year']
    ### execute query from the db
    wars_periods = []
    events = []
    figures = []
    return jsonify({'wars and periods': wars_periods, 'events': events, 'figures': figures})


### test mode
@app.route('/api/test', methods=['GET'])
def test():
    data = request.json
    lesson_id = data['lesson_id']
    random_functions = random.choices(questions_list, k=8)
    questions = [f(lesson_id) for f in random_functions]
    return jsonify({'questions': questions})


### submit test
@app.route('/api/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    lesson_id = data['lesson_id']
    score = data['score']
    test_time = datetime.now().time()
    ### update the db


if __name__ == '__main__':
    app.run(debug=True)
