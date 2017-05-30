from myhdl import *
import hdlcfg

DATA=8               #Size of Data bus
ADDR=4               #Size of address bus
LOWER=4              #Lower limit for FIFO read
UPPER=(2**ADDR)-4    #Upper limit for FIFO write
OFFSET = 2**(ADDR-1) #Limit for fifo read (condition for half full)

#Collection of variables in class
class bus:
    def __init__(self, DATA=8, ADDR=8):
        self.inbusy  = Signal(bool(0))
        self.we      = Signal(bool(0))
        self.din     = Signal(modbv(0)[DATA:])
        self.outbusy = Signal(bool(0))
        self.rd      = Signal(bool(0))
        self.dout    = Signal(modbv(0)[DATA:])
        self.rdout   = Signal(bool(0))
        self.hfull   = Signal(bool(0))

#Module with class-variables
@block
def fifo_with_bus(aBus, inclk, outclk, rst,
                 DATA= DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET):
    fifo_inst = fifo(aBus.din, aBus.we, aBus.inbusy, inclk,
                     aBus.rd, aBus.rdout, aBus.outbusy, aBus.dout, outclk, aBus.hfull, rst,
                     DATA= DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET)
    return instances()

#Module with separate variables (also a general function for fifo)
@block
def fifo(din, we, inbusy, inclk, rd, rdout, outbusy, dout, outclk, hfull, rst,
         DATA= DATA, ADDR=ADDR, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET):
    
    """ Half full FIFO model
    inclk  = Clock Input for write
    inbusy = Input bus is busy (overflow)
    we     = Input bus write enable
    din    = Input bus data input
    inclk  = Clock Input for read
    outbusy= Output bus is busy (underflow)
    rd     = Output bus read enable
    dout   = Output bus data output
    rdout  = Output bus data can be read
    hfull  = Buffer half full
    rst    = Reset
    ADDR   = Size of Address bus
    DATA   = Size of Data bus
    LOWER  = Size of lower limit for buffer after which buffer can be read
    UPPER  = Size of upper limit for buffer after which buffer can not be written
    OFFSET = Size of half full mark"""
    
    mem = [Signal(modbv(0)[DATA:]) for i in range(2**ADDR)]
    in_addr, out_addr  = [Signal(modbv(0)[ADDR+1:]) for i in range(2)]
    length = Signal(modbv(0)[ADDR+1:])
    inbusy_sig, outbusy_sig = [Signal(bool(0)) for i in range(2)]   #...._sig are used to avoid error in '.v' file, O/P port is read internally
    
    #Create separate def for write driver, since 'rst' in mem erases every memory and uses separate registers in kit, while we'll use given Ram module
    @always(inclk.posedge)
    def writemem():
        if we:
            mem[in_addr[ADDR:]].next = din
                    
    @always_seq(inclk.posedge, reset = rst)
    def write():
        if we:
            in_addr.next = in_addr + modbv(1)[ADDR+1:]
            
    @always_seq(outclk.posedge, reset = rst)
    def read():
        if rd & (not outbusy_sig):
            dout.next = mem[out_addr[ADDR:]]
            out_addr.next =  out_addr + modbv(1)[ADDR+1:]
        rdout.next = rd and not outbusy_sig
        length.next = in_addr - out_addr
                    
    @always_comb
    def outputlogic():
        inbusy.next = inbusy_sig
        outbusy.next = outbusy_sig
    
    #Setting up different flags
    @always_comb
    def busy():
        if length >= UPPER:
            inbusy_sig.next = bool(1)
            outbusy_sig.next = bool(0)
        elif length <= LOWER:
            outbusy_sig.next = bool(1)
            inbusy_sig.next = bool(0)
        else:
            inbusy_sig.next = bool(0)
            outbusy_sig.next = bool(0)
        
        if length >= OFFSET:
            hfull.next = 1
        else:
            hfull.next = 0
        
    return instances()


# Define VHDL Conversion function
def fifo_convert(DATA=8, ADDR=4):
    din, dout          = [Signal(modbv(0)[DATA:]) for i in range(2)]
    in_addr, out_addr  = [Signal(modbv(0)[ADDR+1:]) for i in range(2)]
    DATA               = 8
    ADDR               = 4
    UPPER              = 2**ADDR
    LOWER              = 0    
    rst = ResetSignal(0, active=1, async=False)
    inclk, outclk,we, rd, inbusy, outbusy, hfull, rdout = [Signal(bool(0)) for i in range(8)]    
    
    fifo_inst = fifo(din, we, inbusy, inclk, rd, rdout, outbusy, dout, outclk, hfull, rst,
                     OFFSET=OFFSET, DATA = DATA, ADDR =ADDR, UPPER =UPPER,LOWER =LOWER)
    fifo_inst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path,
                     name='fifo_' + str(ADDR)+'_'+ str(DATA))
    
if __name__ == '__main__':
    fifo_convert(DATA=8, ADDR=4)