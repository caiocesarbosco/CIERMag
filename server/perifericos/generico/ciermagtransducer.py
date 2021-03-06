# -*- coding: utf-8 -*-
""" GPIO

Setting the GPIO pins to work as address selection for SPI communication to
increase the number of devices to be connected.

+--------+-----+-------+-------+--------+-------+---------+-------+-------+-------+-------+-------+-------+-------+
|Function| +5V |  +5V  |  GND  |GPIO 14 |GPIO 15| GPIO 18 |  GND  |GPIO 23|GPIO 24|  GND  |GPIO 25|GPIO 08|GPIO 07|
|        |     |       |       | (TXD)  | (RXD) |(PCM_CLK)|       |       |       |       |       | (CE0) | (CE1) |
+--------+-----+-------+-------+--------+-------+---------+-------+-------+-------+-------+-------+-------+-------+
|  PIN   | P02 |  P04  |  P06  |  P08   |  P10  |   P12   |  P14  |  P16  |  P18  |  P20  |  P22  |  P24  |  P26  |
+--------+-----+-------+-------+--------+-------+---------+-------+-------+-------+-------+-------+-------+-------+
|  PIN   | P01 |  P03  |  P05  |  P07   |  P09  |   P11   |  P13  |  P15  |  P17  |  P19  |  P21  |  P23  |  P25  |
+--------+-----+-------+-------+--------+-------+---------+-------+-------+-------+-------+-------+-------+-------+
|        |     |(SDA)  | (SCL) |(GPCLK0)|       |         |       |       |       |(MOSI) |(MISO) |(SCLK) |       |
|Function|+3V3 |GPIO 02|GPIO 03|GPIO 04 |  GND  | GPIO 17 |GPIO 27|GPIO 22| +3V3  |GPIO 10|GPIO 09|GPIO 11|  GND  |
+--------+-----+-------+-------+--------+-------+---------+-------+-------+-------+-------+-------+-------+-------+
Since SPI uses GPIO 08, 07, 09, 10 and 11, there is still left 12 GPIO unused.
The usage order follows: GPIO (Pin) 25(22), 24(18), 23(16), 22(15), 27(13),
17(11), 18(12), 04(07), 14(08), 15(10), 02(03), 03(05)
"""

import spidev
import RPi.GPIO as gpio
import time
import copy
from shimming import convert_bit_voltage
import serverfunctions as sf
import parameterlib as pl
import serverconfig as sc

RESET_ADDRESS = 0
gpio.setwarnings(False)


class Register(object):

    def __init__(self, name, regdict):
        self.name = name

        for key in regdict:
            attrname = key.replace(' ', '_')
            attrname = attrname.lower()
            setattr(self, attrname, regdict[key])
    


