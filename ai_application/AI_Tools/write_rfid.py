from ai_application.Database.GlobalVariable import * 
Global = GlobalVariable()
import threading
import sys
import time, cv2
import numpy as np
from tkinter import SEL
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import fins.tcp
import time
from datetime import datetime

class write_rfid(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fins_instance = fins.tcp.TCPFinsConnection()
        self.plc_ip = '192.168.250.1' #!<- input your data
    
    
    def writeDmDec(self, int_to_write, word_address=0):
        try:
            int_to_write = int(int_to_write)
        except ValueError:
            print(f"Cannot convert {int_to_write} to an integer.")
            return  # Exit the function
        
        self.fins_instance.write(int_to_write, 'd', word_address, 'ui')

    def writeNone(self, word_address=0, number_of_values=1):
        for i in range(number_of_values):
            current_address = word_address + i
            self.fins_instance.write(0, 'd', current_address, 'ui')

    def swap_digits(self, string_list):
        new_list = [s[::-1] if len(s) > 1 else s for s in string_list]
        return new_list

    def convert_string_to_chunks(self, s, chunk_size=2):
        chunks = []
        for i in range(0, len(s), chunk_size):
            chunks.append(s[i:i+chunk_size])
        chunks = self.swap_digits(chunks)
        return chunks

    def writeDmWordFromList(self, string_list, word_address=0):
        ascii_values = []
        for element in string_list:
            for char in element:
                ascii_values.append(ord(char))
        
        for i in range(0, len(ascii_values), 2):
            value = ascii_values[i] << 8  # Shift the first character to the high byte
            if i + 1 < len(ascii_values):
                value |= ascii_values[i + 1]  # Combine the second character into the low byte
            
            word_addr = word_address + i // 2
            self.fins_instance.write(value, memory_area='d', word_address=word_addr, data_type='ui')

    def readDmWord(self, word_address=0, number_of_values=1):
        response = self.fins_instance.read('d', word_address, 'ui', number_of_values)
        if isinstance(response, list):
            hex_responses = [hex(value) for value in response]
        result_str = ''
        for res in hex_responses:
            int_value = int(res, 16)
            bytes_value = int_value.to_bytes(2, byteorder='big')
            swapped_bytes = bytes_value[::-1]
            swapped_int = int.from_bytes(swapped_bytes, byteorder='big')
            swapped_hex = f"0x{swapped_int:04X}"
            hex_str = swapped_hex[2:]  # Skip '0x'
            for i in range(0, len(hex_str), 2):
                if i+2 <= len(hex_str):  # Ensure there's a pair of characters to process
                    char = chr(int(hex_str[i:i+2], 16))
                    result_str += char
        return result_str

    def changeAddrTag(self, word_address=0, hex_string='0x55a', num_word=0):
        integer_value = int(hex_string, 16)
        self.writeDmDec(integer_value, word_address)
        self.writeDmDec(num_word, word_address + 1)

    def fnWriteRfidTag(self, device=0, string_to_write='', num=60): #device=3000
        if num>0:
            self.writeNone((device+110), num) # clear buffer data
            time.sleep(0.1)
            list_str_to_write = self.convert_string_to_chunks(string_to_write.strip())
            self.writeDmWordFromList(list_str_to_write, (device+110))
            time.sleep(0.2)
            dev = int(device/100)
            self.writeDmDec(dev, (device+100)) 
            time.sleep(0.3)
            self.writeDmDec(1, (device+101))
            time.sleep(0.5)
            self.writeDmDec(0, (device+101))

            time.sleep(0.1)
            result = self.readDmWord((device+110), 30)
            # print(result)
            time.sleep(0.2)
            self.writeDmDec(0, (device+100)) # change to mode read


    def run(self):
        self.fins_instance.connect(self.plc_ip)
        print(f"Successfully connected to PLC : {self.plc_ip}")
        device = 3000 #!<- input your data
        address_tag = '0x080' #!<- input your data
        num = 60 #!<- input your data
        self.changeAddrTag(device, address_tag, num)
        self.buffer_text = ''
        while True :
            if Global.hasGlobal('rfid_text') :
                if Global.getGlobal('rfid_text') != '' :
                    try:
                        # timestamp = time.time()
                        # bangkok_offset = 7 * 3600  # 7 hours in seconds
                        # bangkok_timestamp = timestamp + bangkok_offset
                        # formatted_datetime = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime(bangkok_timestamp))

                        # string_to_write = formatted_datetime #!<- input your data
                        # self.fnWriteRfidTag(device, string_to_write, num)
                        text = Global.getGlobal('rfid_text')
                        self.fnWriteRfidTag(device, text, num)
                        if self.buffer_text != text :
                            print(f"Write data to RFID : {text} @ {text}")
                            self.buffer_text = text

                    except Exception as e:
                        print(f"Failed to connect to {self.plc_ip}: {e}")
                else :
                    time.sleep(0.2)

            else :
                time.sleep(0.2)

app = QApplication(sys.argv)
