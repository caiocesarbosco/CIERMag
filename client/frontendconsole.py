# -*- coding: utf-8 -*-
"""


"""
import json
import time
import http.client
import os.path
from collections import OrderedDict

import parameterlib as pl

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, \
    ParameterItem, registerParameterType
import pyqtgraph.console
from pyqtgraph.dockarea import *



WINSIZE = [1200, 800]
MAXLENGTH = 60 * 60 * 24
PENCOLOR = ['r', 'g', 'b', 'c', 'm', 'y', 'w', 'k']

HOST = "10.42.0.116"
#HOST = "192.168.10.116"
#HOST = "192.168.10.170"
#HOST = "127.0.0.1"
PORT = 5000

HEAD_PATH, SCRIPT_NAME = os.path.split(__file__) 


def rebuild_ordereddict(orddict):
    """Create a new dictionary with the meaningful values"""
    newdict = OrderedDict()
    for key in orddict:
        if orddict[key][0] != None:
            newdict[key] = orddict[key][0]
        else:
            newdict[key] = rebuild_ordereddict(orddict[key][1])
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
    rawteds = []
    if len(inputdict) != 0:
        rawteds = basetedsdic[:]

        for key in inputdict:
            if type(inputdict[key]) == type({}):
                rawteds.append(dict(baseregisterdict))
                rawteds[-1]['name'] = key

                for subkey in inputdict[key]:
                    index = search_entry_index(subkey, baseregisterdict)
                    if index != None:
                        rawteds[-1]['children'][index]['value'] = inputdict[key][subkey]

            else:
                index = search_entry_index(key, basetedsdic)
                if index != None:
                    rawteds[index]['value'] = inputdict[key]
                    
    teds.clearChildren()
    teds.addChildren(rawteds)
        

def set_teds_list_from_dict(inputdict, tedslist):
    """ """
    tedslist.clearChildren()
    for key in inputdict:
        tedslist.addChild({'name': key, 'type': 'group', 'children': [
            {'name': inputdict[key], 'type': 'bool', 'value': False}
            ]})
                

def send_teds_to_server(teds, host, port, header):
    """ """
    tedsvalues = teds.getValues()
    tedsvalues = rebuild_ordereddict(tedsvalues)
    tedsstr = json.dumps(tedsvalues)
    http_post(pl.CONSOLE_TEDS_PAGE + '/' + tedsvalues[pl.TEDS_NAME_ID],
              host, port, header, tedsstr)


def update_teds_tedsdictlist(teds, tedsdictlist, address, host, port, header):
    """ """
    http_get_tedslist(address, host, port, header, tedsdictlist)
    set_new_teds(teds)


## If anything changes in the TEDS list, print a message
def teds_list_change(param, changes):

    global selected_teds, par_teds
    (param, change, data) = changes[0]

    if change == 'value':
        tedschanged = param
        tedschangedparent = tedschanged.parent().parent()
        selected_teds = tedschanged
        selectedtedsname = tedschanged.name()
        deselect_other_teds(tedschangedparent, selectedtedsname)
        teds = http_get(pl.CONSOLE_TEDS_PAGE + '/' +
                        tedschanged.parent().name(), HOST, PORT, pl.HEADERS)
        set_teds_fields_from_dict(teds, par_teds, pl.TEDS_BUILD_DICT,
                                  pl.REGISTER_BUILD_DICT)
    


def deselect_other_teds(tedslist, lastselected): # need to prevent uncheck teds
    """When select one TEDS, deselect the others"""
    with tedslist.treeChangeBlocker():
        for ch in tedslist.children():
            for gch in ch:                
                if gch.name() is not lastselected:
                    gch.setValue(False)
        tedslist.treeStateChanges = [] # do not flush the changes to prevent inf loop
        


def set_new_teds(teds):
    """Clear all fields and create a new ID for the new TEDS"""
    for child in teds:
        if child.hasChildren():
            child.remove()
        else:
            child.setToDefault()
            teds.child(pl.TEDS_NAME_ID).setValue(pl.id_generator())



def plot_sensors(sensordata, plotwidget, plotcurves, sensorsdock):
    """ """
    rowcont = 0
    for transducer in sensordata['sensordata']:
               
        plotwidget[transducer] = pg.PlotWidget(
            title=transducer+': '+sensordata['sensordata'][transducer]['name'])
        plotwidget[transducer].showGrid(x = True, y = True, alpha = 0.5)
        plotwidget[transducer].addLegend()
        sensorsdock.addWidget(plotwidget[transducer], col=0, row=rowcont)