class Transducer(object):
    
    pins = [22,12]
    RESET_ADDRESS = 0

    def __init__(self, tedsdict, gpiopinsinuse=2):
        self.registers = {}
        self.gpiopinsinuse = gpiopinsinuse

        # Set transducer attributes with the TEDS data
        for key in tedsdict:

            if type(tedsdict[key]) != type({}):
                attrname = key.replace(' ', '_')
                attrname = attrname.replace('/', '_')
                attrname = attrname.lower()
                setattr(self, attrname, tedsdict[key])
            else:
                # Create a Register
                self.registers[key] = Register(key, tedsdict[key])


        # Continue to initialize the Transducer with the loaded TEDS
        self.init_spi()
        self.set_pinuse(gpiopinsinuse)
        self.init_gpio()
        #self.set_addr(RESET_ADDRESS)
        self.setup_transducer()
        

    def init_spi(self):
        self.spi = spidev.SpiDev()

    def set_pinuse(self, gpiopinsinuse):
        if gpiopinsinuse > len(self.pins):
            self.pinused = self.pins[0:gpiopinsinuse]
        else:
            self.pinused = self.pins

    def init_gpio(self):
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.pinused, gpio.OUT)
        gpio.output(self.pinused[0],1)
        gpio.output(self.pinused[1],1)
        

    def set_addr(self, addr):
        i = 0
        while i < self.gpiopinsinuse:
            gpio.output(self.pinused[i], addr >> i & 1)
            i += 1

    def start_spi_comm(self):
        #self.set_addr(self.spi_address)
        self.spi.open(0,self.spi_select)
        self.spi.max_speed_hz = int(self.clock_speed)
        self.spi.cshigh = not self.chip_select_idle_high
        self.spi.mode = self.clock_polarization_phase_mode

    def end_spi_comm(self):
        self.spi.close()
        #self.set_addr(RESET_ADDRESS)

    def teds_string_to_list(self, inputstring):
        outputlist = []
        auxlist = inputstring.split(';')

        if inputstring != '':

            for item in auxlist:
                auxlist2 = item.split(',')
                auxlist3 = []

                for item2 in auxlist2:
                    auxlist3.append(int(item2))

                outputlist.append(auxlist3)

        return outputlist

    def setup_transducer(self):
        setupdatalist = self.teds_string_to_list(self.data_for_setup) 
        self.start_spi_comm()

        for el in setupdatalist:
            self.spi.writebytes(el)
            
        self.end_spi_comm()


    def bits_to_num(self, dataraw, startbyte, startbit, endbyte, endbit):
        byte = endbyte
        retrieveddata = 0

        if startbyte == endbyte:
            retrieveddata = (dataraw[endbyte] & \
                                self.mask_gen_start(startbit)) >> endbit

        else:
        
            while byte >= startbyte:

                if byte == endbyte:
                    retrieveddata += (dataraw[byte] & self.mask_gen_end(
                        endbit)) >> endbit

                elif byte == startbyte:
                    retrieveddata += (dataraw[byte] & self.mask_gen_start(
                        startbit)) << (8 - endbit + ((endbyte - byte - 1) * 8))

                else:
                    retrieveddata += dataraw[byte] << (8 - endbit + \
                                                       (endbyte - byte - 1) * 8)

                byte -= 1

        return retrieveddata


    def mask_gen_start(self, significant_bits):
        return 2 ** (significant_bits + 1) - 1

    def mask_gen_end(self, significant_bits):
        return ((2 ** 8) - (2 ** significant_bits))

    def num_to_bits(self, number, startbyte, startbit, endbyte, endbit):
        """ """
        byte = endbyte#endbyte
        data_bytes = []#[0] * (startbyte - endbyte +1)
        for i in range(endbyte+1):
            data_bytes.append(0)
        #convert data?
        convnumber = int(number)

        if startbyte == endbyte:
            data_bytes[endbyte] = convnumber << endbit

        else:   

            while byte >= startbyte:

                if byte == endbyte:
                    data_bytes[byte] = (convnumber & (self.mask_gen_end(endbit) >>
                                                  endbit))

                elif byte == startbyte:
                    data_bytes[byte] = (convnumber >> (endbit + (endbyte - byte - 1) \
                                                   * 8)) & self.mask_gen_start(
                                                       startbit)

                else:
                    data_bytes[byte] = (convnumber >> (endbit + (endbyte - byte - 1) \
                                                   * 8)) & 255

                byte -= 1

        return data_bytes

    def compose_serial_data(self, databytes, accessbytes, firstbyte, lastbyte):

        serialdata = copy.deepcopy(accessbytes)

        bytecount1 = 0
        bytecount2 = 0
        count1 = 0
        count2 = 0
        while count1 < len(serialdata):

            while count2 < len(serialdata[count1]):
                if bytecount1 >= firstbyte and bytecount1 <= lastbyte:
                    serialdata[count1][count2] += databytes[bytecount1]
                    bytecount2 += 1

                bytecount1 += 1
                count2 += 1

            count1 += 1

        return serialdata               
        

    def set_register(self, register):
        """"""
        cond = self.active and (self.registers[register].active_register and
                                self.registers[register].is_actuator)

        if self.registers[register].actuator_value > self.registers[register].maximum_value:
            self.registers[register].actuator_value = int(self.registers[register].maximum_value)

        if self.registers[register].actuator_value < self.registers[register].minimum_value:
            self.registers[register].actuator_value = int(self.registers[register].minimum_value)
        
        if cond:
            
            accessbytes = self.teds_string_to_list(self.registers[register].spi_access_bytes)
            databytes = self.num_to_bits(self.registers[register].actuator_value,
                                    self.registers[register].first_data_byte,
                                    self.registers[register].first_data_bit,
                                    self.registers[register].last_data_byte,
                                    self.registers[register].last_data_bit)

            transferbytes = self.compose_serial_data(databytes, accessbytes,
                                                     self.registers[register].first_data_byte,
                                                     self.registers[register].last_data_byte)
            print(transferbytes)            
                               
            gpio.output(self.pinused[0],0)#start reset
            #time.sleep(0.000000001)
            gpio.output(self.pinused[0],1)#stop reset    
            self.start_spi_comm()
            self.spi.writebytes([transferbytes[0][0],transferbytes[0][1],transferbytes[0][2]])
            self.spi.writebytes([transferbytes[0][3],transferbytes[0][4],transferbytes[0][5]])
            self.spi.writebytes([transferbytes[0][6],transferbytes[0][7],transferbytes[0][8]])
            self.spi.writebytes([transferbytes[0][9],transferbytes[0][10],transferbytes[0][11]])
            self.spi.writebytes([transferbytes[0][12],transferbytes[0][13],transferbytes[0][14]])
            self.end_spi_comm()


    def read_register(self, register):
        """"""
        self.start_spi_comm()
        accessbytes = self.teds_string_to_list(self.registers[register].spi_access_bytes)

        #print accessbytes
        receiveddata = []
        for el in accessbytes:
            #print el
            if self.registers[register].next_instruction == True:
                rawdata = self.spi.xfer2(el)
            rawdata = self.spi.xfer2(el)
            print('xfer2 data: ', rawdata)
            data = self.bits_to_num(rawdata,
                                    self.registers[register].first_data_byte,
                                    self.registers[register].first_data_bit,
                                    self.registers[register].last_data_byte,
                                    self.registers[register].last_data_bit)
            #print 'recv bits: ', data
            convdata = data * self.registers[register].value_constant_convertion
            print('conv data: ', convdata)
            receiveddata.append(convdata)

        self.end_spi_comm()

        #Verify if interruption is active
        if self.registers[register].activate_interruption:
            pass
        return receiveddata



