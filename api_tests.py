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
    body = {'email': 'sa@gmai', 'nickname': 'gilad2', 'password': '1'}
    response = requests.post(main_url + path, json=body)
    print(response.status_code)


def select_lesson():
    path = '/api/learn'
    body = {'user':1, 'start_year':1900,'end_year':1920, 'countries':[16,17,20]}
    response = requests.get(main_url + path, json=body)
    print(response.status_code)

main_url = 'http://127.0.0.1:5000'

if __name__ == '__main__':
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'mydb'
    }

    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    print(which_one_participant_in_the_event(0,cursor))
    pass
