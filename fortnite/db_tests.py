import psycopg2
from psycopg2.extras import DictCursor

import click

# from flask import current_app, g
# from flask.cli import with_appcontext


db = psycopg2.connect("dbname=fortnite", cursor_factory=DictCursor)

with db.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS USER;")
    results = cursor.fetchall()
db.close()
