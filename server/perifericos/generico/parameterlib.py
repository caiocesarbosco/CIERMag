# -*- coding: utf-8 -*-
"""


"""
import json
import time
from collections import OrderedDict


TEDSLISTFILE = 'tedslist.txt'
SCRIPTLISTFILE = 'scriptlist.txt'
SENSORDATAFILE = 'sensordatafile.txt'
CONTROLLERDATAFILE = 'controllerdatafile.txt'
PLOTLISTFILE = 'plotlistfile.txt'
NEW_TEDS = "new_teds"

HEADERS = {"Content-type": "application/json",
           "Accept": "text/plain",
           "User-Agent": "ToRMConsole"}

CONSOLE_PAGE = "/tormconsole"
CONSOLE_TEDS_PAGE = "/tormconsole/teds"
NEW_TEDS_PAGE = "/new_teds"
REMOVE_TEDS_PAGE = "/tormconsole/remove"
CONSOLE_PLOT_DATA = "/tormconsole/plotdata"
CONSOLE_CONTROLLERS_DATA = "/tormconsole/controllers"

TEDS_FOLDER = "teds"
FILE_FOLDER = "files"
SCRIPT_FOLDER = "scripts"

RX_NAME_ID= 'ID'
## TEDS field related constant strings
# Strings for the TEDS field names
TEDS_NAME_NAME = 'Name'
TEDS_NAME_ID = 'ID'
TEDS_NAME_ACTIVE = 'Active'
TEDS_NAME_ADDRESS = 'SPI Address'
TEDS_NAME_CLKSPD = 'Clock Speed'
TEDS_NAME_SPI_SELECT = 'SPI Select'
TEDS_NAME_CSHIGH = 'Chip Select Idle High'
TEDS_NAME_CLOCKPOLPHASE = 'Clock Polarization/Phase Mode'
TEDS_NAME_SETUP = 'Data for Setup'

TEDS_NAME_REGISTER = 'Register'
TEDS_REGISTER_FRIENDNAME = 'Register Name'
TEDS_NAME_ACTIVEREGISTER = 'Active Register'
TEDS_NAME_ACCESSDATA = 'SPI Access Bytes'
TEDS_NAME_NEXT_INSTRUCTION = 'Next Instruction'
TEDS_NAME_SIUNIT = 'SI Unit'
TEDS_NAME_MINVALUE = 'Minimum Value'
TEDS_NAME_MAXVALUE = 'Maximum Value'
TEDS_NAME_CONVCONST = 'Value Constant Convertion'
TEDS_NAME_FIRSTDATABYTE = 'First Data Byte'
TEDS_NAME_LASTDATABYTE = 'Last Data Byte'
TEDS_NAME_FIRSTDATABIT = 'First Data Bit'
TEDS_NAME_LASTDATABIT = 'Last Data Bit'
TEDS_NAME_ISACTUATOR = 'Is Actuator'
TEDS_NAME_ACTUATORVALUE = 'Actuator Value'
TEDS_NAME_ISSENSOR = 'Is Sensor'
TEDS_NAME_ACTIVATEINTERRUPT = 'Activate Interruption'
TEDS_NAME_WARNINGTHRESHOLD = 'Warning Threshold'
TEDS_NAME_DANGERTHRESHOLD = 'Danger Threshold'

# Strings for the TEDS field tips
TEDS_TIP_NAME = 'Name for user identification.'
TEDS_TIP_ID = 'TEDS unique identification number.'
TEDS_TIP_ACTIVE = 'Set if the transducer will be used in the system.'
TEDS_TIP_ADDRESS = 'SPI physical address connected to the system. \
    It has a maximum value of 1024.'
TEDS_TIP_CLKSPD = 'Transducer SPI clock speed.'
TEDS_TIP_SPI_SELECT = 'Raspberry pin SPI selection GPIO(7/8)'
TEDS_TIP_CSHIGH = 'Set if chip select is idle high and active low.'
TEDS_TIP_CLOCKPOLPHASE = 'Clock polarization/phase mode: [pol|pha] 0b00=0... \
    0b11=3  '
TEDS_TIP_SETUP = 'Setup/Configuration bytes needed for the transducer initialization.'

TEDS_TIP_ACTIVEREGISTER = 'Set if the register will be used.'
TEDS_TIP_ACCESSDATA = 'Bytes used to access the register.'
TEDS_TIP_NEXT_INSTRUCTION = 'Interested Data came on the next instruction'
TEDS_TIP_SPI_SELECT = 'Raspberry pin SPI selection GPIO(7/8)'
TEDS_TIP_SIUNIT = 'The SI physical unit of the register.'
TEDS_TIP_MINVALUE = 'Minimum value it is able to measure.'
TEDS_TIP_MAXVALUE = 'Maximum value it is able to measure.'
TEDS_TIP_CONVCONST = 'Constant used to convert to digital input/output data'
TEDS_TIP_FIRSTDATABYTE = 'Start Byte of the data. Starts with B0 (first \
    sent/received byte), B1...'
