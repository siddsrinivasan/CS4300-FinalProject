from flask import Flask, render_template
from app.irsystem.controllers import search_controller
# import gevent.wsgi
# import gevent.monkey
# import werkzeug.serving


# gevent.monkey.patch_all()
app = Flask(__name__)
# app.debug= True

@app.route("/")
def search_app_current():
    return search_controller.search_current()

@app.route("/prototype1/")
def search_app_prot1():
    return search_controller.search_prot1_controller()

# @werkzeug.serving.run_with_reloader
# def run_server():
#     ws = gevent.wsgi.WSGIServer(listener=('0.0.0.0', 80),
#                                 application=app)
#     ws.serve_forever()

if __name__ == "__main__":
    print "server running"
    #run_server()
    app.run(host='0.0.0.0', port=80)