## Experimental
##        plotwidget[transducer] = sensorsdock.addPlot(
##            title=transducer+': '+sensordata['sensordata'][transducer]['name'],
##            col=0, row=rowcont)
##        plotwidget[transducer].showGrid(x = True, y = True, alpha = 0.5)
##        plotwidget[transducer].addLegend()
        
        plotcurves[transducer] = {}
        i = 0
        for register in sensordata['sensordata'][transducer]:
            if register != 'name':
                plotcurves[transducer][register] = plotwidget[transducer].plot(
                    sensordata['timedata'][0],
                    sensordata['sensordata'][transducer][register][0],
                    name=register + ' [' + sensordata['sensordata'][transducer][register][1] + ']',
                    pen=pg.mkPen(PENCOLOR[i]))
                i += 1

        rowcont += 1


def load_controllers_data(controllerparameter):
    """"""
    controllerdata = http_get(pl.CONSOLE_CONTROLLERS_DATA, HOST,
                              PORT, pl.HEADERS)

    controllerparameter.clearChildren()

    for transducerid in controllerdata:
        controllerparameter.addChild(
            {'name': transducerid, 'type': 'group', 'children': [
                {'name': 'name',
                 'type': 'str',
                 'value': controllerdata[transducerid]['name'],
                 'readonly': True}
                ]})

        for register in controllerdata[transducerid]:

            if register != 'name':
                controllerparameter.child(transducerid).addChild(
                    {'name': register,
                     'type': 'group',
                     'children': []})

                index = 0
                for param in controllerdata[transducerid][register]:

                    if pl.CONTROLLERS_PARAMETERS[index] == pl.TEDS_NAME_ACTUATORVALUE:
                        controllerparameter.child(transducerid).child(register).addChild(
                            {'name': pl.CONTROLLERS_PARAMETERS[index],
                             'type': 'str',
                             'value': controllerdata[transducerid][register][index],
                             'readonly': False})
                    else:
                        controllerparameter.child(transducerid).child(register).addChild(
                            {'name': pl.CONTROLLERS_PARAMETERS[index],
                             'type': 'str',
                             'value': controllerdata[transducerid][register][index],
                             'readonly': True})
                    index += 1
    
    

