from myhdl import *
from pyhdllib import hdlcfg
from pyhdllib import lane
from pyhdllib import varfifo


ADDR = 4
DATA = 8
WORD = 4
LOWER=4               #lower limit for lane read
UPPER=(2**ADDR)-4     #upper limit for lane write
OFFSET = 2**(ADDR-1)

@block
def varlane(aBus, bBus, inclk, outclk, rst, DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET):
    
    varfifo_inst1 = varfifo.one2many(inclk, aBus.inbusy, aBus.we, aBus.din,
                                     outclk, bBus.outbusy, bBus.rd, bBus.dout, bBus.rdout, bBus.hfull, rst,
                                     DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
    varfifo_inst2 = varfifo.many2one(inclk, bBus.inbusy, bBus.we, bBus.din,
                                     outclk, aBus.outbusy, aBus.rd, aBus.dout, aBus.rdout, aBus.hfull, rst,
                                     DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
    return instances()