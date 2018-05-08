# -*- coding: utf-8 -*-
"""

"""

import datetime
import json
import copy
import os.path
from os import mkdir
from os import remove as remove_file

##import matplotlib.pyplot as plt
##from matplotlib import dates
##import mpld3
from bokeh.plotting import figure, save, output_file



import parameterlib as pl
import serverconfig as sc

LINECOLOR = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF',
         '#000000', '#FF7F00']

SENSOR_TEST = {'sensordata': {'transduceridN': {'register1': ([3, 3, 3, 3, 3, 3, 3, 3, 3, 3],'V'),
                                              'register2': ([4, 4, 4, 4, 4, 4, 4, 4, 4, 4],'V'),
                                              'registerN': ([5, 5, 5, 5, 5, 5, 5, 5, 5, 5],'V'),
                                                'name': 'transducernameN'},
                              'transducerid2': {'register1': ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0],'W'),
                                              'register2': ([1, 1, 1, 1, 1, 1, 1, 1, 1, 1],'A'),
                                              'registerN': ([2, 2, 2, 2, 2, 2, 2, 2, 2, 2],'deg_C'),
                                                'name': 'transducername2'},
                              'transducerid1': {'register1': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],'Ohm'),
                                              'register2': ([1, 3, 5, 7, 9, 11, 13, 15, 17, 19],'A'),
                                              'registerN': ([1, 4, 7, 10, 13, 16, 19, 22, 25, 28],'%'),
                                                'name': 'transducername1'}},
               'timedata': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],'seconds')}

CONTROLLER__TEST = {'transducerid1': {'register1': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'register2': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'registerN': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'name': 'transducername1'
                                      },
                    'transducerid2': {'register1': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'register2': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'registerN': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'name': 'transducername2'
                                      },
                    'transduceridN': {'register1': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'register2': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'registerN': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                      'name': 'transducernameN'
                                      }
                    }



def make_dir():
    """Create the necessary folders if they do not exists"""

    tedsdir = sc.MAIN_PATH + pl.TEDS_FOLDER
    if not os.path.exists(tedsdir):
        mkdir(tedsdir)

    filedir = sc.MAIN_PATH + pl.FILE_FOLDER
    if not os.path.exists(filedir):
        mkdir(filedir)


def save_data(data, filename):
    """Save data in a file"""
    with open(filename, 'w') as auxfile:
        json.dump(data, auxfile, indent=1)


def base_open_file(filename, altdata):
    """ Function to perform basic file operations with error handling """
    
    try:
        with open(filename, 'r') as auxfile:
            loadeddata = json.load(auxfile)
        return loadeddata

    except IOError:
        with open(filename, 'w') as auxfile:
            json.dump(altdata, auxfile, indent=1)
        return altdata
    
def load_dict_script_files(dictscriptfilename):
    altdata = {'scripts':[]}#'script_name': [],'script_file': []}
    return base_open_file(dictscriptfilename, altdata)   

def load_dict_teds_files(dicttedsfilename):
    """"""

    altdata = {'scripts':[]}
    return base_open_file(dicttedsfilename, altdata)


def teds_list_from_dict(tedsdict):
    tedslist = []
    for key in tedsdict:
        tedslist.append(key + ': ' + tedsdict[key])

    return tedslist


def get_teds_id_name(tedsjson):
    #teds = json.loads(tedsjson)
    teds = tedsjson
    return (teds[pl.TEDS_NAME_ID], teds[pl.TEDS_NAME_NAME])


def add_teds_to_tedsdictlist(tedsid, tedsname, tedsdictlistfilename):
    tedsdictlist = load_dict_teds_files(tedsdictlistfilename)
    tedsdictlist[tedsid] = tedsname
    with open(tedsdictlistfilename, 'w') as auxfile:
        json.dump(tedsdictlist, auxfile, indent=1)
        

def remove_teds_from_tedsdictlist(tedsid, tedsdictlistfilename):
    tedsdictlist = load_dict_teds_files(tedsdictlistfilename)
    del tedsdictlist[tedsid]
    with open(tedsdictlistfilename, 'w') as auxfile:
        json.dump(tedsdictlist, auxfile, indent=1)


def create_web_dict_from_teds_dict(inputdict, basetedsdic, baseregisterdict):
    """Uses the dictionary to set the TEDS fields"""
    rawteds = []
    if len(inputdict) != 0:
        rawteds = copy.deepcopy(basetedsdic)

        for key in inputdict:
            if type(inputdict[key]) == type({}):
                rawteds.append(copy.deepcopy(baseregisterdict))
                rawteds[-1]['name'] = key

                for subkey in inputdict[key]:
                    index = pl.search_entry_index(subkey, baseregisterdict)
                    if index != None:
                        rawteds[-1]['children'][index]['value'] = inputdict[key][subkey]

            else:
                index = pl.search_entry_index(key, basetedsdic)
                if index != None:
                    rawteds[index]['value'] = inputdict[key]
    return rawteds

