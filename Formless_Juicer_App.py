# to find COM ports:
# in terminal: dmesg | grep tty
# https://stackoverflow.com/questions/35724405/pyserial-get-the-name-of-the-device-behind-a-com-port


import tkinter as tk
from tkinter import messagebox
import serial
import time
import serial.tools.list_ports

# Linux: '/dev/ttyACM0'
# Windows: 'COM6'
# load_cell_port = "COM7"
# pumps_port = "COM6"

global os
#os = "Linux"
os = "Windows"

def listPorts():
    # https://stackoverflow.com/questions/35724405/pyserial-get-the-name-of-the-device-behind-a-com-port
    """!
    @brief Provide a list of names of serial ports that can be opened as well as a
    a list of Arduino models.
    @return A tuple of the port list and a corresponding list of device descriptions
    """

    ports = list( serial.tools.list_ports.comports() )

    resultPorts = []
    descriptions = []
    for port in ports:
        if not port.description.startswith( "Arduino" ):
            # correct for the somewhat questionable design choice for the USB
            # description of the Arduino Uno
            if port.manufacturer is not None:
                if port.manufacturer.startswith( "Arduino" ) and \
                port.device.endswith( port.description ):
                    port.description = "Arduino Uno"
                else:
                    continue
            else:
                continue
        if port.device:
            resultPorts.append( port.device )
            descriptions.append( str( port.description ) )

    return (resultPorts, descriptions)           


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
            self.fillToWeight(1,10)
        elif self.drink_recipe.get() == "Run Pump 2":
            self.fillToWeight(2,10)
        elif self.drink_recipe.get() == "Run Pump 3":
            self.fillToWeight(3,10)
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
        # Assign COM ports
        global os
        devices = listPorts()[1]
        for device in devices:
            if os == "Windows":
                if str(device).find("Mega 2560") != -1:
                    port = str(device)[str(device).find("(")+1:-1]
                    print(port)
                    pumps_port = port
                if str(device).find("Uno") != -1:
                    port = str(device)[str(device).find("(")+1:-1]
                    print(port)
                    load_cell_port = port
                else:
                    print("no pump or load cell found")
            elif os == "Linux":
                if str(device).find("Mega 2560") != -1:
                    port = str(device)[str(device).find("(")+1:-1]
                    print(port)
                    pumps_port = port
                if str(device).find("Uno") != -1:
                    port = str(device)[str(device).find("(")+1:-1]
                    print(port)
                    load_cell_port = port
                else:
                    print("no pump or load cell found")
            else:
                print("OS isn''t recognized")

        loadCell.baudrate = 9600
        loadCell.port = load_cell_port
        loadCell.open()
        pumps.baudrate = 9600
        pumps.port = pumps_port
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
        tries = 0

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
                    print(ValueError)
            except IndexError:
                print(IndexError)
            tries = tries + 1
            if tries > 5:
                print("failed to retrieve data") 
                return "Failed to get load cell data"



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
        self.l_frame = tk.Frame(master=self, width=400, height=800, bg="red")
        self.r_frame = tk.Frame(master=self, width=200, bg="yellow")
        
        l_box_h = 5
        l_box_w = 18
        l_text = 22
        
        # Displays the weight reading coming from the sensor
        # self.reading = tk.Text(self, height=2, width=30)
        # self.reading.insert(tk.END, "Just a text Widget\nin two lines\n")
        # self.reading.pack()

        # Displays okay button to confirm selection on the menu
        self.btn_okay = tk.Button(self.r_frame,font=('Helvetica',24), height =4, width = 18)
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
        self.dispenseAmt.config(font=('Helvetica',l_text), height = l_box_h, width = l_box_w) # sets drop down button font
        menu = self.nametowidget(self.dispenseAmt.menuname)
        menu.config(font=('Helvetica',l_text)) # set the drop down menu font
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
        self.recipes.config(font=('Helvetica', l_text), height = l_box_h, width = l_box_w) # sets drop down button font
        menu = self.nametowidget(self.recipes.menuname)
        menu.config(font=('Helvetica',l_text)) # set the drop down menu font
        self.recipes.pack()

        self.l_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.r_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
root = tk.Tk()
app = Application(master=root)

app.mainloop()