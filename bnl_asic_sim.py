# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 15:51:50 2019

@author: Eraguzin
This is the top level module for the entire digital simulation.  It sets up the GUI and calls the simulation
"""
import Tkinter as tk
import imageio
from simulation import Simulation_Functions
import os, re
    
class GUI_WINDOW(tk.Frame):
    def __init__(self, master=None):
        
        self.params = dict(
            #Rectangles are top left x and y, and then bottom right x and y
            FPGA_width = 1000,
            FPGA_height = 100
            )

        self.params['canvas_x'] = 1000
        self.params['canvas_y'] = 900
        
        self.params['num_asics'] = 4
        
        self.params['common_signals'] = 1
        self.params['serial_signals'] = 1
        self.params['daisy_signals'] = 1
        
        self.params['buffer_x'] = 500
        self.params['buffer_y'] = 50
        
        self.params['block_size'] = 20
        
        self.params['FPGA_dims'] = [0, 0, self.params['FPGA_width'], self.params['FPGA_height']]
        
        #Create the simulator
        self.sim = Simulation_Functions()
        #Give the simulator the gui objects so it can manipulate them (change colors)
        self.sim.gui = self.set_up_gui(master)
        self.sim.master = master
        
        self.sim.params = self.params
        
    def set_up_gui(self, master):
        #It's calling the constructor of the parent tkinter object, the pack method of the class, which is now a tkinter object
        frame = tk.Frame.__init__(self,master)
        self.pack()

        #Finish/reset button
        finish_button = tk.Button(self, text="Start Simulation",command=self.simulation,width=25)
        finish_button.grid(row=0,column=0,columnspan=1)
        hbar=tk.Scrollbar(frame,orient=tk.HORIZONTAL)
        vbar=tk.Scrollbar(frame,orient=tk.VERTICAL)
        w = tk.Canvas(width=self.params['canvas_x'], height=self.params['canvas_y'], bg = "white", scrollregion=(0,0,2000,2000),
                      yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        
        hbar.pack(side=tk.BOTTOM,fill=tk.X)
        hbar.config(command=w.xview)
        
        vbar.pack(side=tk.RIGHT,fill=tk.Y)
        vbar.config(command=w.yview)
        
        
        w.pack()
        
        w.create_rectangle(self.params['FPGA_dims'], fill="yellow")
        #X and then Y coordinates
        w.create_text((self.params['FPGA_dims'][2] - self.params['FPGA_dims'][0])/2, 
                      (self.params['FPGA_dims'][3] - self.params['FPGA_dims'][1])/2, text="FPGA")
        
        size = self.determine_asic_size()
        self.params['size'] = size
        
        signals_to_pass = self.params['common_signals'] + self.params['daisy_signals']
        
        w.create_line(700,150,700,850,width = 2)
        w.create_line(800,150,800,850,width = 2)
        w.create_line(900,150,900,850,width = 2)
        
        w.create_text(850,130, text="How far light is from creating another peak in the ASIC", anchor=tk.CENTER)
        w.create_text(700,870, text="0 ns", anchor=tk.CENTER)
        w.create_text(800,870, text="500 ns", anchor=tk.CENTER)
        w.create_text(900,870, text="1000 ns", anchor=tk.CENTER)
        
        w.create_line(950,200,1000,200,width = 2, arrow=tk.FIRST, tag = "ASIC0_line", fill = "red")
        w.create_line(950,400,1000,400,width = 2, arrow=tk.FIRST, tag = "ASIC1_line", fill = "red")
        w.create_line(950,600,1000,600,width = 2, arrow=tk.FIRST, tag = "ASIC2_line", fill = "red")
        w.create_line(950,800,1000,800,width = 2, arrow=tk.FIRST, tag = "ASIC3_line", fill = "red")
        
        
        for count, i in enumerate(range(self.params['num_asics'])):
            #Create ASICs
            w.create_rectangle((self.params['serial_signals'] * self.params['per_signal']),
                               self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]),
                               (self.params['serial_signals'] * self.params['per_signal']) + size[0],
                               self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + ((i + 1) * size[1]),
                               fill="light blue", tags=("asic{}".format(i)))
            
            w.create_text((self.params['serial_signals'] * self.params['per_signal']), 
                      self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]), text="ASIC {}".format(i), anchor=tk.SW)
            #Create common signals
            for j in range(signals_to_pass):
                w.create_line((self.params['serial_signals'] * self.params['per_signal']) + ((j + 0.5) * self.params['per_signal']),
                              self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]),
                              (self.params['serial_signals'] * self.params['per_signal']) + ((j + 0.5) * self.params['per_signal']),
                              self.params['FPGA_height'] + ((i) * self.params['buffer_y']) + (i * size[1]),
                              tags=("chip{}".format(i), "common{}".format(j)), width = 5)
                
            #Create horizontal line for serial signals
            y_spacing = size[1]/self.params['serial_signals']
            for j in range(self.params['serial_signals']):
                w.create_line((self.params['serial_signals'] * self.params['per_signal']),
                              self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]) + ((j + 0.5) * y_spacing),
                              (self.params['serial_signals'] * self.params['per_signal']) - ((j+0.5) * self.params['per_signal']),
                              self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]) + ((j + 0.5) * y_spacing),
                              tags=("chip{}".format(i), "serial{}".format(j)), width = 5)

            if (count > (self.params['num_asics'] - 2)):
                #Create vertical line for serial signals
                for j in range(self.params['serial_signals']):
                    w.create_line((self.params['serial_signals'] * self.params['per_signal']) - ((j+0.5) * self.params['per_signal']),
                                  self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]) + ((j + 0.5) * y_spacing),
                                  (self.params['serial_signals'] * self.params['per_signal']) - ((j+0.5) * self.params['per_signal']),
                                  self.params['FPGA_height'],
                                  tags=("serial{}".format(j)), width = 5)
                
                #Create daisy chained signals
                y_spacing = size[1]/self.params['daisy_signals']
                for j in range(self.params['daisy_signals']):
                    #horizontal line
                    w.create_line((self.params['serial_signals'] * self.params['per_signal']) + size[0],
                                  self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]) + ((j + 0.5) * y_spacing),
                                  (self.params['serial_signals'] * self.params['per_signal']) + size[0] + ((j+0.5) * self.params['per_signal']),
                                  self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]) + ((j + 0.5) * y_spacing),
                                  tags=("chip{}".format(i), "daisy{}".format(j)), width = 5)
                    
                    #vertical line
                    w.create_line((self.params['serial_signals'] * self.params['per_signal']) + size[0] + ((j+0.5) * self.params['per_signal']),
                                  self.params['FPGA_height'] + ((i+1) * self.params['buffer_y']) + (i * size[1]) + ((j + 0.5) * y_spacing),
                                  (self.params['serial_signals'] * self.params['per_signal']) + size[0] + ((j+0.5) * self.params['per_signal']),
                                  self.params['FPGA_height'],
                                  tags=("chip{}".format(i), "daisy{}".format(j)), width = 5)
        return w
        
    def example_of_changing_color(self,w):
        print(w.find_withtag("serial1"))
        lines = (w.find_withtag("serial1"))
        for i in lines:
            w.itemconfig(i, fill="blue")
        
    def determine_asic_size(self):
        available_x = self.params['canvas_x']
        total_signal_lines = self.params['common_signals'] + self.params['serial_signals'] + (2 * self.params['daisy_signals'])
        self.params['per_signal'] = (available_x - self.params['buffer_x']) / (total_signal_lines - 1)
        available_y = self.params['canvas_y'] - self.params['FPGA_height'] - self.params['buffer_y']
        y_per_asic = available_y / self.params['num_asics']
        y_for_block = y_per_asic - self.params['buffer_y']
        x_for_block = self.params['per_signal'] * (self.params['common_signals'] + self.params['daisy_signals'])
        return x_for_block, y_for_block
        
    
    def simulation(self):
        self.sim.simulation()
        
        images = []
        directory = os.path.join(os.getcwd(), "Simulation_Output")
        filenames = os.listdir(directory)
        ordered_files = sorted(filenames, key=lambda x: (int(re.sub('\D','',x)),x))
        print(directory)
        for filename in ordered_files:
            filename_to_use = os.path.join(directory, filename )
            print(filename_to_use)
            images.append(imageio.imread(filename_to_use))
            
        for speed in [0.05, 0.1, 0.5]:
            imageio.mimsave('Simulation{}.gif'.format(speed), images, 'GIF', duration = speed, loop = 0)
            
        print("DONE")

        
def main():
    root = tk.Tk()
    root.geometry("1500x1000") #You want the size of the app to be 500x500
#    root.resizable(0, 0) #Don't allow resizing in the x or y direction
    root.title("Quad FE ASIC Test GUI")
    GUI_WINDOW(root)
    root.mainloop()
    


if __name__ == "__main__":
    main()
