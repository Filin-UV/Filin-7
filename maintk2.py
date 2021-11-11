
import cv2
import numpy
import time
import subprocess
import sys
from sys import platform
import tkinter
import tkinter.messagebox
from tkinter.ttk import Frame, Label, Style
import PIL.Image, PIL.ImageTk
import time
import board
import adafruit_dht
import struct
import smbus
import sys
import time
import os
from RPi import GPIO
import datetime
import localisation
from itertools import cycle
import configparser

width = 480  #480
height = 320 #320
vid_width = 385  #480
vid_height = 255 #320

clk = 22
dt = 27
sw = 17
clicked = False
cursor_pos = 0
prev_cursor_pos = 1
charge = 0
UV_saturation = 80
UV_threshold = 178.5
timediff = 0
bat_image = "/home/pi/Filin7-RPi/pics/bat20.png"
bat20 = "/home/pi/Filin7-RPi/pics/bat20.png"
bat30 = "/home/pi/Filin7-RPi/pics/bat30.png"
bat50 = "/home/pi/Filin7-RPi/pics/bat50.png"
bat75 = "/home/pi/Filin7-RPi/pics/bat75.png"
bat100 = "/home/pi/Filin7-RPi/pics/bat100.png"
batonline = "/home/pi/Filin7-RPi/pics/batonline.png"
photopath = "/home/pi/Filin7-RPi/photo/"
videopath = "/home/pi/Filin7-RPi/video/"
modes = cycle([3, 4, 5])
modes_num = cycle([0, 1, 2])
languages_num = cycle([0, 1, 2])
time_zones = cycle([0,1,2,3,4,5,6,7,8,9,10,11,12,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1])
settings_screen = False
record_flag = False
charger = False
updating_flag = False



dictionary = []
cursor_max = 4
temp_text = ""
humid_text = ""


