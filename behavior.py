# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:00:35 2019

@author: Eraguzin
"""
from myhdl import block, delay, always, now, Signal, intbv
from PIL import ImageGrab
import os, sys
from Tkinter import W, CENTER
class the_blocks():
    def __init__(self):
        #Speed at which master FPGA clock pulses
        self.clock_pulse = 5
        self.w = None
        
        
        
    @block
    def blank_plotter(self,clk):
        @always(clk.posedge)
        def do_nothing():
            pass
        return do_nothing
        
    @block
    def plotter(self, clk):
        @always(clk.posedge)
        def create_image():
            self.master.update()
            ImageGrab.grab(bbox=self.box).save(os.getcwd() + "\Simulation_Output\{}".format(now()) + '.jpg')
        return create_image
    
    @block
    def light_deposit(self, clk, data0, data1, data2, data3):
        time = [200,450,800,1200]
        amplitudes = [Signal(intbv(210)[8:]), Signal(intbv(195)[8:]), Signal(intbv(152)[8:]), Signal(intbv(177)[8:])]
        outputs = [data0, data1, data2, data3]
        
        @always(clk.negedge)
        def light_deposit_things():
            for count, i in enumerate(time):
                if (now() == i):
                    outputs[count].next = amplitudes[count]
                else:
                    outputs[count].next = Signal(intbv(0)[8:])
                    
                if ((i - now()) > 0):
                    line = self.w.find_withtag("ASIC{}_line".format(count))
                    y_value = (200 * (count +1))
                    x_value = 700 + ((i - now())/5)
                    coord = (x_value,y_value,x_value + 50,y_value)
                    self.w.coords(line, coord)
                    
            
        return light_deposit_things
        
    @block
    def FPGA(self, clk, data_in, token_in, token_out):
        #Get GUI elements sorted out
        token_out_line = self.w.find_withtag("daisy0")
#        print("FPGA Token Out is {}".format(token_out_line))
        previous_chip_lines = self.w.find_withtag("chip0")
        
        daisy_in = self.params['common_signals'] + self.params['daisy_signals'] - 1
        potential_token_in_line1 = self.w.find_withtag("common{}".format(daisy_in))
        
        token_in_line_tuple = tuple(set(potential_token_in_line1).intersection(set(previous_chip_lines)))
        if (len(token_in_line_tuple) == 1):
            token_in_line = token_in_line_tuple[0]
        else:
            sys.exit("behavior.py --> Found multiple options for an FPGA token line")
#        print("FPGA Token In is {}".format(token_in_line))
        
        clk_line = self.w.find_withtag("serial0")
#        print("FPGA Clock is {}".format(clk_line))
        
        potential_data_in_line = self.w.find_withtag("common0")
        data_in_line_tuple = tuple(set(potential_data_in_line).intersection(set(previous_chip_lines)))
        if (len(data_in_line_tuple) == 1):
            data_in_line = data_in_line_tuple[0]
        else:
            sys.exit("behavior.py --> Found multiple options for an FPGA data line")
#        print("FPGA Data In is {}".format(data_in_line))
        
        sent_signal = Signal(bool(0))
        prev_token_in = Signal(bool(0))
        @always(delay(self.clock_pulse))
        def drive_clk():
            clk.next = not clk
            
        @always(clk.negedge)
        def do_things():
            self.w.delete("fpga_status_text")
            
            self.w.create_text((self.params['FPGA_dims'][0] + 600), 
                (self.params['FPGA_dims'][3] - self.params['FPGA_dims'][1])/2, anchor = W, 
                text="Clock pulse at {} ns".format(now()), tag = "fpga_status_text")
            
            
            if (sent_signal == 0):
                token_out.next = (bool(1))
                self.w.create_text((self.params['FPGA_dims'][0] + 50), 
                (self.params['FPGA_dims'][3] - self.params['FPGA_dims'][1])/2, anchor = W, 
                text="Haven't sent token yet, will do it next pulse", tag = "fpga_status_text")
                
                sent_signal.next = Signal(bool(1))
                
            if (token_out == Signal(bool(1))):
                for i in token_out_line:
                    self.w.itemconfig(i, fill="green")
                token_out.next = Signal(bool(0))
                self.w.create_text((self.params['FPGA_dims'][0] + 50), 
                (self.params['FPGA_dims'][3] - self.params['FPGA_dims'][1])/2, anchor = W, 
                text="Token was sent, next pulse it will be lowered", tag = "fpga_status_text")
            else:
                for i in token_out_line:
                    self.w.itemconfig(i, fill="red")
                    
            if (token_in == Signal(bool(1))):
                self.w.create_text((self.params['FPGA_dims'][0] + 50), 
                (self.params['FPGA_dims'][3] - self.params['FPGA_dims'][1])/2, anchor = W, 
                text="Incoming token is high!", tag = "fpga_status_text")
            else:
                if (prev_token_in.val == 1):
                    self.w.create_text((self.params['FPGA_dims'][0] + 50), 
                    (self.params['FPGA_dims'][3] - self.params['FPGA_dims'][1])/2, anchor = W, 
                    text="Negative token in edge!", tag = "fpga_status_text")
                    sent_signal.next = Signal(bool(0))
            prev_token_in.next = token_in
                
        return drive_clk, do_things
    
    @block
    def ASIC(self, clk, data_in, data_out, token_in, token_out, data_input, num):
        #Get GUI elements sorted out
#        print("This is ASIC {}".format(num))
        potential_lines = self.w.find_withtag("chip{}".format(num))
        potential_common_in_lines = self.w.find_withtag("chip{}".format(num+1))
        potential_fpga_in_lines = self.w.find_withtag("daisy0")
        
        daisy_out = self.params['common_signals'] + self.params['daisy_signals'] - 1
        potential_token_line = self.w.find_withtag("common{}".format(daisy_out))
        token_out_line_tuple = tuple(set(potential_lines).intersection(set(potential_token_line)))
        if (len(token_out_line_tuple) == 1):
            token_out_line = token_out_line_tuple[0]
        else:
            sys.exit("behavior.py --> Found multiple options for a token out line")
#        print("ASIC {} Token Out is {}".format(num, token_out_line))
        
        #If this is the last chip, the token in will come from the FPGA daisy line
        if (len(potential_common_in_lines) == 0):
            token_in_line = potential_fpga_in_lines
        else:
            token_in_line_tuple = tuple(set(potential_common_in_lines).intersection(set(potential_token_line)))
            if (len(token_in_line_tuple) == 1):
                token_in_line = token_in_line_tuple[0]
            else:
                print("Potential common in lines are {}".format(potential_common_in_lines))
                print("Potential Token lines are {}".format(potential_token_line))
                print("And the combination is {}".format(token_in_line_tuple))
                sys.exit("behavior.py --> Found multiple options for a token in line")
#        print("ASIC {} Token In is {}".format(num, token_in_line))
        
        potential_data_out_line = self.w.find_withtag("common0")
        data_out_line_tuple = tuple(set(potential_lines).intersection(set(potential_data_out_line)))
        if (len(data_out_line_tuple) == 1):
            data_out_line = data_out_line_tuple[0]
        else:
            sys.exit("behavior.py --> Found multiple options for a data out line")
#        print("ASIC {} Data Out is {}".format(num, data_out_line))
        
        #If this is the last chip, the data in line will be open
        if (len(potential_common_in_lines) == 0):
            data_in_line = None
        else:
            potential_data_in_line = self.w.find_withtag("common0")
            data_in_line_tuple = tuple(set(potential_common_in_lines).intersection(set(potential_data_in_line)))
            if (len(data_in_line_tuple) == 1):
                data_in_line = data_in_line_tuple[0]
            else:
                print("Potential common in lines are {}".format(potential_common_in_lines))
                print("Potential Data in lines are {}".format(potential_data_in_line))
                print("And the combination is {}".format(data_in_line))
                sys.exit("behavior.py --> Found multiple options for a data in line")
                
        self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 25, 
                          self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])-25, 
                          text="Data Out", fill = "black", anchor=W)
        
        self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 185, 
                          self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])-25, 
                          text="Token Out", fill = "black", anchor=W)
        
        self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) - 75, 
                          self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1]) - 0, 
                          text="Clock", fill = "black", anchor=W)
#        print("ASIC {} Data In is {}".format(num, data_in_line))
                
        #Global variables workaround
        d = {"prev_token_in" : Signal(0),
             "read_out" : Signal(0)}
        data_used = Signal(intbv(1)[4:])
        input_counter = Signal(intbv(0)[4:])
        index = Signal(intbv(0)[8:])
        data_buffer0 = Signal(intbv(12)[8:])
        data_buffer1 = Signal(intbv(0)[8:])
        data_buffer2 = Signal(intbv(0)[8:])
        data_buffer3 = Signal(intbv(0)[8:])
        all_buffers = [data_buffer0, data_buffer1, data_buffer2, data_buffer3]
        
        def setup_buffers():
            for count,buff in enumerate(all_buffers):
                for j in range(len(buff)):
                    reversed_j = len(buff) - j - 1
                    dimensions = [(self.params['serial_signals'] * self.params['per_signal']) + (j * self.params['block_size']),
                               self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])
                               + (count * self.params['block_size']),
                               (self.params['serial_signals'] * self.params['per_signal']) + ((j+1) * self.params['block_size']),
                               self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])
                               + ((count+1) * self.params['block_size'])]
                    self.w.create_rectangle(dimensions, fill="white", tags=("block{}{}{}".format(num,count,reversed_j)))
                    text_x = (dimensions[2] + dimensions[0]) / 2
                    text_y = (dimensions[3] + dimensions[1]) / 2
                    if (data_used[count] == 1):
                        text="{}".format(int(buff[reversed_j]))
                    else:
                        text = "X"
                    self.w.create_text(text_x, text_y, text=text, fill = "black", 
                                       anchor=CENTER, tags=("block_text{}{}{}".format(num,count,reversed_j)))
                    
        setup_buffers()
        @always(clk.negedge)
        def do_things():
            self.w.delete("asic{}_status_text".format(num))
            #Check for light input
            if (data_input != 0):
                next_buffer = data_input
                all_buffers[data_used].next = next_buffer
                data_used.next = data_used+1
                self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 50, 
                      self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+85, 
                      text="Light input!", fill = "yellow", anchor=W, tag = "asic{}_status_text".format(num))
                for j in range(len(next_buffer)):
                    text_block = self.w.find_withtag("block_text{}{}{}".format(num,int(data_used),j))
                    self.w.itemconfig(text_block, text = "{}".format(int(next_buffer[j])))
            
            #Means the previous ASIC is sending its data after the first clock pulse
            if (token_in == bool(1)):
                input_counter.next = input_counter + 1
                self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 200, 
                      self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+70, 
                      text="Incoming token is high!", fill = "dark green", anchor=W, tag = "asic{}_status_text".format(num))
                buffer_to_write = all_buffers[data_used]
                
                if (input_counter.val == 1):
                    index.next = index + 1
                    buffer_to_write.next = data_in.val
                    text_block = self.w.find_withtag("block_text{}{}{}".format(num,data_used,int(index)))
                    self.w.itemconfig(text_block, text = "{}".format(int(data_in.val)))
                    
                elif ((input_counter.val > 1)):
                    index.next = index + 1
                    buffer_to_write.next = buffer_to_write + (data_in.val << index)
                    text_block = self.w.find_withtag("block_text{}{}{}".format(num,data_used,int(index)))
                    self.w.itemconfig(text_block, text = "{}".format(int(data_in.val)))
                    if (input_counter == len(data_buffer0)):
                        data_used.next = data_used+1
                    
            else:
                input_counter.next = 0
                index.next = 0
                #This is the first time the token in has gone down, so previous ASIC is done sending data
                if (d['prev_token_in'] == bool(1)):
                    self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 200, 
                      self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+80, 
                      text="Incoming token low edge!", fill = "red", anchor=W, tag = "asic{}_status_text".format(num))
                    self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 250, 
                          self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+100, 
                          text="Checking to see if we have data to send!", fill = "yellow", 
                          anchor=W, tag = "asic{}_status_text".format(num))
                    d['read_out'].next = bool(1)
                    token_out.next = bool(1)
                    index.next = 0
                else:
                    self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 200, 
                      self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+80, 
                      text="Incoming token is low!", fill = "red", anchor=W, tag = "asic{}_status_text".format(num))
                    
                #In the middle of reading out the data
                if (d['read_out'] == bool(1)):
                    self.w.itemconfig(data_out_line, fill="blue")
                    #There was never any data to send
                    if (data_used == 0):
                        token_out.next = bool(0)
                        d['read_out'].next = bool(0)
                        self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 250, 
                          self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+100, 
                          text="No data to send!", fill = "red", anchor=W, tag = "asic{}_status_text".format(num))
                    #Still data to read out
                    else:
                        #For the first clock cycle, just hold the token_out high, data starts on the second clock pulse
                        if (index.val == 0):
                            bit_to_send = all_buffers[0][index]
                            data_out.next = bit_to_send
                        else:
                            bit_to_send = all_buffers[0][index]
                            block = self.w.find_withtag("block{}{}{}".format(num,0,int(index-1)))
                            
                            self.w.itemconfig(block, outline="red")
                            #In the middle of sending out a buffer
                            if (index < len(data_buffer0) + 1):
                                self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 200, 
                                  self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+100, 
                                  text="Sending out buffer {}, bit {}, which is {}".format(0,index-1, int(data_out.val)), fill = "red", 
                                  anchor=W, tag = "asic{}_status_text".format(num))
                            
                            data_out.next = bit_to_send
                        
                        #Finished sending out a full buffer
                        if (index.val  > (len(data_buffer0))):
                            index.next = 0
                            d['read_out'].next = bool(0)
                            
                            for i in range(len(data_buffer0)):
                                text_block = self.w.find_withtag("block_text{}{}{}".format(num,0,i))
                                self.w.itemconfig(text_block, text = "X")
                                
                            self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 250, 
                              self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+100, 
                              text="Done sending out data!", fill = "red", anchor=W, tag = "asic{}_status_text".format(num))
                            
                            for i in range(len(data_buffer0)):
                                block = self.w.find_withtag("block{}{}{}".format(num,0,i))
                                self.w.itemconfig(block, outline="black")
                                
                            #This means that there was data in the deeper buffers
                            if (data_used > 1):
                                for i in range(data_used - 1):
                                    all_buffers[i] = all_buffers[i+1]
                                    all_buffers[i+1] = Signal(intbv(0)[8:])
                                    for j in range(len(data_buffer0)):
                                        text_block = self.w.find_withtag("block_text{}{}{}".format(num,i+1,j))
                                        self.w.itemconfig(text_block, text = "X")
                                        
                                    for j in range(len(data_buffer0)):
                                        text_block = self.w.find_withtag("block_text{}{}{}".format(num,i,j))
                                        self.w.itemconfig(text_block, text = "{}".format(int(all_buffers[i][j])))
                                    
                                    
                                    
                            data_used.next = data_used-1
                                
                        elif (index.val == (len(data_buffer0))):
                            token_out.next = bool(0)
                            index.next = index + 1
                            
                        else:
                            index.next = index + 1
                else:
                    self.w.itemconfig(data_out_line, fill="black")
                    
            #Just GUI stuff
            if (token_out == bool(1)):
                self.w.itemconfig(token_out_line, fill="green")
                self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 200, 
                      self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+45, 
                      text="Token out is high!", fill = "dark green", anchor=W, tag = "asic{}_status_text".format(num))
            else:
                self.w.itemconfig(token_out_line, fill="red")
                self.w.create_text((self.params['serial_signals'] * self.params['per_signal']) + 200, 
                      self.params['FPGA_height'] + ((num+1) * self.params['buffer_y']) + (num * self.params['size'][1])+55, 
                      text="Token out is low!", fill = "red", anchor=W, tag = "asic{}_status_text".format(num))
                
            d['prev_token_in'].next = token_in
            
        
        #every block must be returned
        return do_things