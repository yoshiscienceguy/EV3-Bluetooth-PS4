/*
 * Gamepad API Test
 * Written in 2013 by Ted Mielczarek <ted@mielczarek.org>
 *
 * To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
 *
 * You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
 */
var haveEvents = 'GamepadEvent' in window;
var haveWebkitEvents = 'WebKitGamepadEvent' in window;
var controllers = {};
var rAF = window.mozRequestAnimationFrame ||
  window.webkitRequestAnimationFrame ||
  window.requestAnimationFrame;

function connecthandler(e) {
  addgamepad(e.gamepad);
  remoteConnection = true;
}
function addgamepad(gamepad) {
  controllers[gamepad.index] = gamepad; var d = document.createElement("div");
  d.setAttribute("id", "controller" + gamepad.index);
  var t = document.createElement("h1");
  t.appendChild(document.createTextNode("gamepad: " + gamepad.id));
  d.appendChild(t);
  var b = document.createElement("div");
  b.className = "buttons";
  for (var i=0; i<gamepad.buttons.length; i++) {
    var e = document.createElement("span");
    e.className = "button";
    //e.id = "b" + i;
    e.innerHTML = i;
    b.appendChild(e);
  }
  d.appendChild(b);
  var a = document.createElement("div");
  a.className = "axes";
  for (i=0; i<gamepad.axes.length; i++) {
    e = document.createElement("meter");
    e.className = "axis";
    //e.id = "a" + i;
    e.setAttribute("min", "-1");
    e.setAttribute("max", "1");
    e.setAttribute("value", "0");
    e.innerHTML = i;
    a.appendChild(e);
  }
  d.appendChild(a);
  document.getElementById("start").style.display = "none";
  document.body.appendChild(d);
  rAF(updateStatus);
}

function disconnecthandler(e) {
  removegamepad(e.gamepad);
}

function removegamepad(gamepad) {
  var d = document.getElementById("controller" + gamepad.index);
  document.body.removeChild(d);
  delete controllers[gamepad.index];
}

function updateStatus() {
  scangamepads();
  for (j in controllers) {
    var controller = controllers[j];
    var d = document.getElementById("controller" + j);
    var buttons = d.getElementsByClassName("button");
    var dataPack = {'btns':{},'joysticks':{}}
    sendbtn= false;
    for (var i=0; i<controller.buttons.length; i++) {
      var b = buttons[i];
      var val = controller.buttons[i];
      var pressed = val == 1.0;
      var touched = false;
      if (typeof(val) == "object") {
        pressed = val.pressed;
        if ('touched' in val) {
          touched = val.touched;
        }
        val = val.value;
      }
      var pct = Math.round(val * 100) + "%";
      b.style.backgroundSize = pct + " " + pct;
      b.className = "button";
      if (pressed) {
        b.className += " pressed";
        dataPack["btns"][i] = true;
        sendbtn = true;
      }
      else if (touched) {
        dataPack["btns"][i] = true;
        b.className += " touched";
        sendbtn = true;
      }
      else{
        dataPack["btns"][i] = false;

      }
    }

    var axes = d.getElementsByClassName("axis");
    for (var i=0; i<controller.axes.length; i++) {
      var a = axes[i];
      a.innerHTML = i + ": " + controller.axes[i].toFixed(4);
      dataPack['joysticks'][i] = controller.axes[i].toFixed(4);
      a.setAttribute("value", controller.axes[i]);
    }

        sendInfo(dataPack);
    
  }
  rAF(updateStatus);
}

function scanDevices(){
  if (!scanning){
    socket.emit('scan_devices');
    console.log("updating scanning bluetooth");
    scanningMode(); 
  }
  else{
    console.log("already scanning");
  }
}


var btConnection = false;
var remoteConnection = false;
var socketConnection = false;
var refreshButton = document.getElementById("scan_refresh");
var select = document.getElementById("portSelection");


function scanningMode(){
  scanning = true;
  refreshButton.disabled = scanning;
  refreshButton.textContent = "Scanning";
  select.innerHTML = '';

}

function choosePort(){
  socket.emit('setPort', {data: select.options[select.selectedIndex].value});
}

const socket = io(); //socketio connection to server//

socket.on("connect", () => {
 console.log("connected");
        document.getElementById("header").innerHTML = "<h3>" + "Websocket Connected" + "</h3";
        
        scanningMode();
        socket.emit('bt_start', {data: "success"});
        socketConnection = true;

});
socket.on("PortInfo", (ports) => {
  var options = JSON.parse(ports)

  for(var i = 0; i < options.length; i++) {
      var opt = options[i];
      var el = document.createElement("option");
      el.textContent = opt;
      el.value = opt;
      select.appendChild(el);
  }

  console.log("done Scanning")
  
  scanning = false;
  refreshButton.disabled = scanning;
  refreshButton.textContent = "Scan Devices";
});

socket.on("BTReady",(data)=>{
  //diasable dropdown and enable disconnect button
  console.log("bt connected");
  btConnection = true;
  document.getElementById("btconfirmation").innerHTML = "<h3> Bluetooth Connected! </h3><button onClick='closeBTConnection()' >Disconnect</button>";
});

function sendInfo(data){
    if(btConnection && socketConnection && remoteConnection){
      socket.emit("controller",JSON.stringify(data) )
    }

}
function closeBTConnection(){
  socket.emit('bt_stop',false);
  btConnection = false;
}

/*
function sendInfo(data){
    

    const url = '/update'; // Endpoint URL 
 
    fetch(url, { 
      method: 'POST', 
      headers: { 
        'Content-Type': 'application/json' 
      }, 
      body: JSON.stringify(data) 
    }) 
    .then(response => { 
      if (!response.ok) { 
        throw new Error('Network response was not ok'); 
      } 
      return response.json(); 
    }) 
    //.then(data => { 
      //console.log(data); // Handle the response data 
    //}) 
    .catch(error => { 
      console.error('There was a problem with your fetch operation:', error); 
    }); 

}*/

function scangamepads() {
  var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
  for (var i = 0; i < gamepads.length; i++) {
    if (gamepads[i] && (gamepads[i].index in controllers)) {
      controllers[gamepads[i].index] = gamepads[i];
    }
  }
}

if (haveEvents) {
  window.addEventListener("gamepadconnected", connecthandler);
  window.addEventListener("gamepaddisconnected", disconnecthandler);
} else if (haveWebkitEvents) {
  window.addEventListener("webkitgamepadconnected", connecthandler);
  window.addEventListener("webkitgamepaddisconnected", disconnecthandler);
} else {
  setInterval(scangamepads, 500);
}

var controllerSelection = document.getElementById("SwitchController");
controllerSelection.addEventListener("click",changeSWController);


var controller2Selection = document.getElementById("PS4Controller");
controller2Selection.addEventListener("click",changePS4Controller);

function changeSWController(){
  console.log("switch ");
  socket.emit('change_controller', {data: 0});

}
function changePS4Controller(){
  console.log("ps4 ");
  socket.emit('change_controller', {data: 1});

}