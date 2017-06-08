#test bench for fifo
from unittest import TestCase
import unittest
from myhdl import *
import random
from random import randrange
from pyhdllib.unittests import test_fifo
from pyhdllib import varfifo
from pyhdllib import fifo
import numpy as np

ADDR = 4
DATA = 8
WORD = 4
LOWER=4               #lower limit for FIFO read
UPPER=(2**ADDR)-4     #upper limit for FIFO write
OFFSET = 2**(ADDR-1)

class Testvarfifo(TestCase):
    Testfifo = test_fifo.Testfifo()
    
    def testvarfifo(self):
        '''Testing one2many logic'''
        
        @block
        def test_varfifo():
            
            rst = ResetSignal(0, active=1, async=False)    
            inclk, outclk = [Signal(bool(0)) for i in range(2)]
            clock0_inst = self.Testfifo.clock(inclk, DELAY=5)
            clock1_inst = self.Testfifo.clock(outclk, DELAY=7)
            inbusy, we, outbusy, rd, rdout, hfull = [Signal(bool(0)) for i in range(6)]
            din  = Signal(modbv(0)[DATA:])
            dout = Signal(modbv(0)[DATA:])            
            aBus = fifo.bus(DATA = DATA*WORD, ADDR =ADDR)
            
            one2many_inst = varfifo.one2many(inclk, inbusy, we, din,
                                             outclk, aBus.outbusy, aBus.rd, aBus.dout, aBus.rdout, aBus.hfull, rst,
                                             DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
            
            many2one_inst = varfifo.many2one(outclk, aBus.inbusy, aBus.we, aBus.din,
                                             inclk, outbusy, rd, dout, rdout, hfull, rst,
                                             DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
            
            connector_inst = fifo.connector(aBus.din, aBus.we, aBus.inbusy, aBus.rd, aBus.rdout, aBus.outbusy, aBus.dout, aBus.hfull)
            
            fifotester_inst = self.Testfifo.fifotester(din, we, inbusy, inclk,
                                                       rd, rdout, outbusy, dout,
                                                       inclk, hfull, rst,
                                                       DATA = DATA, ADDR =ADDR, UPPER =UPPER, 
                                                       LOWER =LOWER, OFFSET=OFFSET, PRINTLOG=True)

            return instances()
        
        tb = test_varfifo()
        tb.config_sim(trace= True)
        tb.run_sim(duration=4000)
        tb.quit_sim()
        

if __name__ == '__main__':
    unittest.main()
