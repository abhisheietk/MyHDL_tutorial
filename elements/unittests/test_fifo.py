#test bench for fifo
from unittest import TestCase
import unittest
from myhdl import *
import random
from random import randrange
import fifo
import numpy as np

ADDR = 4
DATA = 8
LOWER=4               #lower limit for FIFO read
UPPER=(2**ADDR)-4     #upper limit for FIFO write
OFFSET = 2**(ADDR-1)

class Testfifo(TestCase):
    
    #Creating buffer (random data)
    def createbuff(self, DATA, ADDR):
        return [Signal(modbv(randrange(2**DATA))) for i in range(2**ADDR)]

    #A function for differest tests of fifo (minimising the code in case of different instances)
    @block
    def fifotester(self, din, we, inbusy, inclk, rd, rdout, outbusy, dout, outclk, hfull, rst,
                   DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET):

        #Clock driver for input
        @always(delay(5))
        def inclkgen(): 
            inclk.next = not inclk

        #Clock driver for output
        @always(delay(7))
        def outclkgen(): 
            outclk.next = not outclk

        fifobuff =[]
        fifobuff =self.createbuff(DATA, 4*ADDR)      #4**ADDR is used to give ample amount of din to test 'inbusy'

        #Driver for reset signal
        @instance
        def stimulus():
            yield delay(15)
            rst.next = 1
            yield delay(10)
            rst.next = 0
            yield delay(10)

        #Write driver for fifo    
        @instance
        def write():
            we.next = 0
            yield delay(50)
            i = 0
            while 1:
                yield inclk.posedge
                if not inbusy and np.random.choice(2):     #For random switching of 'we'
                    we.next = 1
                    din.next = fifobuff[i]
                    i +=1
                else:
                    we.next = 0
                    din.next = 0
                if i == len(fifobuff):
                    break
            yield inclk.posedge
            we.next = 0

        #Read driver for fifo
        @instance
        def read():
            rd.next = 0
            yield outclk.posedge
            while(hfull==0):
                yield outclk.posedge
                pass
            yield outclk.posedge
            i = 0
            while(1):
                yield outclk.posedge
                if hfull and not outbusy and np.random.choice(2):
                    rd.next = 1
                else:
                    rd.next = 0                   
                if rdout:
                    #print(dout, fifobuff[i])
                    self.assertEqual(dout, fifobuff[i])
                    i +=1;
                if i == len(fifobuff):
                    break

            yield outclk.posedge
            rd.next = 0


        return instances()

    '''#A test for fifo with separate variables
    def testReadWrite(self):   
        
        @block
        def test_fifo():
                     
            din, dout = [Signal(modbv(0)[DATA:]) for i in range(2)]
            rst = ResetSignal(0, active=1, async=False)    
            inclk, outclk,we, rd, inbusy, outbusy, hfull, rdout = [Signal(bool(0)) for i in range(8)]
            fifo_inst = fifo.fifo(din, we, inbusy, inclk, rd, rdout, outbusy, dout, outclk, hfull, rst,
                                  DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
            fifotester_inst = self.fifotester(din, we, inbusy, inclk, rd, rdout, outbusy, dout, outclk, hfull, rst,
                                              DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
                    
            return instances()
            
        tb = test_fifo()
        tb.config_sim(trace= True)
        tb.run_sim(duration=4000)
        tb.quit_sim()'''
    
    #A test for fifo with class variables
    def testReadWriteFifoWithBus(self):
        
        @block
        def test_fifo_with_bus():
                     
            aBus = fifo.bus(DATA = DATA, ADDR =ADDR)
            
            rst = ResetSignal(0, active=1, async=False)    
            inclk, outclk = [Signal(bool(0)) for i in range(2)]
            
            fifo_inst = fifo.fifo_with_bus(aBus, inclk, outclk, rst,
                                           DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
            fifotester_inst = self.fifotester(aBus.din, aBus.we, aBus.inbusy, inclk,
                                              aBus.rd, aBus.rdout, aBus.outbusy, aBus.dout, outclk, aBus.hfull, rst,
                                              DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
                              
            return instances()
            
        tb = test_fifo_with_bus()
        tb.config_sim(trace= True)
        tb.run_sim(duration=4000)
        tb.quit_sim()
        
if __name__ == '__main__':
    unittest.main()