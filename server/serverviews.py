import json
import os
import sys
from time import ctime, strftime, gmtime


from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from werkzeug import secure_filename
import importlib 

import perifericos.generico.parameterlib as pl
import serverconfig as sc
import perifericos.generico.serverfunctions as sf
import perifericos.generico.ciermagthread as ct
from perifericos.Rx_Tx.Conj_Motherboards import modulo_rx_tx
sys.path.append(sc.MAIN_PATH+pl.SCRIPT_FOLDER)

Modulo_Rx_Tx = []

METHOD_ERROR = 'Method not allowed'
PAGE_ERROR = 'Page not allowed'



# configuration
server_app = Flask(__name__)
server_app.secret_key = sc.SECRET_KEY
#session['logged_in'] = False
sf.make_dir()



@server_app.route('/', methods=['POST', 'GET'])
@server_app.route('/login', methods=['POST', 'GET'])
def login():
    """Login page view funcion. """
    error = None

    # Check if login form was sent
    if request.method == 'POST':

        # Check if it is a valid username and password
        if request.form['username'] != sc.USERNAME: 
            error = 'Invalid username'
        elif request.form['password'] != sc.PASSWORD:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect(url_for('main_page'))

    # Check if it is a GET method
    elif request.method == 'GET':
        page_dict = {'current_time': pl.id_generator()}
        return render_template('login_page.html', **page_dict)

    # Recieved invalid method
    else:
        return METHOD_ERROR



@server_app.route('/main', methods=['GET'])
def main_page():
        

    # Check if the user is logged
    if session.get('logged_in'):

        # CHeck the client: console or browser
        if str(request.user_agent) == pl.HEADERS['User-Agent']:
            return redirect(url_for(pl.CONSOLE_PAGE))

        else:
            tedsdictlist = sf.load_dict_teds_files(
                sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.TEDSLISTFILE)
            #return json.dumps(sc.MAIN_PATH + pl.FILE_FOLDER + pl.TEDSLISTFILE)
            #teds_list = sf.teds_list_from_dict(tedsdictlist)
            page_dict = {'teds_dictlist': tedsdictlist,
                         'current_time': pl.id_generator()}
            return render_template('main_page.html', **page_dict)

    else:
        return redirect(url_for('login'))



@server_app.route('/editor/<selected_teds>', methods=['POST', 'GET'])
def editor_page(selected_teds):

    # Check if the user is logged
    if session.get('logged_in'):

        msg = 'Welcome'
        print(request.form)

        if selected_teds == 'new_teds':
            baseteds = sf.set_new_teds(pl.TEDS_BUILD_DICT)
           
        else:
            tedsdict = pl.load_teds(sc.MAIN_PATH + pl.TEDS_FOLDER + '/' +
                                    selected_teds)
            baseteds = sf.create_web_dict_from_teds_dict(
                tedsdict, pl.TEDS_BUILD_DICT, pl.REGISTER_BUILD_DICT)

        page_dict = {
            'method': request.method,
            'message': msg,
            'webteds': baseteds
            }

        if request.method == 'GET':
            return render_template('editor_page.html', **page_dict)

        elif request.method == 'POST':           
            
            teds = sf.recover_teds_dict_from_form(
                request.form, pl.TEDS_BUILD_DICT, pl.REGISTER_BUILD_DICT)
            page_dict['message'] = teds
            ### lock here
            with ct.changed_teds_lock:
                sf.save_data(teds,
                             sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + \
                             teds[pl.TEDS_NAME_ID] + '.ted')
                ct.changed_teds.append(teds[pl.TEDS_NAME_ID])

            tedsdictlist = sf.load_dict_teds_files(
                sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.TEDSLISTFILE)
            tedsdictlist[teds[pl.TEDS_NAME_ID]] = teds[pl.TEDS_NAME_NAME]
            sf.save_data(tedsdictlist,
                         sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.TEDSLISTFILE)
            
##            return render_template('editor_page.html', **page_dict)
            return redirect(url_for('main_page'))

        else:
            return METHOD_ERROR

    else:
        return redirect(url_for('login'))


@server_app.route('/addregister/<selected_teds>', methods=['GET'])
def add_register(selected_teds):
    tedsdict = pl.load_teds(sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + selected_teds)
    newtedsdict = sf.add_register_function(tedsdict)
    sf.save_data(newtedsdict,
                 sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + newtedsdict[pl.TEDS_NAME_ID] + '.ted')
