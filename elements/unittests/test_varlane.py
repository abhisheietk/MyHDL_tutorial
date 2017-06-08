#test bench for fifo
from unittest import TestCase
import unittest
from myhdl import *
import random
from random import randrange
from pyhdllib.unittests import test_fifo
from pyhdllib import lane
from pyhdllib import fifo
import numpy as np

ADDR = 4
DATA = 8
WORD = 4
LOWER=4               #lower limit for FIFO read
UPPER=(2**ADDR)-4     #upper limit for FIFO write
OFFSET = 2**(ADDR-1)

class Testlane(TestCase):
    Testfifo = test_fifo.Testfifo()
    
    def testlane(self):
        @block
        def test_Lane():
            
            rst = ResetSignal(0, active=1, async=False)    
            inclk, outclk = [Signal(bool(0)) for i in range(2)]
            
            clock0_inst = self.Testfifo.clock(inclk, DELAY=5)
            clock1_inst = self.Testfifo.clock(outclk, DELAY=7)
            
            aBus = fifo.bus(DATA = DATA, ADDR =ADDR)
            bBus = fifo.bus(DATA = DATA*WORD, ADDR =ADDR)
            
            lane_inst = lane.lane(aBus, bBus, inclk, outclk, rst, DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
            loopBack_inst = lane.loopBack(bBus)
            
            fifotester_inst = self.Testfifo.fifotester(aBus.din, aBus.we, aBus.inbusy, inclk,
                                                       aBus.rd, aBus.rdout, aBus.outbusy, aBus.dout,
                                                       inclk, aBus.hfull, rst,
                                                       DATA = DATA, ADDR =ADDR, UPPER =UPPER,
                                                       LOWER =LOWER, OFFSET=OFFSET, PRINTLOG=False)

            return instances()

        tb = test_Lane()
        tb.config_sim(trace= True)
        tb.run_sim(duration=4000)
        tb.quit_sim()
        
if __name__ == '__main__':
    unittest.main()