TEDS_TIP_LASTDATABYTE = 'Last sent/recieved Data Byte'
TEDS_TIP_FIRSTDATABIT = 'The number of the position of the first bit (Most \
    Significant Bit) of the data in the First Data Byte. \
    Byte = (MSB)|b7|b6|b5|b4|b3|b2|b1|b0|(LSB)'
TEDS_TIP_LASTDATABIT = 'The number of the position of the last bit (Least \
    Significant Bit) of the data in the Last Data Byte. \
    Byte = (MSB)|b7|b6|b5|b4|b3|b2|b1|b0|(LSB)'
TEDS_TIP_ISACTUATOR = 'Checkbox confirming the transducer\'s actuation \
    function.'
TEDS_TIP_ACTUATORVALUE = 'Actuator target value'
TEDS_TIP_ISSENSOR = 'Checkbox confirming the transducer\'s sensing function.'
TEDS_TIP_ACTIVATEINTERRUPT = 'Activate Interruption'
TEDS_TIP_WARNINGTHRESHOLD = 'Warning  Threshold Value'
TEDS_TIP_DANGERTHRESHOLD = 'Danger  Threshold Value'

# TEDS dictionaries
TEDS_BUILD_DICT = [{'name': TEDS_NAME_NAME, 'type': 'str', 'value': '', 'tip': TEDS_TIP_NAME},
        {'name': TEDS_NAME_ID, 'type': 'str', 'value': '', 'tip': TEDS_TIP_ID, 'readonly': True},
        {'name': TEDS_NAME_ACTIVE, 'type': 'bool', 'value': True, 'tip': TEDS_TIP_ACTIVE},
        {'name': TEDS_NAME_ADDRESS, 'type': 'int', 'value': 1, 'limits': (1, 2 ** 10), 'tip': TEDS_TIP_ADDRESS},
        {'name': TEDS_NAME_CLKSPD, 'type': 'int', 'value': 0, 'siPrefix': True, 'suffix': 'kHz', 'tip': TEDS_TIP_CLKSPD},
        {'name': TEDS_NAME_SPI_SELECT, 'type': 'int', 'value': 1, 'tip':TEDS_TIP_SPI_SELECT},
        {'name': TEDS_NAME_CSHIGH, 'type': 'bool', 'value': True, 'tip': TEDS_TIP_CSHIGH},
        {'name': TEDS_NAME_CLOCKPOLPHASE, 'type': 'int', 'value': 0, 'limits': (0, 2 ** 2 - 1), 'tip': TEDS_TIP_CLOCKPOLPHASE},
        {'name': TEDS_NAME_SETUP, 'type': 'str', 'value': '', 'tip': TEDS_TIP_SETUP}
        ] 


REGISTER_BUILD_DICT = {'name': TEDS_NAME_REGISTER, 'type': 'group', 'renamable': True, 'removable': True, 'children':[
                {'name':TEDS_REGISTER_FRIENDNAME, 'type': 'str', 'value': ''},
                {'name': TEDS_NAME_ACTIVEREGISTER, 'type': 'bool', 'value': False, 'tip': TEDS_TIP_ACTIVEREGISTER},
                {'name': TEDS_NAME_ACCESSDATA, 'type': 'str', 'value': '', 'tip': TEDS_TIP_ACCESSDATA},
                {'name': TEDS_NAME_NEXT_INSTRUCTION, 'type':'bool','value':False, 'tip': TEDS_TIP_NEXT_INSTRUCTION},
                {'name': TEDS_NAME_SIUNIT, 'type': 'str', 'value': '', 'tip': TEDS_TIP_SIUNIT},
                {'name': TEDS_NAME_MINVALUE, 'type': 'float', 'value': 0, 'tip': TEDS_TIP_MINVALUE},
                {'name': TEDS_NAME_MAXVALUE, 'type': 'float', 'value': 0, 'tip': TEDS_TIP_MAXVALUE},
                {'name': TEDS_NAME_CONVCONST, 'type': 'float', 'value': 0, 'tip': TEDS_TIP_CONVCONST},
                {'name': TEDS_NAME_FIRSTDATABYTE, 'type': 'int', 'value': 0, 'tip': TEDS_TIP_FIRSTDATABYTE},
                {'name': TEDS_NAME_LASTDATABYTE, 'type': 'int', 'value': 0, 'tip': TEDS_TIP_LASTDATABYTE},
                {'name': TEDS_NAME_FIRSTDATABIT, 'type': 'int', 'value': 0, 'limits': (0, 2 ** 3 - 1), 'tip': TEDS_TIP_FIRSTDATABIT},
                {'name': TEDS_NAME_LASTDATABIT, 'type': 'int', 'value': 0, 'limits': (0, 2 ** 3 - 1), 'tip': TEDS_TIP_LASTDATABIT},
                {'name': TEDS_NAME_ISACTUATOR, 'type': 'bool', 'value': False, 'tip': TEDS_TIP_ISACTUATOR},
                {'name': TEDS_NAME_ACTUATORVALUE, 'type': 'float', 'value': 0, 'tip': TEDS_TIP_ACTUATORVALUE},
                {'name': TEDS_NAME_ISSENSOR, 'type': 'bool', 'value': False, 'tip': TEDS_TIP_ISSENSOR},
                {'name': TEDS_NAME_ACTIVATEINTERRUPT, 'type': 'bool', 'value': False, 'tip': TEDS_TIP_ACTIVATEINTERRUPT},
                {'name': TEDS_NAME_WARNINGTHRESHOLD, 'type': 'float', 'value': 0, 'tip': TEDS_TIP_WARNINGTHRESHOLD},
                {'name': TEDS_NAME_DANGERTHRESHOLD, 'type': 'float', 'value': 0, 'tip': TEDS_TIP_DANGERTHRESHOLD}
                ]}

