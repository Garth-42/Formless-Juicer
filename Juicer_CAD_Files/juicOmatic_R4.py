# Write driver so can turn whichever pump I want to

# Write COM connections so open and close before and after reading from them?

import tkinter as tk
from tkinter import messagebox
import serial
import time

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        global loadCell
        global pumps
        global pump_state
        pump_state = False
        pumps = serial.Serial()
        loadCell = serial.Serial()
        self.startSerial()
    
    def ok(self):
        global vol
        print( "Volume:", self.drink_vol.get(), "Recipe is ", self.drink_recipe.get())
        if self.drink_recipe.get() == "Run Pump 1":
            self.fillToWeight(1,1000)
        elif self.drink_recipe.get() == "Run Pump 2":
            self.fillToWeight(2,1000)
        elif self.drink_recipe.get() == "Run Pump 3":
            self.fillToWeight(3,1000)
        elif self.drink_recipe.get() == "Emperors Cleanse":
            
            # Total oz of drink selected
            sel_oz = vol[self.drink_vol.get()]

            # Ratio of ingredients to whole amount
            ratio_1 = .20
            ratio_2 = .50
            ratio_3 = .30
            print("Filling bottle with Emperors Cleanse!")
            print(ratio_1*sel_oz)

            self.fillToWeight(1, ratio_1*sel_oz)
            self.fillToWeight(2, ratio_2*sel_oz)
            self.fillToWeight(3, ratio_3*sel_oz)
        
        elif(self.drink_recipe.get() == "Calibrate Load Cells"):
            loadCell.write(('c\n').encode()) # Enter calibration mode
            messagebox.showinfo(message="Remove everything from scale.")
            time.sleep(0.42)
            loadCell.write(('n\n').encode()) # Signal ready to device for reading
            messagebox.showinfo(message="Scale zero calibrated. Now Place 10 oz object on scale.")
            time.sleep(0.42)
            loadCell.write(('n\n').encode())
            time.sleep(0.42)
            loadCell.write(('10\n').encode()) # Send device calibration weight data
            messagebox.showinfo(message="Calibration complete!")
            

    def startSerial(self):
        loadCell.baudrate = 9600
        loadCell.port = 'COM7'
        loadCell.open()
        pumps.baudrate = 9600
        pumps.port = 'COM6'
        pumps.open()
        print('serial started')
        self.readLoadCell()

    def stopSerial(self):
        loadCell.close()
        pumps.close()

    def readLoadCell(self):
        # https://stackoverflow.com/questions/1093598/pyserial-how-to-read-the-last-line-sent-from-a-serial-device
        global readSerial_after_id
        global last_received
        
        while True:
            time.sleep(.1)
            # Get new values from the sensor
            buffer_string = ''
            buffer_string = buffer_string + loadCell.read(loadCell.inWaiting()).decode()
            lines = buffer_string.split('\n') # Guaranteed to have at least 2 entries
            try:
                last_received = lines[-2]
                try:
                    return float(last_received.rstrip())
                except ValueError:
                    pass
            except IndexError:
                pass



    def on_closing(self):
        self.stopSerial()
        root.destroy()

    def fillToWeight(self, pump, adtl_wt):
        # Pass in the pump to turn and the weight to add to the current weight
        
        wt_init = self.readLoadCell() # This is the initial weight on the platform before dispensing
        #print("Moving pumps!")
        pumps.write(('Turn'+str(pump)+'\n').encode())# pumps.write(('Turn' + pump + '\n').encode())
        pump_state = True
        print("moving pump " + str(pump))
        while(adtl_wt + wt_init > self.readLoadCell()):
            time.sleep(0.1)
            print(str(self.readLoadCell())) # Need to call the function within a while loop as while blocks other code even though have a .after method??
        pumps.write('Stop\n'.encode())# pumps.write(('Stop' + pump + '\n').encode())
        print("Stopping pump!")

    def create_widgets(self):
        global vol
        self.l_frame = tk.Frame(master=self, width=200, height=100, bg="red")
        self.r_frame = tk.Frame(master=self, width=100, bg="yellow")
        # Displays the weight reading coming from the sensor
        # self.reading = tk.Text(self, height=2, width=30)
        # self.reading.insert(tk.END, "Just a text Widget\nin two lines\n")
        # self.reading.pack()

        # Displays okay button to confirm selection on the menu
        self.btn_okay = tk.Button(self.r_frame,font=('Helvetica',28), height = 4, width = 10)
        self.btn_okay["text"] = "OKAY"
        self.btn_okay["command"] = self.ok
        self.btn_okay.pack()
        
        # Displays the possible drink volumes to dispense
        drink_vol_list =[
            "16 oz",
            "24 oz",
            "32 oz",
            "1 gallon"
        ]
        vol = {"16 oz":16, "24 oz": 24, "32 oz":32, "1 gallon": 128}
        self.drink_vol = tk.StringVar(self)
        self.drink_vol.set(drink_vol_list[0])
        self.dispenseAmt = tk.OptionMenu(self.l_frame, self.drink_vol, *drink_vol_list)
        self.dispenseAmt.config(font=('Helvetica',28), height = 2, width = 18) # sets drop down button font
        menu = self.nametowidget(self.dispenseAmt.menuname)
        menu.config(font=('Helvetica',28)) # set the drop down menu font
        self.dispenseAmt.pack()

        # Displays a list of the available recipes
        drink_recipe_list =[
            "Emperors Cleanse",
            "Run Pump 1",
            "Run Pump 2",
            "Run Pump 3",
            "Calibrate Load Cells" # Create a popup menu with data output and or instructions
        ]
        self.drink_recipe = tk.StringVar(self)
        self.drink_recipe.set(drink_recipe_list[0])
        self.recipes = tk.OptionMenu(self.l_frame,self.drink_recipe, *drink_recipe_list)
        self.recipes.config(font=('Helvetica',28), height = 2, width = 18) # sets drop down button font
        menu = self.nametowidget(self.recipes.menuname)
        menu.config(font=('Helvetica',28)) # set the drop down menu font
        self.recipes.pack()

        self.l_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.r_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
root = tk.Tk()
app = Application(master=root)

app.mainloop()


# 7.461
# Exception in Tkinter callback
# Traceback (most recent call last):
#   File "C:\Users\garth\Anaconda3\lib\tkinter\__init__.py", line 1705, in __call__
#     return self.func(*args)
#   File "c:/Users/garth/Desktop/JuicOmatic/juicOmatic_R3.py", line 45, in ok
#     self.fillToWeight(2, ratio_2*sel_oz)
#   File "c:/Users/garth/Desktop/JuicOmatic/juicOmatic_R3.py", line 97, in fillToWeight
#     while(adtl_wt + wt_init > self.readLoadCell()):
#   File "c:/Users/garth/Desktop/JuicOmatic/juicOmatic_R3.py", line 87, in readLoadCell
#     return float(last_received.rstrip())
# ValueError: could not convert string to float:

#Erratically can't open the COM port for the UNO using the load cell... after disconnecting the usb hub that
#everything was connected to and only using the uno, not having issues anymore?
#also manually changed the unos port from 3 to 7 in device manager
#previously had a keyboard, mouse, and the 2 arduinos connected to the usb hub, disconnected the keyboard and the mouse and now I am not getting the permission error?