def set_new_teds(inputteds):
    teds = copy.deepcopy(inputteds)
    index = pl.search_entry_index(pl.TEDS_NAME_ID, teds)
    teds[index]['value'] = pl.id_generator()
    return teds

def set_new_parameters(inputteds):
    teds = copy.deepcopy(inputteds)
    index = pl.search_entry_index(pl.RX_NAME_ID, teds)
    teds[index]['value'] = pl.id_generator()
    return teds

def convert_values(inputdict, basetedsdic, baseregisterdict):
    """Uses the dictionary to set the TEDS fields"""
    boolcomp = ['True', True]
    for key in inputdict:

        if type(inputdict[key]) == type({}):
            for subkey in inputdict[key]:
                index = pl.search_entry_index(subkey, baseregisterdict)
                if index != None:
                    if baseregisterdict['children'][index]['type'] == 'int':
                        try:
                            value = int(inputdict[key][subkey])
                        except ValueError:
                            value = baseregisterdict['children'][index]['value']
                    elif baseregisterdict['children'][index]['type'] == 'float':
                        try:
                            value = float(inputdict[key][subkey])
                        except ValueError:
                            value = baseregisterdict['children'][index]['value']
                    elif baseregisterdict['children'][index]['type'] == 'bool':
                        value =  inputdict[key][subkey] in boolcomp
                    else:
                        value = inputdict[key][subkey]

                    inputdict[key][subkey] = value

        else:
            index = pl.search_entry_index(key, basetedsdic)
            if index != None:
                if basetedsdic[index]['type'] == 'int':
                    try:
                        value = int(inputdict[key])
                    except ValueError:
                        value = basetedsdic[index]['value']
                elif basetedsdic[index]['type'] == 'float':
                    try:
                        value = float(inputdict[key])
                    except ValueError:
                        value = basetedsdic[index]['value']
                elif basetedsdic[index]['type'] == 'bool':
                    value =  inputdict[key] in boolcomp
                else:
                    value = inputdict[key]
                    
                inputdict[key] = value
    return inputdict

def recover_teds_dict_from_form(form, baseteds, baseregister):
    tedsdict = {}
    for item in form:
        if '&_' in item:
            splitted = item.split('&_')
            if splitted[0] not in tedsdict:
                tedsdict[splitted[0]] = {}
##            if form[item]
            tedsdict[splitted[0]][splitted[1]] = form[item]
        else:
            tedsdict[item] = form[item]

        teds = convert_values(tedsdict, baseteds, baseregister)  
    return teds

def add_register_function(teds):
    rawregister = copy.deepcopy(pl.REGISTER_BUILD_DICT)
    i = 0
    while rawregister['name'] in teds:
        rawregister['name'] = pl.TEDS_NAME_REGISTER + str(i)
        i=i+1
    teds[rawregister['name']] = {}

    for item in rawregister['children']:
        teds[rawregister['name']][item['name']] = item['value']

    return teds


def load_sensor_data(filename):
    """
    
    sensors_data = {'sensordata': {'transduceridN': {'register1': ([3, 3, 3, 3, 3, 3, 3, 3, 3, 3],'V'),
                                              'register2': ([4, 4, 4, 4, 4, 4, 4, 4, 4, 4],'V'),
                                              'registerN': ([5, 5, 5, 5, 5, 5, 5, 5, 5, 5],'V'),
                                                'name': 'transducernameN'},
                              'transducerid2': {'register1': ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0],'W'),
                                              'register2': ([1, 1, 1, 1, 1, 1, 1, 1, 1, 1],'A'),
                                              'registerN': ([2, 2, 2, 2, 2, 2, 2, 2, 2, 2],'deg_C'),
                                                'name': 'transducername2'},
                              'transducerid1': {'register1': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],'Ohm'),
                                              'register2': ([1, 3, 5, 7, 9, 11, 13, 15, 17, 19],'A'),
                                              'registerN': ([1, 4, 7, 10, 13, 16, 19, 22, 25, 28],'%'),
                                                'name': 'transducername1'}},
               'timedata': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],'seconds')}
               
    """

    altdata = {'timedata': ([], 'Time'),
               'sensordata': {}}
    #altdata = SENSOR_TEST
    return base_open_file(filename, altdata)


