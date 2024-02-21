import inspect
import random
from datetime import datetime

import questions_generator
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
members = inspect.getmembers(questions_generator)

# Filter functions from members
questions_list = [member[1] for member in members if inspect.isfunction(member[1])]

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Adaboost123#',
    'database': 'mydb'
}

conn = mysql.connector.connect(**mysql_config)
cursor = conn.cursor()

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


@app.route('/api/all_countries', methods=['GET'])
def get_countries():
    cursor.execute("SELECT ID, country, flag FROM countries")
    result = cursor.fetchall()
    return jsonify(result)


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
    cursor.execute("SELECT b.nickname, avg(a.score) as average FROM mydb.lesson as a, mydb.user as b "
                   "where b.idUser = a.user"
                   " group by a.user order by average desc"
                   "LIMIT 10")
    scoreboard = cursor.fetchall()
    return jsonify({'board': scoreboard})


### login
@app.route('/api/login/<nickname>/<password>', methods=['GET'])
def login(nickname, password):
    cursor.execute("SELECT iduser FROM user WHERE nickname='{}' and password = '{}'".format(nickname, password))
    result = cursor.fetchall()
    if result is not []:
        return jsonify(result[0][0]), 200
    else:
        return jsonify({'message': 'no registered'}), 400


### register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    nickname = data['nickname']
    email = data['email']
    password = data['password']
    cursor.execute(f"SELECT * FROM user WHERE email = '{email}' or nickname = '{nickname}'")
    result = cursor.fetchall()
    if len(result) != 0:
        return jsonify({'message': 'already registered'}), 400
    else:
        cursor.execute(f"INSERT into user (nickname, email, password) VALUES(%s, %s, %s)", (nickname, email,
                                                                                            password))
        user_id = cursor.lastrowid
        conn.commit()
        return jsonify({"user_id": user_id}), 200


### learn mode
@app.route('/api/learn', methods=['GET'])
def learn():
    data = request.json
    countries = data['countries']
    start_year = data['start_year']
    end_year = data['end_year']
    user = data['user']
    ### insert as lesson to the db
    query = """
    INSERT into lesson (user,start_time,end_time) VALUES (%s, %s, %s)
    """
    values = (user, start_year, end_year)
    cursor.execute(query, values)
    conn.commit()
    lesson_id = cursor.lastrowid
    for country in countries:
        query = """
            INSERT into lesson_country (idcountry,idlesson) VALUES (%s, %s)
            """
        values = (country, lesson_id)
        cursor.execute(query, values)
    ### extract the lesson events, figure and periods
    ### event query
    query = f"""
    SELECT Title, Year, Month, day, description
    FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
    a.country = 
    c.idcountry"""
    cursor.execute(query)
    events = cursor.fetchall()
    ### periods
    query = f"""
    SELECT distinct Title, Description, start_time, end_time
    FROM (SELECT Historical_Period
    FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = 0  and c.idlesson = 0 and a.year < b.end_time and a.year > b.start_time and a.country = c.idcountry) as d, mydb.historical_period
    WHERE d.Historical_Period = historical_period.ID
    """
    cursor.execute(query)
    wars_periods = cursor.fetchall()
    ### figures
    query = f"""
    (SELECT distinct Name, photo, description 
    FROM mydb.figure as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE ((a.year_birth <= b.start_time and a.year_death >= b.start_time ) or (a.year_death <= b.end_time and a.year_birth >= b.start_time) or (a.year_birth >= b.start_time and a.year_birth <=b.end_time)) 
    and b.idlesson = c.idlesson and c.idlesson = {lesson_id} and (a.birth_country = c.idcountry or a.death_country = c.idcountry))
    UNION
    (SELECT distinct Name, photo, description 
    FROM mydb.figure as a, mydb.event_figures as b, (SELECT ID
    FROM mydb.historical_event as a, mydb.lesson as b, mydb.lesson_country as c
    WHERE b.idlesson = {lesson_id}  and c.idlesson = {lesson_id} and a.year < b.end_time and a.year > b.start_time and 
    a.country = c.idcountry) as c
    WHERE c.ID = b.idevent and a.ID = idfigure)
    """
    cursor.execute(query)
    figures = cursor.fetchall()
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
    test_time = datetime.now()
    query = "UPDATE lesson SET score=%s, testing_time=%s WHERE idlesson=%s"
    values = (score, test_time, lesson_id)
    cursor.execute(query, values)
    conn.commit()
    return jsonify({}), 200


if __name__ == '__main__':
    app.run(debug=True)
