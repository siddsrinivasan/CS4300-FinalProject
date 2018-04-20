from flask import Flask, render_template
import string
from app.irsystem.controllers import search_controller
import os

app = Flask(__name__)

@app.route("/")
def search_app_current():
    return search_controller.search_current()

@app.route("/prototype1/")
def search_app_prot1():
    return search_controller.search_prot1_controller()
# @app.route("/?search=<query>")
# def search_app(query):
#     q= ''
#     for each_char in str(query):
#         if each_char != '+':
#             q+= each_char
#         else:
#             q+= ' '
#     print q
#     return search_controller.search(q)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