def load_plot_list(filename):
    """ """
    altdata = []
    return base_open_file(filename, altdata)
    

def remove_old_plots(plotlist):
    """"""

    for plot in plotlist:
        remove_file(plot)

        

##def html_plot_generator(sensordata):
##    """  """
##    
##    plotlistfullpath = sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.PLOTLISTFILE
##    plotlist = load_plot_list(plotlistfullpath)
##    remove_old_plots(plotlist)
##    plotlist = []
##
##    time = map(datetime.datetime.fromtimestamp, sensordata['timedata'][0])
##    convtime = dates.date2num(time)
##    timeformat = dates.DateFormatter('%H:%M')
##    
##    for transducer in sensordata['sensordata']:
##        fig, ax = plt.subplots(figsize=(12, 6))
##
##        for register in sensordata['sensordata'][transducer]:
##            if register != 'name':                   
##
##                plt.xticks(rotation=70)
##                plt.plot(convtime,
##                        sensordata['sensordata'][transducer][register][0],
##                        lw=4, alpha=1,
##                        label=register + ' [' + sensordata['sensordata'][transducer][register][1] + ']')
##        
##        plt.title(transducer + ': ' + sensordata['sensordata'][transducer]['name'],
##                  size=30, fontweight='bold')
##
##        ax.xaxis.set_major_locator(dates.MinuteLocator())
##        #ax.xaxis.set_major_locator(dates.SecondLocator())
##        ax.xaxis.set_major_formatter(timeformat)
##        
##        ax.set_xlabel(sensordata['timedata'][1], size=20)
##        ax.grid(color='black', alpha=0.5)
##        ax.legend(loc=1)
##
##        yajust = ax.get_yticks()
##        ax.set_ylim(2 * yajust[0] - yajust[1],
##                    2 * yajust[len(yajust) - 1] - yajust[len(yajust) - 2])
##
##        fig.autofmt_xdate()
##        fullname = sc.MAIN_PATH + 'templates/' + str(transducer) + ".html"
##        plotlist.append(fullname)
##        mpld3.save_html(fig, fullname)
##        mpld3.show()
##
##    save_data(plotlist, plotlistfullpath)

def html_bokeh_plot_generator(sensordata):
    """  """
    
    plotlistfullpath = sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.PLOTLISTFILE
    plotlist = load_plot_list(plotlistfullpath)
    remove_old_plots(plotlist)
    plotlist = []

    time = list(map(datetime.datetime.fromtimestamp, sensordata['timedata'][0]))
        
    for transducer in sensordata['sensordata']:
        fig = figure(x_axis_type="datetime")
        fig.title = transducer + ': '+sensordata['sensordata'][transducer]['name']

        color = 0
        for register in sensordata['sensordata'][transducer]:

            if register != 'name':
                fig.line(time,
                         sensordata['sensordata'][transducer][register][0],
                         color = LINECOLOR[color],
                         legend=register+' ['+sensordata['sensordata'][
                             transducer][register][1]+']')
                color += 1
        
        fig.xaxis.axis_label = sensordata['timedata'][1]
        #fig.xaxis.major_label_orientation = 'vertical'
        
        fullname = sc.MAIN_PATH + 'templates/' + str(transducer) + ".html"
        plotlist.append(fullname)
        output_file(fullname)
        save(fig)


    save_data(plotlist, plotlistfullpath)


def load_controllers_data(filename):
    """
    
    controllers_data = {'transducerid1': {'register1': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'register2': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'registerN': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'name': 'transducername1'
                                          },
                        'transducerid2': {'register1': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'register2': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'registerN': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'name': 'transducername2'
                                          },
                        'transduceridN': {'register1': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'register2': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'registerN': ('MinValue', 'MaxValue', 'Unit', 'ActuatorValue'),
                                          'name': 'transducernameN'
                                          }
                        }
    
    """
                
    altdata = {}
    altdata = CONTROLLER__TEST
    return base_open_file(filename, altdata)



def save_controllers_data(controllersdata):

    prevdatapath = sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE
    prevdata = load_controllers_data(prevdatapath)

    for item in controllersdata:
        if '&_' in item:
            splitted = item.split('&_')

            if controllersdata[item] != '':
                prevdata[splitted[0]][splitted[1]][3] = controllersdata[item]
            
    save_data(prevdata, prevdatapath)


if __name__ == "__main__":

    print('load data: ', datetime.datetime.now())
    sensordata = load_sensor_data(
        sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SENSORDATAFILE)
    print('end load data: ', datetime.datetime.now())

    html_bokeh_plot_generator(sensordata)

    