##    return json.dumps(newtedsdict, indent=1)
    return redirect(url_for('editor_page', selected_teds=selected_teds))


@server_app.route('/removeregister/<selected_register>', methods=['GET'])
def remove_register(selected_register):
    return selected_register
    #@@@@@@@@@@@@@


@server_app.route('/sensors_main', methods=['GET'])
def sensor_main_page():

            
    with ct.sensor_data_lock:
        sensor_data = sf.load_sensor_data(
                    sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SENSORDATAFILE)

    page_dict = {'sensor_data': sensor_data,
                 'message': 'Welcome',
                 'current_time': pl.id_generator(),
                 'print': ''
                 }
    
    return render_template('sensors_main_page.html', **page_dict)
        
@server_app.route('/uploader', methods = ['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        UPLOAD_DIR='/home/pi/front-end/server/scripts/' 
        server_app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
        if not os.path.isdir(UPLOAD_DIR):
            os.mkdir(UPLOAD_DIR)  
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(server_app.config['UPLOAD_FOLDER'],filename))
        scriptlist = sf.load_dict_script_files(sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SCRIPTLISTFILE)
        for item in request.form:
            scriptlist['scripts'].append({'script_name':request.form[item],'script_file':f.filename.split('.')[0]})  
        sf.save_data(scriptlist, sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SCRIPTLISTFILE)      
        return redirect(url_for('script_page'))


@server_app.route('/sensors/<selected_sensor>', methods = ['GET'])
def sensor_page(selected_sensor):

    page_dict = {}
    pagepath = selected_sensor + '.html'
    
    return render_template(pagepath, **page_dict)

@server_app.route('/scripts', methods=['GET'])
def script_page():
    
    if request.method == 'GET':
        script_dictlist = sf.load_dict_script_files(
        sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SCRIPTLISTFILE)
        
        page_dict = {'message':'Scripts',
                     'current_time':pl.id_generator(),
                     'script_dictlist': script_dictlist
                     }
        return render_template('script_page.html', **page_dict)
    
@server_app.route('/setups/rx_gain',methods=['GET','POST'])
def rx_gain_setup_page():
    
    if request.method == 'GET':
        
        if len(Modulo_Rx_Tx):    
            webdict=Modulo_Rx_Tx[0].instances_to_webdict()
            
        else:
            webdict={}
        
        page_dict = {'message':'RX TX GAIN SETUP',
                     'current_time': pl.id_generator(),
                     'webdict': webdict
                     }
        return render_template('rx_gain_setup_page.html',**page_dict)

    elif request.method == 'POST':
        
        if len(Modulo_Rx_Tx) == 0:
            Modulo_Rx_Tx.append(modulo_rx_tx())
        else:
            del Modulo_Rx_Tx[0]
            Modulo_Rx_Tx.append(modulo_rx_tx())
        #if request.form:
        #    pass
        #else: 
        #    Rx_Tx.detect_rx_modules()
        return redirect(url_for('rx_gain_setup_page'))

    else:
        return METHOD_ERROR 
    
@server_app.route('/setups/rx_gain/set_gain/<board>/<modulo>',methods=['POST'])
def set_gain_page(modulo,board):
    if request.form["gain"] != "-1":
        Modulo_Rx_Tx[0].set_gain_rx(board,modulo,request.form["gain"])
        
    return redirect(url_for('rx_gain_setup_page'))

@server_app.route('/setups/rx_gain/set_all_gain',methods=['POST'])
def set_all_gain_page():
    print(request.form)
    if request.form:
        for item in request.form:
            break_dict=item.split()
            if break_dict[0] == 'Run':
                if request.form["gain "+break_dict[1]+" "+break_dict[2]] != '-1':
                    Modulo_Rx_Tx[0].set_gain_rx(break_dict[1],break_dict[2],request.form["gain "+break_dict[1]+" "+break_dict[2]])
                return redirect(url_for('rx_gain_setup_page'))
        Modulo_Rx_Tx[0].webdict_to_instance(request.form)
    return redirect(url_for('rx_gain_setup_page'))

@server_app.route('/setups',methods=['GET'])
def setups_page():
    
    if request.method == 'GET':
        page_dict = {'message':'Setups',
                     'current_time':pl.id_generator()
                     }
        return render_template('setups_page.html', **page_dict)
    
@server_app.route('/runscript/<selected_script>', methods=['GET'])
def run_script(selected_script):
    
    if request.method == 'GET':
        script_dic=sf.load_dict_script_files(sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SCRIPTLISTFILE)
        for item in script_dic['scripts']:
            if item['script_name']== selected_script:
                module_name=item['script_file']
                print(module_name)
        ss=importlib.import_module(module_name,pl.SCRIPT_FOLDER)
        print(ss)
        ss.script_auto()
        return redirect(url_for('script_page'))
    
    

@server_app.route('/controllers', methods=['GET', 'POST'])
def controller_page():

    if request.method == 'GET':

        with ct.actuator_data_lock:
            controllers_data = sf.load_controllers_data(
                sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)
        page_dict = {'message': 'Welcome',
                     'controllers_data': controllers_data,
                     'counter': 0
                     }
        return render_template('controller_page.html', **page_dict)

    elif request.method == 'POST':
        
        with ct.actuator_data_lock:
            controllers_data = sf.save_controllers_data(request.form)
            ct.actuator_update = True
        return redirect(url_for('controller_page'))
        #return json.dumps(controllers_data)



# Console Pages ---------------------------------
#
@server_app.route(pl.CONSOLE_PAGE, methods=['GET'])
def console_page():

    # check who is connecting
    if str(request.user_agent) == pl.HEADERS['User-Agent']:

        if request.method == "GET":
            tedslist = sf.load_dict_teds_files(
                sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.TEDSLISTFILE)
            return json.dumps(tedslist)
      
        else:
            return "Not Supported Method"

    else:
        return "Page not Allowed"

@server_app.route(pl.CONSOLE_TEDS_PAGE + '/<selected_teds>',
                  methods=['POST', 'GET'])

def console_teds_page(selected_teds):

    # check who is connecting
    if str(request.user_agent) == pl.HEADERS['User-Agent']:

        if request.method == "GET":
            tedsid = selected_teds
            teds = pl.load_teds(
                sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + tedsid)
            return json.dumps(teds)

        elif request.method == "POST":
            tedsjson = request.json
            tedsid, tedsname = sf.get_teds_id_name(tedsjson)
            with ct.changed_teds_lock:
                pl.save_teds(request.json,
                             sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + tedsid)
                ct.changed_teds.append(tedsid)
            sf.add_teds_to_tedsdictlist(
                tedsid, tedsname,
                sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.TEDSLISTFILE)
            #return redirect(url_for('console_page')) #has to be the name of the function
            return "ok"
        
        else:
            return "Method Not Supported"
    
    else:
        return "User-Agent not Allowed"


@server_app.route(pl.REMOVE_TEDS_PAGE + '/<selected_teds>', methods=['GET'])
def console_remove_page(selected_teds):
    
        if str(request.user_agent) == pl.HEADERS['User-Agent']:
            sf.remove_teds_from_tedsdictlist(
                selected_teds, sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.TEDSLISTFILE)
            sf.remove_file(sc.MAIN_PATH + pl.TEDS_FOLDER + '/' + selected_teds + '.ted')
            return 'ok'

        else:
            return "Page not Allowed"

@server_app.route(pl.CONSOLE_PLOT_DATA, methods=['GET'])
def console_plot_data():

    with ct.sensor_data_lock:
        sensor_data = sf.load_sensor_data(
                    sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.SENSORDATAFILE)
    
    return json.dumps(sensor_data)

@server_app.route(pl.CONSOLE_CONTROLLERS_DATA, methods=['GET', 'POST'])
def console_controllers():

    if request.method == 'GET':
        with ct.actuator_data_lock:
            controllers_data = sf.load_controllers_data(
                sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)
        
        return json.dumps(controllers_data)

    elif request.method == 'POST':
        with ct.actuator_data_lock:
            sf.save_data(request.json,
                         sc.MAIN_PATH + pl.FILE_FOLDER + '/' + pl.CONTROLLERDATAFILE)
            ct.actuator_update = True
        #return redirect(url_for('controller_page'))
        #return json.dumps(controllers_data)

    else:
        return "Method not Allowed"

@server_app.route('/parameterlib', methods=['GET'])
def download_parameterlib():

    if request.method == 'GET':

        #parameterlib = sf.base_open_file('parameterlib.py', None)
        with open('parameterlib.py', 'r') as auxfile:
            parameterlib = auxfile.read()
        
        #return json.dumps(parameterlib)
        return parameterlib

    else:
        return "Method not Allowed"
