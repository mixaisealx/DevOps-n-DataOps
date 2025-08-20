#!/usr/bin/env python3
import os
import json
from flask import Flask, Response
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE')
app.config['MYSQL_DATABASE_HOST'] = 'db'
mysql.init_app(app)

tusers = os.getenv('DB_CUSTOM_TABLE_NAME')

@app.route('/health')
def ep_health():
    return '{"status": "OK"}',200


@app.route('/')
def ep_default():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from `" + tusers + "`")
    data = cursor.fetchall()
    conn.close()
    return json.dumps([{'name':row[0], 'age':row[1]} for row in data]),200

if __name__ == '__main__':
    app.run()
