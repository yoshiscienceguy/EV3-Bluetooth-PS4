# Use pygame to get readouts from a ds4 controller
# This is an efficient way to get inputs as long as you don't need six-axis data


import pygame
import serial
import time
import app.BTConn.EV3BT as EV3BT
import subprocess

class DualShock4():
    def __init__(self):
    # Labels for DS4 controller axes
        self.AXIS_LEFT_STICK_X = 0
        self.AXIS_LEFT_STICK_Y = 1
        self.AXIS_RIGHT_STICK_X = 2
        self.AXIS_RIGHT_STICK_Y = 3
        self.AXIS_R2 = 4
        self.AXIS_L2 = 5

        # Labels for DS4 controller buttons
        # Note that there are 14 buttons (0 to 13 for pygame, 1 to 14 for Windows setup)
        self.BUTTON_SQUARE = 0
        self.BUTTON_CROSS = 1
        self.BUTTON_CIRCLE = 2
        self.BUTTON_TRIANGLE = 3

        self.BUTTON_L1 = 4
        self.BUTTON_R1 = 12
        self.BUTTON_L2 = 6
        self.BUTTON_R2 = 7

        self.BUTTON_SHARE = 8
        self.BUTTON_OPTIONS = 9

        self.BUTTON_LEFT_STICK = 10
        self.BUTTON_RIGHT_STICK = 11

        self.BUTTON_PS = 5
        self.BUTTON_PAD = 13

        # Labels for DS4 controller hats (Only one hat control)
        self.HAT_1 = 0

        self.axis = {}
        self.button = {}
        self.hat = {}

    def initRemote(self):
        pygame.init()
        pygame.joystick.init()

        controller = pygame.joystick.Joystick(0)
        controller.init()

        # Three types of controls: axis, button, and hat
        

        # Assign initial data values
        # Axes are initialized to 0.0
        for i in range(controller.get_numaxes()):
            self.axis[i] = 0.0
        # Buttons are initialized to False
        for i in range(controller.get_numbuttons()):
            self.button[i] = False
        # Hats are initialized to 0
        for i in range(controller.get_numhats()):
            self.hat[i] = (0, 0)

class Tools:
    def scale(val, src, dst):
        """
        Scale the given value from the scale of src to the scale of dst.
    
        val: float or int
        src: tuple
        dst: tuple
    
        example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
        """
        return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

    def clamp(value,floor=-100,ceil=100):
        return max(min(value,ceil),floor)

class PS4BT:
    def __init__(self,COM,invert_speed = False,invert_turn= True):
        self.INVERT_SPEED = invert_speed
        self.INVERT_TURN = invert_turn
        self.EV3 = None
        self.startBT(COM)
        self.Controller = DualShock4()

    def startBT(self,COM_PORT):
        print("Connecting ... ")
        self.EV3 = serial.Serial(COM_PORT)
        print("Bluetooth Ready")
    
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
    

        


    def mainloop(self):
        while True:
            # Get events
            for event in pygame.event.get():

                if event.type == pygame.JOYAXISMOTION:
                    self.Controller.axis[event.axis] = round(event.value,3)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.Controller.button[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.Controller.button[event.button] = False


            quitbt = self.Controller.button[self.Controller.BUTTON_PS]
            if(quitbt):
                s = EV3BT.encodeMessage(EV3BT.MessageType.Logic, 'done', True)
                self.EV3.write(s)
                break
            
            
            speed =Tools().scale(self.Controller.axis[self.Controller.AXIS_LEFT_STICK_Y], (-1,1), (-100,100))

            if(self.INVERT_SPEED):
                speed *=-1
            
            turn = Tools().scale(self.Controller.axis[self.Controller.AXIS_LEFT_STICK_X], (-1,1), (-100,100))
            if(self.INVERT_TURN):
                turn *=-1
        ##    #Dead Zone
            if(speed < 6 and speed > -6):
                speed = 0
            if(turn < 6 and turn > -6):
                turn = 0

            right_dc = Tools().clamp(-speed-turn)
            left_dc = Tools().clamp(-speed+turn)


            s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, 'rightM', right_dc)
            self.EV3.write(s)

            s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, 'leftM', left_dc)
            self.EV3.write(s)
        ##

            time.sleep(.01)

        self.EV3.close()
    




