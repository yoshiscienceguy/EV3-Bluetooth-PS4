import flask,requests,json 
from flask_socketio import SocketIO, emit
from app.BTConn import BTConnection

app = flask.Flask(__name__)
socketio = SocketIO(app,debug=True,cors_allowed_origins='*',async_mode = None)
PS4Remote = BTConnection.PS4BT(invert_turn= True)
#PS4Remote.restartBTService()
@app.route("/")
def home_view():
    return flask.render_template("./index.html")



@socketio.event
def setPort(port):
    PS4Remote.setComPort(port)
    if(PS4Remote.startBT()):
        emit("BTReady",True)

@socketio.event
def bt_stop(message): 
    
    PS4Remote.close()
    print("disconnected")
@socketio.event
def scan_devices():
    emit("PortInfo",json.dumps(PS4Remote.scanDevices()))

@socketio.event
def bt_start(message):
    PS4Remote.close()
    emit("PortInfo",json.dumps(PS4Remote.scanDevices()))
    #
@socketio.event
def change_controller(message):
    PS4Remote.changeRemote(message)
    
    #
@socketio.event
def controller(message):
    info = json.loads(message)
    #btns = info["btns"] 
    #joysticks = info["joysticks"]

    if(not PS4Remote.send(info)):
        emit("bt_disconnected")
# @app.route("/update", methods = ['POST'])
# def buttonPressed():
#     if flask.request.method == "POST":
#           info=flask.request.json
#           buttons = info["btns"]
#           joysticks = info["joysticks"]
#           print(buttons["1"])
#           return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
#     return json.dumps({'success':False}), 405, {'ContentType':'application/json'} 