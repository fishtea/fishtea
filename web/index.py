#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import Flask, render_template
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config['DEBUG'] = True  # 开启 debug
mongo = PyMongo(app, uri="mongodb://localhost:27017/SemDB")


@app.route('/')
def query_user():
    sem = mongo.db.sem.find({})
    return  render_template('index.html',sem=sem)
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)