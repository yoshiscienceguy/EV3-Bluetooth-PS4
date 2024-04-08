import serial,subprocess,Tools,time
import serial.tools.list_ports
from app.BTConn import EV3BT
class PS4BT:
    def __init__(self,COM="",invert_speed = False,invert_turn= True):
        self.INVERT_SPEED = invert_speed
        self.INVERT_TURN = invert_turn
        self.EV3 = None
        self.COM = COM
        #self.startBT(COM)
    def setComPort(self,data):
        
        port = data["data"].split(",")[0].strip()
        self.COM = port

        
    def getPorts(self):
        out = []
        for port in serial.tools.list_ports.comports():
            if "BTHENUM" in port.hwid:
                start_of_address=port.hwid.rfind("&")
                end_of_address=port.hwid.rfind("_")
                address=port.hwid[start_of_address+1:end_of_address]
                if int(address,16)==0:
                    port_type="incoming"
                else:
                    port_type="outgoing"
                    out.append(port.name+" , " +port_type)
        return out

    def startBT(self):
        try:
            print("Connecting ... ")
            
            self.EV3 = serial.Serial(self.COM,timeout=1, write_timeout=0.01)
            print("Bluetooth Ready")
            return True
        except:
            self.restartBTService()
            print("Again Connecting ... ")
            
        return False
    def restartBTService(self):

        proc = subprocess.Popen(["net", "stop","Bluetooth Support Service", "&&", "net","start","Bluetooth Support Service"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        out = out.decode().strip().split("\r\n")
        isStopping = False
        sucessStop = False
        isStarting = False
        sucessStart = False
        for text in out:
            if("is" in text and "stopping" in text):
                isStopping = True
            if("stopped" in text and "successfully" in text and isStopping):
                sucessStop = True
            if("is" in text and "starting" in text):
                isStarting = True
            if("started" in text and "successfully" in text and isStarting):
                sucessStart = True

        if(isStopping and sucessStop and isStarting and sucessStart):
            return "sucess!"
                
        else:
            return "bt restart failed: "            
    

        


    def send(self,info):

        quitbt = info["btns"]["16"]
        if(quitbt):
            s = EV3BT.encodeMessage(EV3BT.MessageType.Logic, 'done', True)
            self.EV3.write(s)
            self.close()
        
        
        speed =self.scale(float(info["joysticks"]["0"]), (-1,1), (-100,100))

        if(self.INVERT_SPEED):
            speed *=-1
        
        turn = self.scale(float(info["joysticks"]["1"]), (-1,1), (-100,100))
        if(self.INVERT_TURN):
            turn *=-1
    ##    #Dead Zone
        if(speed < 6 and speed > -6):
            speed = 0
        if(turn < 6 and turn > -6):
            turn = 0

        right_dc = self.clamp(-speed-turn)
        left_dc = self.clamp(-speed+turn)

        try:
            s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, 'rightM', right_dc)
            self.EV3.write(s)

            s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, 'leftM', left_dc)
            self.EV3.write(s)
    ##  
        except(serial.SerialTimeoutException):
            pass
        except(serial.PortNotOpenError):
            print("BT Disconnected!")
            return False
        except(serial.SerialException):
            return False
        except(OSError):
            return False
        return True
        #time.sleep(.01)
    def close(self):
        if(self.EV3 != None):
            self.EV3.close()
    
    def scale(self, val, src, dst):
        """
        Scale the given value from the scale of src to the scale of dst.
    
        val: float or int
        src: tuple
        dst: tuple
    
        example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
        """
        return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

    def clamp(self,value,floor=-100,ceil=100):
        return max(min(value,ceil),floor)