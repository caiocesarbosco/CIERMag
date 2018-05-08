import RPi.GPIO as gpio
import spidev
import time

###############Lista de Comandos para o MCP23S17#######################
###########-------Dúvidas olhar o Datasheet------######################

WRITE=0
READ=1
OFFSET_ADDR=64
IOCON=10
IODIRA=0
IODIRB=1
GPPUA=12
GPIOA=18
GPIOB=19

###################GPIOB bits access in Decimal##################################

GPIOB7 = 128
GPIOB6 = 64
GPIOB5 = 32
GPIOB4 = 16
GPIOB3 = 8
GPIOB2 = 4
GPIOB1 = 2
GPIOB0 = 1

RESET_PIN = 22
SPI_CLOCK = 50000

class tx():
    
    n_modules=0
    slot=0
    tx_gate_pair=0
    gain_LO=0.5
    LATA=0
    LATB=0
    
    def __init__(self,mod_num):
        self.tx_gate_pair=tx.n_modules%4
        self.slot=int(mod_num)
        tx.n_modules=tx.n_modules+1               

    def __del__(self):
        tx.n_modules=tx.n_modules-1 
        
    def update_gain(self,gain):
        if gain == '0.5 dB':
            self.gain_LO='0.5 dB'
        elif gain == '1.0 dB': 
            self.gain_LO='1 dB'
        elif gain == '2.0 dB': 
            self.gain_LO='2 dB'
        elif gain == '4.0 dB': 
            self.gain_LO='4 dB'
        elif gain == '8.0 dB': 
            self.gain_LO='8 dB'
        elif gain == '16.0 dB': 
            self.gain_LO='16 dB'
        elif gain == '31.5 dB': 
            self.gain_LO='31.5 dB'   
                                                                              
    def instances_to_webdict(self):
        vec_webdict= [{'name':'type','type':'Tx'},{'name':'slot','slot':self.slot},{'name':'gate_pair','gate_pair':self.tx_gate_pair},{'name':'gain','gain':self.gain_LO},{'name':'gain_type','gain_type':'list'}]
        return vec_webdict
    
    def clear_modules_count(self):
        tx.n_modules=0
    
    def reset_mcp23s17(self):
        self.spi = spidev.SpiDev()
        gpio.setmode(gpio.BOARD)
        gpio.setup(RESET_PIN, gpio.OUT)
        gpio.output(RESET_PIN,1)        
        gpio.output(RESET_PIN,0)#start reset
        gpio.output(RESET_PIN,1)#stop reset 
        
    def blink_led(self):
        time.sleep(1)        
        self.set_pins_latches(GPIOB,GPIOB7)       

    def enable_slot(self):
        #-------------------MCP23S17 Command -------------
        #    1º Byte     |    2º Byte     |     3º Byte
        #    Nº Slot     |     IOCON      |      Value
        #  40H + N_slot  |      0AH       |       08H
        #    Hardware Habilitado no Endereço Passado
        #--------------------------------------------------
        
        command_slot=OFFSET_ADDR+2*self.slot+WRITE
        frame=[command_slot,IOCON,8]
        self.spi.writebytes(frame)
            
    def port_direction(self,port_reg,direction):
        #-------------------MCP23S17 Command -------------
        #    1º Byte     |    2º Byte     |     3º Byte
        #    Nº Slot     |     IODIRX     |      Value
        #  40H + N_slot  |    port_reg    |   direction(0-255)  
        #    Seta Porta A ou Porta B como entrada ou saída 
        #--------------------------------------------------
        
        command_slot=OFFSET_ADDR+2*self.slot+WRITE
        frame=[command_slot,port_reg,direction]
        self.spi.writebytes(frame)        
        
    def set_pull_up(self,active_pull_up):
        #-------------------MCP23S17 Command -------------
        #    1º Byte     |    2º Byte     |     3º Byte
        #    Nº Slot     |     GPPUA      |      Value
        #  40H + N_slot  |      0CH       |   activate_pull_up(0-255)  
        #    Habilita/Desabilita Pull-up da Porta A
        #--------------------------------------------------
                
        command_slot=OFFSET_ADDR+2*self.slot+WRITE
        frame=[command_slot,GPPUA,active_pull_up]
        self.spi.writebytes(frame)
        
    def set_pins_latches(self,port_reg,value):
        #-------------------MCP23S17 Command -------------
        #    1º Byte     |    2º Byte     |     3º Byte
        #    Nº Slot     |     GPIOX      |      Value
        #  40H + N_slot  |    port_reg    |      value(0-255)  
        #    Seta Nível ALto/Baixo na Porta X
        #--------------------------------------------------
                
        command_slot=OFFSET_ADDR+2*self.slot+WRITE
        if port_reg == GPIOA:
            self.LATA=self.LATA|value
            value=self.LATA
        elif port_reg == GPIOB:
            self.LATB=self.LATB|value
            value=self.LATB
        frame=[command_slot,port_reg,value]
        self.spi.writebytes(frame)
        
    def clear_pins_latches(self,port_reg,value):
        #-------------------MCP23S17 Command -------------
        #    1º Byte     |    2º Byte     |     3º Byte
        #    Nº Slot     |     GPIOX      |      Value
        #  40H + N_slot  |    port_reg    |      value(0-255)  
        #    Seta Nível ALto/Baixo na Porta X
        #--------------------------------------------------

        command_slot=OFFSET_ADDR+2*self.slot+WRITE
        if port_reg == GPIOA:
            self.LATA=self.LATA & ~value
            value=self.LATA
        elif port_reg == GPIOB:
            self.LATB=self.LATB & ~value
            value=self.LATB
        frame=[command_slot,port_reg,value]
        self.spi.writebytes(frame)    
        
    def read_type_module(self,port_reg):
        #-------------------MCP23S17 Command -------------
        #    1º Byte     |    2º Byte     |     3º Byte
        #    Nº Slot     |     GPIOX      |      Value
        #  41H + N_slot  |    port_reg    |        0(read)  
        #           Lê Nível Lógico da Porta X
        #--------------------------------------------------         
         
        command_slot=OFFSET_ADDR+2*self.slot+READ
        frame=[command_slot,port_reg,0]
        rawdata = self.spi.xfer2(frame)
        read_module = rawdata[2]&3        
        return read_module
     
    def select_tx_gate_pair(self):
    
        if self.tx_gate_pair == 1:
            self.clear_pins_latches(GPIOB,GPIOB6)    
            self.clear_pins_latches(GPIOB,GPIOB5)
            
        elif self.tx_gate_pair == 2:
            self.set_pins_latches(GPIOB,GPIOB6)
            self.clear_pins_latches(GPIOB,GPIOB5)     
        
        elif self.tx_gate_pair == 3:
            self.set_pins_latches(GPIOB,GPIOB5)
            self.clear_pins_latches(GPIOB,GPIOB6)
                
        elif self.tx_gate_pair == 4:
            self.set_pins_latches(GPIOB,GPIOB6)
            self.set_pins_latches(GPIOB,GPIOB5)
    
    def select_gain(self):
        
        if self.gain_LO == '0.5 dB':
            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨|______XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low  
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW             
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication 
        elif self.gain_LO == '1.0 dB':
            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨|_|¨¨¨¨¨¨¨¨¨XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low   
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW                         
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH            
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
    
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication             

        elif self.gain_LO == '2.0 dB':
            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨|_|¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low  
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW                         
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH            
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication 
            
        elif self.gain_LO == '4.0 dB':

            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨¨¨¨¨¨¨¨¨¨¨¨¨|_|¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low  
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW             
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH            
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication 

        elif self.gain_LO == '8.0 dB':

            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨¨¨¨¨¨¨|_|¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low  
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW                         
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH            
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication             

        elif self.gain_LO == '16.0 dB':

            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨|_|¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low  
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW                         
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.set_pins_latches(GPIOB,GPIOB2)#DIN HIGH            
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication             

        elif self.gain_LO == '31.5 dB':

            #-------------------------SKY Command------------------------------
            #LE:  XXXX¨¨¨¨|____________________________________________|¨¨¨XXXXX
            #DIN: XXXXXXXXXX¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨|______XXXXXXXXXXXXXXX
            #bits:            D5    D4    D3    D2    D1    D0
            #SCLK:XXXXXXXXXXX_|¨|___|¨|___|¨|__|¨|___|¨|____|¨|___XXXXXXXXXXXXXX
            #
            #------------------------------------------------------------------

            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Start Low  
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High
            self.clear_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) Low -> Star Communication  
            
            #--------------- D5 ---------------------
            self.clear_pins_latches(GPIOB,GPIOB2)##DIN LOW             
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall  
            #--------------- D4 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D3 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D2 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall            
            #--------------- D1 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall 
            #--------------- D0 ---------------------
            self.set_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Rise  
            self.clear_pins_latches(GPIOB,GPIOB3)#SCLK (Clock) Fall                                        
            
            self.set_pins_latches(GPIOB,GPIOB1)#LE (Chip Select) High -> End Communication             
                
    def setup_module(self):
        self.spi = spidev.SpiDev()  
        self.spi.open(0,0)
        self.spi.max_speed_hz = SPI_CLOCK
        self.enable_slot()#Habilita em todos os módulos comandos endereçaveis
        self.port_direction(IODIRB,0)          
        self.port_direction(IODIRA,255)
        self.set_pull_up(255)
        type = self.read_type_module(GPIOA)
        
        if type == 1:
            self.blink_led()
            self.select_tx_gate_pair()
            self.select_gain()
            
        elif type ==2:
            self.spi.close()
            return 2
        
        else:
            self.spi.close()
            return 0
                     
        self.spi.close()
        return 1    
    
                
            
        
            
    

