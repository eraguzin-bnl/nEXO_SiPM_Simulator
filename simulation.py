# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 17:24:10 2019

@author: Eraguzin
"""
from myhdl import block, Signal, intbv
from behavior import the_blocks
#all times are in nanoseconds
class Simulation_Functions():
    def __init__(self):
        self.to_plot = True
        #Import the hardware blocks
        self.block = the_blocks()
    def simulation(self):
        #If this is called, a simulation has been requested
        @block
        def prepare():
            #Serial signals
            clk = Signal(bool(0))
            #token = [Signal(bool(0))] * (self.num_asics + 1)
            token0 = Signal(bool(0))
            token1 = Signal(bool(0))
            token2 = Signal(bool(0))
            token3 = Signal(bool(0))
            token4 = Signal(bool(0))
            data = [Signal(bool(0))] * (self.params['num_asics'] + 1)
            
            asic0_input = Signal(intbv(0)[8:])
            asic1_input = Signal(intbv(0)[8:])
            asic2_input = Signal(intbv(0)[8:])
            asic3_input = Signal(intbv(0)[8:])
            
            
            #Pass along the GUI
            self.block.w = self.gui
            self.block.master = self.master
            
            self.block.params = self.params
            
            x=self.gui.winfo_rootx()
            y=self.gui.winfo_rooty()
            x1=x+self.gui.winfo_width()
            y1=y+self.gui.winfo_height()
            self.block.box=(x,y,x1,y1)
            
            if (self.to_plot):
                the_plotter = self.block.plotter(clk)
            else:
                the_plotter = self.block.blank_plotter(clk)
            
            #Instantiate all blocks
            the_FPGA = self.block.FPGA(clk = clk, token_in = token0, 
                                       token_out = token4, data_in = data[0])
            asic0 = self.block.ASIC(clk = clk, token_out = token0, token_in = token1,
                                                  data_out = data[0], data_in = data[1], num = 0, data_input = asic0_input)
            asic1 = self.block.ASIC(clk = clk, token_out = token1, token_in = token2,
                                                  data_out = data[1], data_in = data[2], num = 1, data_input = asic1_input)
            asic2 = self.block.ASIC(clk = clk, token_out = token2, token_in = token3,
                                                  data_out = data[2], data_in = data[3], num = 2, data_input = asic2_input)
            asic3 = self.block.ASIC(clk = clk, token_out = token3, token_in = token4,
                                                  data_out = data[3], data_in = data[4], num = 3, data_input = asic3_input)
            
            light = self.block.light_deposit(clk = clk, data0 = asic0_input, 
                                             data1 = asic1_input, data2 = asic2_input, data3 = asic3_input)
#            asic_tuple = []
#            for i in range(self.num_asics):
#                asic_tuple.append(self.block.ASIC(clk = clk, token_out = token[i], token_in = token[i+1],
#                                                  data_out = data[i], data_in = data[i+1], num = i))
            
            #Necessary to run everything
            return the_FPGA, asic0, asic1, asic2, asic3, the_plotter, light
        
        #Prepares the simulation and runs it
        inst = prepare()
        inst.run_sim(2500)