class App:
    def __init__(self, window, window_title):
        #self.constants
        self.nonactive_color = "#555"
        self.active_color = "#f50"

        #self.variables
        self.mode = 0
        self.mode_txt = dictionary[3]
        self.timer = 0
        self.temp = 0
        self.humid = 0
        
        #code
        self.PeripheryInit()
        self.WindowConstruct(window, window_title)
        self.detectActivePort()
        try:
            self.video_source1 = self.available_ports[0]
        except IndexError as error:
            tkinter.messagebox.showerror(title = "Error", message = "Cam1 is not available \n Please contact the manufacturer")
        try:
            self.video_source2 = self.available_ports[1]
        except IndexError as error:
            tkinter.messagebox.showerror(title = "Error", message = "Cam2 is not available \n Please contact the manufacturer")
        self.vid = MyVideoCapture(self.video_source1,self.video_source2)
        
        self.delay = 1
        self.update()
        
        self.window.mainloop()
        
    def PeripheryInit(self):
        self.dhtdev = adafruit_dht.DHT22(board.D25)
        self.bus = smbus.SMBus(1)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(6, GPIO.IN)
        clkLastState = GPIO.input(clk)
        dtLastState = GPIO.input(dt)
        swLastState = GPIO.input(sw)        
        GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=100)
        GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=100)
        GPIO.add_event_detect(sw, GPIO.FALLING, callback=swClicked, bouncetime=200)    
        GPIO.add_event_detect(6, GPIO.BOTH, callback=charger_event)
        
    def WindowConstruct(self, window, window_title):
        global temp
        global humid
        global vid_width
        global vid_height
        self.window = window
        self.window.title(window_title)
        self.window.geometry('{}x{}'.format(width,height))
        self.style = Style()
        self.style.theme_use("default")
        
        self.canvas = tkinter.Canvas(window)
        self.canvas.place(relx=0.001,rely=0.005, relwidth = 0.845, relheight = 0.845)

        self.bat_level = tkinter.Label(window, text = "{}%".format(charge),height = 1)       
        self.bat_level.place(relx=0.65, y=vid_height+5)
        self.bat_canvas = tkinter.Canvas(window)
        self.bat_canvas.place(relx=0.725,y=vid_height+3)
        self.bat_ind = PIL.ImageTk.PhotoImage(image=PIL.Image.open(bat_image))
        self.bat_canvas.create_image(0,0,image=self.bat_ind,anchor=tkinter.NW)
        
        self.mode_label = tkinter.Label(window, text = "{}\n{}".format(dictionary[2],self.mode_txt), width = 10,height = 2, bd=3, relief = tkinter.GROOVE ,background = self.nonactive_color)
        self.mode_label.place(relx=0.815, rely=0.005)
        
        self.gain_label = tkinter.Label(window, text = "{}:\n{}%".format(dictionary[6], int((255-UV_threshold)/2.55)), width = 10,height = 2, bd=3, relief = tkinter.GROOVE ,background = self.nonactive_color)
        self.gain_label.place(relx=0.815, rely=0.166)

        self.label3 = tkinter.Label(window, text = "{}".format(dictionary[7]), width = 10,height = 2, bd=3, relief = tkinter.GROOVE ,background = self.nonactive_color)
        self.label3.place(relx=0.815, rely=0.333)

        self.label4 = tkinter.Label(window, text = "{}".format(dictionary[8]), width = 10,height = 2, bd=3, relief = tkinter.GROOVE ,background = self.nonactive_color)
        self.label4.place(relx=0.815, rely=0.5)
        
        self.settings_label = tkinter.Label(window, text = "{}".format(dictionary[1]), width = 10,height = 2, bd=3, relief = tkinter.GROOVE ,background = self.nonactive_color)
        self.settings_label.place(relx=0.815, rely=0.667)
        
    def detectActivePort(self):
        self.dev_port = 0
        self.available_ports = []
        while self.dev_port < 6:#is_working:
            self.camera = cv2.VideoCapture(self.dev_port)
            if self.camera.isOpened():
                print("Port %s is working." %self.dev_port)
                self.available_ports.append(self.dev_port)
            else:
                print("Port %s is not working!!!" %self.dev_port)
            #self.camera.release()
            self.dev_port +=1
        print(self.available_ports)

    
    def refresh_colors(self, activePos, prevactivePos):
        global prev_cursor_pos
        
        if prevactivePos == 0 or prevactivePos == 5:
                self.mode_label["background"] = self.nonactive_color
        elif prevactivePos == 1 or prevactivePos == 6:
                self.gain_label["background"] = self.nonactive_color
        elif prevactivePos == 2 or prevactivePos == 7:
                self.label3["background"] = self.nonactive_color
        elif prevactivePos == 3 or prevactivePos == 8:
                self.label4["background"] = self.nonactive_color
        elif prevactivePos == 4 or prevactivePos == 9:
                self.settings_label["background"] = self.nonactive_color
        prev_cursor_pos = cursor_pos        
        if activePos == 0 or activePos == 5:
                print("\n!!!!!!ActPos==0!!!!!!!\n")
                self.mode_label["background"] = self.active_color
        elif activePos == 1 or activePos == 6:
                print("\n!!!!!!ActPos==1!!!!!!!\n")
                self.gain_label["background"] = self.active_color
        elif activePos == 2 or activePos == 7:
                print("\n!!!!!!ActPos==2!!!!!!!\n")
                self.label3["background"] = self.active_color
        elif activePos == 3 or activePos == 8:
                print("\n!!!!!!ActPos==3!!!!!!!\n")
                self.label4["background"] = self.active_color
        elif activePos == 4 or activePos == 9:
                print("\n!!!!!!ActPos==4!!!!!!!\n")
                self.settings_label["background"] = self.active_color
        
    def update(self):
        global cursor_pos
        global clicked
        global settings_screen
        global dictionary
        global tz
        global out
        global record_flag
        global updating_flag
        
        self.bat_ind = PIL.ImageTk.PhotoImage(image=PIL.Image.open(bat_image))
        self.bat_canvas.create_image(0,0,image=self.bat_ind,anchor=tkinter.NW)
        date = "{}".format((datetime.datetime.now() + datetime.timedelta(hours=timediff))
                           .strftime("%d/%m/%Y %H:%M:%S"))
        ret1, frame1, ret2, frame2 = self.vid.get_frame()
        if ret1 & ret2:
            if self.mode == 0:
                frame3 = MyVideoCapture.mix_frame(frame2, frame1)
                frame = frame3
            elif self.mode == 1:
                frame = frame2
            elif self.mode == 2:
                frame = frame1
            frame = cv2.putText(frame, temp_text, (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            frame = cv2.putText(frame, humid_text, (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            frame = cv2.putText(frame, date, (200,240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            print("recflag {}".format(record_flag))
            if record_flag:
                out.write(frame)
                print("saved")
                frame = cv2.circle(frame, (330,15), 4, (255,0,0), 5)
                frame = cv2.putText(frame, "REC", (338,18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo,anchor=tkinter.NW)
        if self.timer == 10:
            self.getmeteodata()
            self.getbatinfo()
            self.bat_level["text"] = "{}%".format(int(charge))
            self.timer = 0
        else:
            self.timer= self.timer + 1
        if cursor_pos != prev_cursor_pos:
                self.refresh_colors(cursor_pos, prev_cursor_pos)
        if clicked:
            if cursor_pos == 0:
                self.mode_txt = dictionary[next(modes)]
                print(self.mode_txt)
                self.mode = next(modes_num)
                print(self.mode)
                self.mode_label["text"] = "{}\n{}".format(dictionary[2],self.mode_txt)
            elif cursor_pos == 1:
                global UV_threshold
                if UV_threshold > 0:
                    UV_threshold = UV_threshold - 25.5
                else:
                    UV_threshold = 255
                self.gain_label["text"] = "{}:\n{}%".format(dictionary[6], int((255-UV_threshold)/2.55))
            elif cursor_pos == 2:
                if self.mode == 0:
                    name = "MXD-"
                elif self.mode == 1:
                    name = "UV-"
                elif self.mode == 2:
                    name = "DSC-"
                bl, gr, rd = cv2.split(frame)
                frame_ph = cv2.merge([rd, gr, bl])
                name = "".join([photopath,name, (datetime.datetime.today() + datetime.timedelta(hours=timediff)).strftime("%d-%m-%Y_%H-%M-%S"), ".jpg"])
                ph = cv2.imwrite(name, frame_ph)
            elif cursor_pos == 3:
                record_flag = not record_flag
                if record_flag:
                    if self.mode == 0:
                        video_name = "MXV-"
                    elif self.mode == 1:
                        video_name = "UVV-"
                    elif self.mode == 2:
                        video_name = "VID-"
                    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                    video_name = "".join([videopath,video_name, (datetime.datetime.today() + datetime.timedelta(hours=timediff)).strftime("%d-%m-%Y_%H-%M-%S"), ".avi"])
                    out = cv2.VideoWriter(video_name, fourcc, 10.0, (numpy.shape(frame)[0],  numpy.shape(frame)[1]))
                if not record_flag:
                    out.release()
                pass
            elif cursor_pos == 4:
                settings_screen = True
                cursor_pos = 5
                self.mode_label["text"] = "{}:\n{}".format(dictionary[11], dictionary[12])
                if(timediff>=0):
                    tz = "+{}".format(timediff)
                else:
                    tz = "{}".format(timediff)
                self.gain_label["text"] = "{}:\n UTC{}".format(dictionary[13],tz)

                self.label3["text"] = "{}:\n{}".format(dictionary[15],dictionary[16])
                self.label4["text"] = "{}".format(dictionary[18])
                self.settings_label["text"] = "{}".format(dictionary[14])

            elif cursor_pos == 5:
                
                current_lang = next(languages_num)
                dictionary = localisation.change_lang(current_lang)
                self.mode_label["text"] = "{}:\n{}".format(dictionary[11],dictionary[12])
                self.gain_label["text"] = "{}:\n UTC{}".format(dictionary[13],tz)
                self.settings_label["text"] = "{}".format(dictionary[14])
                self.label3["text"] = "{}:\n{}".format(dictionary[15],dictionary[16])
                self.label4["text"] = "{}".format(dictionary[18])
                config.set("settings","language", str(current_lang))
                with open("config.ini","w") as config_file:
                    config.write(config_file)
                    
            elif cursor_pos == 6:
                current_tz = next(time_zones)
                if(current_tz>=0):
                    tz = "+{}".format(current_tz)
                else:
                    tz = "{}".format(current_tz)
                self.gain_label["text"] = "{}:\n UTC{}".format(dictionary[13],tz)
                config.set("settings","timediff", str(current_tz))
                with open("config.ini","w") as config_file:
                    config.write(config_file)

            elif cursor_pos == 7:
                print(dictionary)
                pass
            elif cursor_pos == 8:
                self.window.destroy()
                subprocess.Popen("/home/pi/Filin7-RPi/updatesoft.sh")
                os._exit
                pass
            elif cursor_pos == 9:
                settings_screen = False
                cursor_pos = 0
                print(dictionary)
                self.mode_txt = dictionary[3]
                self.mode_label["text"] = "{}\n{}".format(dictionary[2],self.mode_txt) 
                self.gain_label["text"] = "{}:\n{}%".format(dictionary[6], int((255-UV_threshold)/2.55))
                self.label3["text"] = "{}".format(dictionary[7])
                self.label4["text"] = "{}".format(dictionary[8])
                self.settings_label["text"] = "{}".format(dictionary[1])
                
            clicked = False
            
        self.window.after(self.delay, self.update)

    def getmeteodata(self):
        global temp_text
        global humid_text
        try:
            temp = 25#self.dhtdev.temperature
            humid = 60#self.dhtdev.humidity
            temp_text = "Temp:{}C".format(temp)
            humid_text = "Humid:{}%".format(humid)
            #print(" temp: {:.1f} C Humid: {}%".format(temp, humid))
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
        except Exception as error:
            self.dhtdev.exit()
            raise error
        
    def getbatinfo(self):
        global bat_image
        global charge
        charge = self.readCapacity(self.bus)
        if charger and charge < 100:
            bat_image = batonline
        else:
            if charge > 75:
                bat_image = bat100
            elif charge <=75 and charge > 50:
                bat_image = bat75
            elif charge <= 50 and charge > 30:
                bat_image = bat50
            elif charge <= 30 and charge > 20:
                bat_image = bat30
            elif charge <= 20:
                bat_image = bat20
        
            
        #print ("Voltage:{:.1f}V Battery:{:.1f}%".format(self.readVoltage(self.bus), self.readCapacity(self.bus)))

    def readVoltage(self, bus):
        self.address = 0x36
        self.read = self.bus.read_word_data(self.address, 2)
        self.swapped = struct.unpack("<H", struct.pack(">H", self.read))[0]
        self.voltage = self.swapped * 1.25 /1000/16
        return self.voltage

    def readCapacity(self, bus):
        global charge
        self.address = 0x36
        self.read = self.bus.read_word_data(self.address, 4)
        self.swapped = struct.unpack("<H", struct.pack(">H", self.read))[0]
        self.capacity = self.swapped/256
        charge = self.capacity
        return self.capacity
        
class MyVideoCapture:
    def __init__(self, video_source1,video_source2):
        self.vid1 = cv2.VideoCapture(video_source1)
        self.vid2 = cv2.VideoCapture(video_source2)
        if not self.vid1.isOpened():
            raise ValueError("Cam1 is not available")
        if not self.vid2.isOpened():
            raise ValueError("Cam2 is not available")
        self.width1 = self.vid1.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height1 = self.vid1.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width2 = self.vid2.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height2 = self.vid2.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid1.isOpened() & self.vid2.isOpened():
            ret1, frame1 = self.vid1.read()
            ret2, frame2 = self.vid2.read()
            if ret1 & ret2:
                frame1 = cv2.resize(frame1, (vid_width, vid_height), cv2.INTER_LINEAR)
                frame2 = cv2.resize(frame2, (vid_width, vid_height), cv2.INTER_LINEAR)
                return (ret1, cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB), ret1, cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
            else:
                return (ret1, None,ret2, None)
        else:
            return (ret1, None,ret2, None)
        
    def mix_frame(UV_frame, vis_frame):
        UV_smooth = cv2.medianBlur(UV_frame, 3)
        #print(image1_smooth)
        UV_thrhold = cv2.threshold(UV_smooth, UV_threshold, 255, cv2.THRESH_BINARY)
        frame3 = cv2.addWeighted(vis_frame, 1, UV_thrhold[1], UV_saturation, 0)
        return frame3

    def __del__(self):
        if self.vid1.isOpened():
            self.vid1.release()
        if self.vid2.isOpened():
            self.vid2.release()
            
def clkClicked(channel):
        global cursor_pos
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        print(settings_screen)
        if not settings_screen:
            if clkState == 0 and dtState == 1 and cursor_pos < cursor_max:
                cursor_pos = cursor_pos + 1
                print ("Counter ", cursor_pos)
        elif settings_screen:
            if clkState == 0 and dtState == 1 and cursor_pos < 9:
                cursor_pos = cursor_pos + 1
                print ("Counter ", cursor_pos)
                
def dtClicked(channel):
        global cursor_pos
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
        print(settings_screen)
        if not settings_screen:
            if clkState == 1 and dtState == 0 and cursor_pos > 0:
                cursor_pos = cursor_pos - 1
                print ("Counter ", cursor_pos)
        elif settings_screen:
            if clkState == 0 and dtState == 1 and cursor_pos > 5:
                cursor_pos = cursor_pos - 1
                print ("Counter ", cursor_pos)

def swClicked(channel):
        global clicked
        clicked = True
        print ("Clicked")
        
def charger_event(channel):
    global charger
    if GPIO.input(6):     # if port 6 == 1
        charger = False
        print("---AC Power Loss OR Power Adapter Failure---")
    else:                  # if port 6 != 1
        charger = True
        print("---AC Power OK,Power Adapter OK---")


config = configparser.ConfigParser()
config.read('config.ini')
timediff = int(config["settings"]["timediff"])
language = int(config["settings"]["language"])
print(timediff)
print(language)


dictionary = localisation.change_lang(language)
print(dictionary)
MainWindow = App(tkinter.Tk(), dictionary[0])