RX_SETUP_BUILD_DICT = [{'name': 'Motherboard', 'type': 'float', 'value': 0}, 
                {'name': 'Slot', 'type': 'float', 'value': 0},                       
                {'name': RX_NAME_ID, 'type': 'str', 'value': '', 'readonly': True},
                {'name': 'Rx_Gate_Pair', 'type': 'int', 'value': 0 },
                {'name': 'Gain(Low/High)', 'type': 'int'}                 
                ]

CONTROLLERS_PARAMETERS = (TEDS_NAME_MINVALUE, TEDS_NAME_MAXVALUE,
                          TEDS_NAME_SIUNIT, TEDS_NAME_ACTUATORVALUE)

def get_list_from_text(inputstring):
    """Convert string type to list type at the TEDS field's input"""
    outputlist = []

    auxlist = inputstring.split(';')
    if inputstring != '':

        for item in auxlist:
            auxlist2 = item.split(',')
            intlist = []
            
            for item in auxlist2:
                intlist.append(int(item))

            outputlist.append(intlist)

    return outputlist


def get_text_from_list(inputlist):
    """Convert list type to string type at the TEDS field's input"""
    outputstring = ''
    auxlist3 = []

    for sublist in inputlist:
        auxlist = []

        for item in sublist:
            auxlist.append(str(item))

        auxlist2 = ','.join(auxlist)
        auxlist3.append(auxlist2)

    outputstring = ';'.join(auxlist3)
    return outputstring


def id_generator():
    """Create an unique identifier"""
    return time.strftime('%Y%b%d%H%M%S',time.gmtime())


def save_teds(datateds, fileteds):
    """Save TEDS in a file .ted from a dictionary"""
    with open(fileteds + '.ted', 'w') as auxfile:
        json.dump(datateds, auxfile, indent=1)


def load_teds(fileteds):
    """Load TEDS from a file .ted to a dictionary"""
    with open(fileteds + '.ted', 'r') as auxfile:
        datateds = json.load(auxfile)
    return datateds


def load_teds_ordereddict(fileteds):
    """Load TEDS from a file .ted to a ordered dictionary"""
    with open(fileteds + '.ted', 'r') as auxfile:
        datateds = json.load(auxfile, object_pairs_hook=OrderedDict)
    return datateds


def build_dict_from_ordereddict(orddict):
    """Create a new dictionary with the meaningful values"""
    newdict = OrderedDict()
    for key in orddict:
        if orddict[key][0] != None:
            newdict[key] = orddict[key][0]
        else:
            newdict[key] = build_dict_from_ordereddict(orddict[key][1])
    return newdict

def search_entry_index(entry, builddict):
    """ """
    if type(builddict) == type([]):
        for item in builddict:
            if item['name'] == entry:
                return builddict.index(item)

    elif type(builddict) == type({}):
        for item in builddict['children']:
            if item['name'] == entry:
                return builddict['children'].index(item)
            
    else:
        return None

def set_teds_fields_from_dict(inputdict, teds, basetedsdic, baseregisterdict):
    """Uses the dictionary to set the TEDS fields"""
    for key in inputdict:
        if type(inputdict[key]) == type(OrderedDict()):
            teds.addChild(baseregisterdict, autoIncrementName=True)
            teds.child(key).setName(key)

            for subkey in inputdict[key]:
                if ((subkey == TEDS_NAME_ACCESSDATA)):
                    teds.child(key).child(subkey).setValue(
                        get_text_from_list(inputdict[key][subkey]))
                else:
                    teds.child(key).child(subkey).setValue(inputdict[key][subkey])
        else:
            if key == TEDS_NAME_SETUP:
                teds.child(key).setValue(get_text_from_list(inputdict[key]))
            else:
                teds.child(key).setValue(inputdict[key])
                # if teds does not have the inputdict key?

def set_teds_list_from_dict(inputdict, tedslist):
    """ """
    for key in inputdict:
        tedslist.addChild({'name': key, 'type': 'group', 'children': [
            {'name': inputdict[key], 'type': 'bool', 'value': True}
            ]})
                
            

def set_teds_fields_from_file(fileteds, teds, basetedsdic, baseregisterdict):
    """Load TEDS from file and set the fields"""
    auxdict = load_teds_ordereddict(fileteds)
    set_teds_fields_from_dict(auxdict, teds, basetedsdic, baseregisterdict)


  