def create_actuator_data(transducerdict):
    """"""
    actuatordata = {}

    for transducerid in transducerdict:
        #transducerdict[transducerid].message.append(MSG[0])

        if transducerdict[transducerid].active:
            actuatordata[transducerid] = {'name': transducerdict[transducerid].name}
            for register in transducerdict[transducerid].registers:

                if (transducerdict[transducerid].registers[register].active_register and
                    transducerdict[transducerid].registers[register].is_actuator):
                    actuatordata[transducerid][register] = (transducerdict[transducerid].registers[register].minimum_value,
                                                            transducerdict[transducerid].registers[register].maximum_value,
                                                            transducerdict[transducerid].registers[register].si_unit,
                                                            transducerdict[transducerid].registers[register].actuator_value)

    return actuatordata
                
        
def process_actuator_data(actuatordata, transducerdict):
    """"""
    for transducer in actuatordata:
        print('Teste_Registers')
        for register in transducerdict[transducer].registers:
            if (transducerdict[transducer].registers[register].active_register and transducerdict[transducer].registers[register].is_actuator):
                print(register)
                transducerdict[transducer].registers[register].actuator_value = int(actuatordata[transducer][register][3])
                transducerdict[transducer].set_register(register)


def update_sensor_data(sensordata, transducerdict, maxlen):
    """"""
    
    sensordata['timedata'][0].append(int(time.time()))# anexa tempo atual no lista de tempo

    if len(sensordata['timedata'][0]) > maxlen:# caso o tamanho da lista (amostragem) exceda o valor limite, reseta a lista
        del sensordata['timedata'][0][0]

    for transducerid in transducerdict:#varredura das TEDS

        if transducerdict[transducerid].active:#valida update somente para TEDS ativas

            for register in transducerdict[transducerid].registers:#varredura dos registradores de cada TED

                if (transducerdict[transducerid].registers[register].active_register and
                    transducerdict[transducerid].registers[register].is_sensor):#valida update dos registradores ativos e que tenham funcionalidade de sensor

                    if transducerid not in sensordata['sensordata']:#caso o transdutor tenha acabado de ser incluido, adiciona um dicionário dedicado aos dados daquele transdutor
                        sensordata['sensordata'][transducerid] = {'name': transducerdict[transducerid].name}

                    if register not in sensordata['sensordata'][transducerid]:#caso o registrador tenha acabado de ser incluido, adiciona: 
                        sensordata['sensordata'][transducerid][register] = \
                            ([0] * (len(sensordata['timedata'][0]) - 1),#valores nulos para todo o tempo passado ao qual o registrador ainda não existia
                             transducerdict[transducerid].registers[register].si_unit,#unidade de medida do registrador
                             transducerdict[transducerid].registers[register].register_name)#nome amigável do registrador

                    if len(sensordata['sensordata'][transducerid][register][0]) < (len(sensordata['timedata'][0]) - 1): # caso haja algum lapso onde o número de amostragens do registrador
                        sensordata['sensordata'][transducerid][register][0].append([0]* (len(sensordata['timedata'][0])-1-len(sensordata['sensordata'][transducerid][register][0])))#for menor do que as amostragens globais (medidas pela lista de tempo)corrige com a adição de zeros.
                        


                    data = transducerdict[transducerid].read_register(register)#Executa leitura SPI do registrador(iterador_r) do transdutor(iterador_t) em questão
                    data = convert_bit_voltage(data)#Falta Generalizar
                    sensordata['sensordata'][transducerid][register][0].append(data[0])#anexa valores lidos e convertidos para suas respectivas unidades             
                    
                    if len(sensordata['sensordata'][transducerid][register][0]) > maxlen:
                        del sensordata['sensordata'][transducerid][register][0][0]## caso o tamanho da lista (amostragem) exceda o valor limite, reseta a lista

    for transducerid in list(sensordata['sensordata'].keys()):#varredura dos transdutores no dicionário

        if (transducerid not in transducerdict):#caso transdutor não esteja mais presente
            del sensordata['sensordata'][transducerid]#apaga transdutor do dicionário
        else:

            if not transducerdict[transducerid].active:#caso transdutor não estiver mais ativo
                del sensordata['sensordata'][transducerid]#apaga do dicionário

            for register in list(sensordata['sensordata'][transducerid].keys()):#varredura dos registradores

                if (register != 'name'):

                    if register not in transducerdict[transducerid].registers:#se registrador não estiver mais presente
                        del sensordata['sensordata'][transducerid][register]#apaga do dicionário
                    else:

                        if not transducerdict[transducerid].\
                           registers[register].active_register:#se registrador não estiver mais ativo
                            del sensordata['sensordata'][transducerid][register]#apaga do dicionário
             


