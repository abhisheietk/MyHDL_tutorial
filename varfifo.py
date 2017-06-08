from myhdl import *
from pyhdllib import hdlcfg
from pyhdllib import fifo
from pyhdllib import demux
from pyhdllib import mux
import math

ADDR = 4
DATA = 8
WORD = 4
LOWER=4               #lower limit for fifo read
UPPER=(2**ADDR)-4     #upper limit for fifo write
OFFSET = 2**(ADDR-1)

@block
def one2many(inclk, inbusy, we, din,
             outclk, outbusy, rd, dout, rdout, hfull, rst,
             DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET):
    
    count = Signal(modbv(0)[math.log(WORD,2):])
    we_t = [Signal(modbv(0)) for i in range(WORD)] #[Signal(bool(0)) for i in range(WORD)]
    rd_t = Signal(bool(0))
    rdout_t = [Signal(bool(0)) for i in range(WORD)]
    dout_t   = [Signal(modbv(0)[DATA:]) for i in range(WORD)]
    outbusy_t = [Signal(bool(0)) for i in range(WORD)]
    inbusy_t = [Signal(bool(0)) for i in range(WORD)]
    hfull_t = [Signal(bool(0)) for i in range(WORD)]
    
    demux_t = demux.demux(we, we_t, count, BITS = WORD)
    fifo_inst = [fifo.fifo(din, we_t[i], inbusy_t[i], inclk,
                           rd_t, rdout_t[i], outbusy_t[i], dout_t[i], outclk, hfull_t[i], rst, 
                           DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET) for i in range(WORD)]
    
    p = [dout_t[i](j) for i in range(WORD) for j in reversed(range(DATA))]
    q = ConcatSignal(*p)
    
    @always_comb
    def logic():
        inbusy.next = inbusy_t[WORD-1]
        outbusy.next = outbusy_t[WORD-1]
        hfull.next = hfull_t[WORD-1]
        rdout.next = rdout_t[WORD-1]
        rd_t.next = rd
        dout.next = q
     
    @always_seq(inclk.posedge, reset=rst)
    def write_logic():
        if we:
            count.next = count + modbv(1)
    return instances()

@block
def many2one(inclk, inbusy, we, din,
             outclk, outbusy, rd, dout, rdout, hfull, rst,
             DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET):
    
    count_rd = Signal(modbv(0)[math.log(WORD,2):])
    count_rdout = Signal(modbv(0)[math.log(WORD,2):])
    we_t = [Signal(bool(0)) for i in range(WORD)]
    rd_t = [Signal(bool(0)) for i in range(WORD)]
    rdout_t = [Signal(bool(0)) for i in range(WORD)]
    outbusy_t = [Signal(bool(0)) for i in range(WORD)]
    inbusy_t = [Signal(bool(0)) for i in range(WORD)]
    hfull_t = [Signal(bool(0)) for i in range(WORD)]
    dout_t = [Signal(modbv(0)[DATA:]) for i in range(WORD)]
    din_t = [din(DATA*(i+1),DATA*(i)) for i in reversed(range(WORD))]
    
    demux_t = demux.demux(rd, rd_t, count_rd,  BITS = WORD)
    rdout_mux_t = mux.mux(rdout, rdout_t, count_rdout)
    fifo_inst = [fifo.fifo(din_t[i], we, inbusy_t[i], inclk,
                           rd_t[i], rdout_t[i], outbusy_t[i], dout, outclk, hfull_t[i], rst, 
                           DATA = DATA, ADDR =ADDR, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET) for i in range(WORD)]
                           
    @always_comb
    def logic():
        inbusy.next = inbusy_t[WORD-1]
        outbusy.next = outbusy_t[WORD-1]
        hfull.next = hfull_t[WORD-1]
        
    @always_seq(outclk.posedge, reset=rst)
    def read_logic():
        if rd:
            count_rd.next = count_rd + modbv(1)
        if rdout:
            count_rdout.next = count_rdout + modbv(1)
            #print(count,rdout_t)
                      
    return instances()
    
# Define VHDL Conversion function
def varfifo_convert(DATA=DATA, ADDR=ADDR, WORD=WORD, UPPER=UPPER, LOWER=LOWER, OFFSET=OFFSET):
    rst = ResetSignal(0, active=1, async=False)    
    inclk, outclk = [Signal(bool(0)) for i in range(2)]    
    inbusy, we, outbusy, rd, rdout, hfull = [Signal(bool(0)) for i in range(6)]
    din  = Signal(modbv(0)[DATA:])
    dout = Signal(modbv(0)[DATA:])
    
    one2many_inst = one2many(inclk, inbusy, we, din,
                             outclk, outbusy, rd, dout, rdout, hfull, rst,
                             DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)

    one2many_inst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path,
                          name='one2many_' + str(DATA)+'_'+ str(ADDR)+'_'+ str(WORD)+'_'+ str(UPPER)+'_'+ str(LOWER)+'_'+ str(OFFSET))
    
    many2one_inst = many2one(inclk, inbusy, we, din,
                             outclk, outbusy, rd, dout, rdout, hfull, rst,
                             DATA = DATA, ADDR =ADDR, WORD=WORD, UPPER =UPPER, LOWER =LOWER, OFFSET=OFFSET)
    
    many2one_inst.convert(hdl='Verilog', header=hdlcfg.header, directory=hdlcfg.hdl_path,
                          name='many2one_' + str(DATA)+'_'+ str(ADDR)+'_'+ str(WORD)+'_'+ str(UPPER)+'_'+ str(LOWER)+'_'+ str(OFFSET))
    
    insig = Signal(bool(0))
    outsig = Signal(modbv(0)[WORD:])
    sel = Signal(modbv(0)[math.log(WORD, 2):])
    
if __name__ == '__main__':
    varfifo_convert(DATA=8, ADDR=4, WORD =4, UPPER=(2**ADDR)-4, LOWER=4, OFFSET=2**(ADDR-1))