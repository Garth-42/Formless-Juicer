# https://stackoverflow.com/questions/35724405/pyserial-get-the-name-of-the-device-behind-a-com-port
# import serial
# import serial.tools
import serial.tools.list_ports

def listPorts():
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

if __name__ == "__main__":
    devices = listPorts()[1]
    for device in devices:
        if str(device).find("Mega 2560") != -1:
            port = str(device)[str(device).find("(")+1:-1]
            print(port)
        if str(device).find("Uno") != -1:
            port = str(device)[str(device).find("(")+1:-1]
            print(port)