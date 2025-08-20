#!/usr/bin/python
import os
import pymysql
import csv
import json

data = []
with open("/tmp/data.csv", 'r', encoding='utf-8') as f:
    creader = csv.reader(f, delimiter = ",")
    for row in creader:
        try:
            data.append((row[0],int(row[1])))
        except:
            pass

tusers = os.getenv('DB_CUSTOM_TABLE_NAME')

connection = pymysql.connect(
    host='db',
    port=3306,
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE'),
    cursorclass=pymysql.cursors.DictCursor
)

cursor = connection.cursor()

sql = "INSERT INTO `" + str(tusers) + "` VALUES (%s, %s)"
for row in data:
    cursor.execute(sql, row)

connection.commit()

cursor.execute("SELECT * from `" + tusers + "`")
recv_data = cursor.fetchall()
print(json.dumps(recv_data), flush=True)

connection.close()

exit(0)
