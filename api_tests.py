import requests
import mysql.connector
from questions_generator import *


def login():
    path = "/api/login/"
    url = main_url + path + "gilad" + "/" + str(1)
    response = requests.get(url)
    print(response)
    return


def register():
    path = '/api/register'
    body = {'email': 'asassa@gmai', 'nickname': 'gil', 'password': '1'}
    response = requests.post(main_url + path, json=body)
    print(response.status_code)


def select_lesson():
    path = '/api/learn'
    body = {'user':1, 'start_year':1900,'end_year':1980, 'countries':[16,17,20]}
    response = requests.post(main_url + path, json=body)
    print(response.content)

def test_submit_test():
    path = '/api/submit_test'
    body = {'lesson_id': 0, 'score': 85}
    response = requests.post(main_url + path, json=body)
    print(response.status_code)

main_url = 'http://127.0.0.1:5000'

if __name__ == '__main__':
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Adaboost123#',
        'database': 'mydb'
    }

    conn = mysql.connector.connect(**mysql_config)
    select_lesson()
    pass