if __name__ == '__main__':

    import json
    import random

    def teste_set_reg(value):
        print(bin(value))
        for reg in shiftregister.registers:
            shiftregister.registers[reg].actuator_value = value
            shiftregister.set_register(reg)

    def teste_read_reg():
        res = []
        for i in adc.registers:
            res += adc.read_register(i)
        print(res)

    def zzteste(value):
        teste_set_reg(value)
        teste_read_reg()
        
        """
    with open('./teds/2018Mar05191357.ted', 'r') as auxfile1:
        tedsdict1 = json.load(auxfile1)
    print 'read adc ted!'
    adc = Transducer(tedsdict1)
    print 'create adc!'"""
    system_transducers = {}        
    tedsdict = pl.load_teds(sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + '2018Mar06200614')
    system_transducers[tedsdict['ID']] = Transducer(tedsdict)
    actuatordata = create_actuator_data(system_transducers)
    sf.save_data(actuatordata, sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)
    process_actuator_data(actuatordata, system_transducers)    
#with open('./teds/2018Mar06200614.ted', 'r') as auxfile2:        
        
        

##    with open(sc.MAIN_PATH+'teds'+'/'+'2016May06141756.ted', 'r') as auxfile:        
##        tedsdict = json.load(auxfile)
##    print 'setup transducer'
##    shiftregister = Transducer(tedsdict)
##    print 'done'
##
##
##    with open(sc.MAIN_PATH+'teds'+'/'+'2016May24202631.ted', 'r') as auxfile:
##    #with open(sc.MAIN_PATH+'teds'+'/'+'2016May06194553.ted', 'r') as auxfile:
##        tedsdict = json.load(auxfile)
##    print 'setup transducer'
##    adc = Transducer(tedsdict)
##    print 'done'
##
##
##    with open(sc.MAIN_PATH+'teds'+'/'+'2016May25140938.ted', 'r') as auxfile:
##        tedsdict = json.load(auxfile)
##    print 'setup transducer'
##    termopark = Transducer(tedsdict)
##    print 'done'
##    

##    for i in [128, 0, 128, 128, 0, 128]:
##        num = random.randint(0,255)
##        teste_set_reg(num)
##        teste_read_reg()
##        time.sleep(1)

##    transd = {shiftregister.id: shiftregister,
##              adc.id: adc,
##              }
##
##    teste_sensor_data = {'timedata' : ([], 'second'),
##                         'sensordata': {}}
##
##    for i in range(10):
##        num = random.randint(0,255)
##        teste_set_reg(num)
##        update_sensor_data(teste_sensor_data, transd, 1000)
##        #print message_reader(transd)
##
##    print teste_sensor_data
##
##    teste_set_reg(-1)
##    #print message_reader(transd)
##    time.sleep(2)
##    teste_set_reg(-2)
##    #print message_reader(transd)
##    time.sleep(2)
##    teste_set_reg(257)
##    #print message_reader(transd)
##    time.sleep(2)
##    teste_set_reg(258)
##    #print message_reader(transd)
##    teste_set_reg(202)
##    print message_reader(transd)

##
##    for reg in termopark.registers:
##        termopark.read_register(reg)
        