## HTTP Protocol
def http_post(address, host, port, headers, body):
    """ """
    conn = http.client.HTTPConnection(host=host, port=port)
    conn.request("POST", address, body, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()
    return data


def http_get(address, host, port, headers):
    """ """
    conn = http.client.HTTPConnection(host=host, port=port)
    conn.request("GET", address, headers=headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    convdata = json.loads(data)
    conn.close()
    return convdata


def http_get_tedslist(address, host, port, headers, tedslist):
     recievedtedslist = http_get(address, host, port, headers)
     set_teds_list_from_dict(recievedtedslist, tedslist)



    

# Buttons functions
def newteds():
    set_new_teds(par_teds)
    deselect_other_teds(par_tedslist, 'newteds')

def save():
    send_teds_to_server(par_teds, HOST, PORT, pl.HEADERS)
    update_teds_tedsdictlist(par_teds, par_tedslist, pl.CONSOLE_PAGE, HOST,
                             PORT, pl.HEADERS)
    set_new_teds(par_teds)

def remove():
    global selected_teds
    
    if selected_teds.name() != None:
        http_get(pl.REMOVE_TEDS_PAGE + '/' + selected_teds.parent().name(),
                 HOST, PORT, pl.HEADERS)
        update_teds_tedsdictlist(par_teds, par_tedslist, pl.CONSOLE_PAGE, HOST,
                                 PORT, pl.HEADERS)

def copy():
    par_teds.child(pl.TEDS_NAME_ID).setValue(pl.id_generator())
    deselect_other_teds(par_tedslist, 'newteds')

def addfunction():
    par_teds.addChild(pl.REGISTER_BUILD_DICT, autoIncrementName=True)


def update_plot():

    plot_curves  = {}
    plot_widget = {}
    sensors_data = http_get(pl.CONSOLE_PLOT_DATA, HOST, PORT, pl.HEADERS)
##    plot_sensors(sensors_data, plot_widget, plot_curves, plotsarea) # Experimental
    plot_sensors(sensors_data, plot_widget, plot_curves, sensors_dock)


def update_controllers():
    
    load_controllers_data(controllers)


def save_controllers():

    ctrldata = pl.build_dict_from_ordereddict(controllers.getValues())
    print(json.dumps(ctrldata, indent=1))
    
                              
# Application
    
app = QtGui.QApplication([])

#variables initialization
selected_teds = None

## Create tree of Parameter objects
par_teds = Parameter.create(name='TEDS', type='group',
                            children=pl.TEDS_BUILD_DICT)
par_tedslist = Parameter.create(name='TEDS List', type='group', children={})

## Create ParameterTree tree
teds_tree = ParameterTree()
teds_tree.setParameters(par_teds, showTop=False)

tedslist_tree = ParameterTree()
tedslist_tree.setParameters(par_tedslist, showTop=False)

#par_teds.sigTreeStateChanged.connect(field_teds_change)
par_tedslist.sigTreeStateChanged.connect(teds_list_change)

## Create Window
win = QtGui.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.setWindowTitle('Application')

d1 = Dock('TEDS Editor area', size=(WINSIZE[0]/4, WINSIZE[1]))
d2 = Dock('Availble TEDS', size=(WINSIZE[0]/4,WINSIZE[1]))
area.addDock(d1, 'left')
area.addDock(d2, 'right')

w1 = pg.LayoutWidget()
w1.addWidget(teds_tree)
d1.addWidget(w1)
w2 = pg.LayoutWidget()
w2.addWidget(tedslist_tree, row=0, col=0)
d2.addWidget(w2)

win.show()
win.resize(WINSIZE[0],WINSIZE[1])

http_get_tedslist(pl.CONSOLE_PAGE, HOST, PORT, pl.HEADERS, par_tedslist)
set_new_teds(par_teds)

## Buttons
saveBtn = QtGui.QPushButton('Save TEDS')
newtedsBtn = QtGui.QPushButton('New TEDS')
removeBtn = QtGui.QPushButton('Remove TEDS')
copyBtn = QtGui.QPushButton('Copy TEDS')
addfunctBtn = QtGui.QPushButton('Add Register Function')

w1.addWidget(saveBtn, row=1, col=0)
w1.addWidget(newtedsBtn, row=4, col=0)
w1.addWidget(removeBtn, row=6, col=0)
w1.addWidget(copyBtn, row=7, col=0)
w1.addWidget(addfunctBtn, row=8, col=0)

saveBtn.clicked.connect(save)
newtedsBtn.clicked.connect(newteds)
removeBtn.clicked.connect(remove)
copyBtn.clicked.connect(copy)
addfunctBtn.clicked.connect(addfunction)


#Create Sensor Area


sensors_dock = Dock('Sensor Area', size=(WINSIZE[0]/4, WINSIZE[1]))
area.addDock(sensors_dock, 'right')

##Experimental
##sensors_dock = Dock('Sensor Area', size=(WINSIZE[0]/4, WINSIZE[1]))
##area.addDock(sensors_dock, 'right')
##scrollarea = pg.QtGui.QScrollArea()
##sensors_dock.addWidget(scrollarea)
##plotsarea = pg.GraphicsLayoutWidget()
##plotsarea.setFixedHeight(WINSIZE[1])
##plotsarea.setFixedWidth(WINSIZE[0]/4)
##scrollarea.setWidget(plotsarea)



#Buttom area
dock_button = Dock('Button Area', size=(WINSIZE[0]/4, WINSIZE[1]/10))
area.addDock(dock_button, 'right')
area.moveDock(dock_button, 'bottom', sensors_dock)
#Update button
sensors_button_update = QtGui.QPushButton('Update Plots')
dock_button.addWidget(sensors_button_update, row=0, col=0)
sensors_button_update.clicked.connect(update_plot)


# Create Controllers Area
controllers_dock = Dock('Controllers Area', size=(WINSIZE[0]/4, WINSIZE[1]))
area.addDock(controllers_dock, 'right')

controllers = Parameter.create(name='Controllers', type='group',children={})
controllers_tree = ParameterTree()
controllers_tree.setParameters(controllers, showTop=False)

contr_widget = pg.LayoutWidget()
contr_widget.addWidget(controllers_tree)
controllers_dock.addWidget(contr_widget)

ctrlbtn = QtGui.QPushButton('Update Controllers')
contr_widget.addWidget(ctrlbtn, row=1, col=0)
ctrlbtn.clicked.connect(update_controllers)

ctrlsavebtn = QtGui.QPushButton('Save Controllers')
contr_widget.addWidget(ctrlsavebtn, row=2, col=0)
ctrlsavebtn.clicked.connect(save_controllers)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

