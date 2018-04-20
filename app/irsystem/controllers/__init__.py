# Import flask deps
from flask import request, render_template, \
	flash, g, session, redirect, url_for, jsonify, abort

# Import module models
# from app.irsystem import search

# IMPORT THE BLUEPRINT APP OBJECT
from app.irsystem import irsystem
