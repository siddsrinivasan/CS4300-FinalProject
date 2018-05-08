from flask import Flask, render_template
from app.irsystem.controllers import search_controller
import sys
import gc
import gevent.pywsgi
import gevent.monkey
import werkzeug.serving

reload(sys)
sys.setdefaultencoding('utf8')

gevent.monkey.patch_all()
app = Flask(__name__)
# app.debug= True

@app.route("/")
def search_app_current():
    gc.collect()
    return search_controller.search_current()

@app.route("/prototype1/")
def search_app_prot1():
    gc.collect()
    return search_controller.search_prot1_controller()

@app.route("/prototype2/")
def search_app_prot2():
    gc.collect()
    return search_controller.search_prot2_controller()

# @werkzeug.serving.run_simple
def run_server():
    ws = gevent.pywsgi.WSGIServer(listener=('0.0.0.0', 80),
                                application=app)
    ws.serve_forever()

if __name__ == "__main__":
    run_server()
    # app.run(host='0.0.0.0', port=80)
