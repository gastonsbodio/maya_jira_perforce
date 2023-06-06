### common functions module
import sys
import json
import os
import stat
import subprocess
si = subprocess.STARTUPINFO()
import definitions as de
try:
	import importlib
except Exception:
    pass
try:
    reload(de)
except Exception:
    importlib.reload(de)
sys.path.append( de.PY_PACKAGES)
import yaml as yaml

def make_read_write(filename):
    """set file as read-only false
    Args:
        filename ([str]): [description]
    """
    os.chmod(filename, stat.S_IWRITE)

def metadata_dicc2json(path, dicc):
    """Creates a json file from a givem dicctionary
    Args:
        path ([str]): [json file path ]
        dicc ([dicc obj]): [description]
    """
    json_object = json.dumps( dicc, indent = 2 ) 
    with open( path, 'w') as fileFa:
        fileFa.write( str(json_object) )
        fileFa.close()
        
def json2dicc_load(path):
    """Read a json dicc and return a python dicc
    Args:
        path ([str]): [json file path]

    Returns:
        [dicc]: [description]
    """
    dicc = {}
    if os.path.isfile( path ):
        with open( path) as fileFa:
            dicc = json.load(fileFa)
            fileFa.close()
    return dicc

def load_jira_vars():
    """instancing loging vars for make it run Jira queries.
    """
    dicc = json2dicc_load( de.TEMP_FOL+de.LOGIN_METADATA_FI_NA )
    if dicc != {}:
        USER = str( dicc['emailAddress'] ) 
        APIKEY = str( dicc['apikey'] )
        PROJECT_KEY = str( dicc['project'] )
    else:
        USER = 'None'
        APIKEY = 'None'
        PROJECT_KEY = 'None'
    return  USER , APIKEY, PROJECT_KEY

def load_anim_check_vars( QMessageBox, app ):
    """instancing anim check tool vars.
    """
    dicc = json2dicc_load( de.TEMP_FOL+de.ANIM_CHECK_TOOL_SETTING )
    if dicc != {}:
        GOOG_DOC_NA      = str( dicc['sheet_na'] )
        try:
            SHEET_NA         = str( dicc['form_na'] )
        except Exception:
            QMessageBox.information(app, u'Googlesheet error.', 'PLease, delete: '+de.TEMP_FOL+de.ANIM_CHECK_TOOL_SETTING +"""   
                                    and fill settings again
                                    """)
        DEPOT_ANIM_ROOT  = str( dicc['depot_a_root'] )
        UNREAL_ANIM_ROOT = str( dicc['unreal_a_root'] )
    else:
        GOOG_DOC_NA = 'None'
        SHEET_NA = 'None'
        DEPOT_ANIM_ROOT = 'None'
        UNREAL_ANIM_ROOT = 'None'
    return GOOG_DOC_NA , SHEET_NA , DEPOT_ANIM_ROOT, UNREAL_ANIM_ROOT

def load_perf_vars():
    """instancing loging vars for make it run  Perforce queries.
    """    
    dicc = json2dicc_load( de.TEMP_FOL+de.PERF_LOG_METADATA_FI_NA )
    if dicc != {}:
        PERF_USER = str( dicc['perf_user'] ) #'user'])
        PERF_WORKSPACE = str( dicc['perf_workspace'] )
        PERF_SERVER = str( dicc['perf_server'] )
    else:
        PERF_USER = 'None'
        PERF_WORKSPACE = 'None'
        PERF_SERVER = 'None'
    return  PERF_USER ,PERF_SERVER ,PERF_WORKSPACE 

def load_root_vars():
    """instancing roots vars for path building.
    """    
    dicc = json2dicc_load( de.TEMP_FOL+de.ROOTS_METAD_FI_NA )
    if dicc != {}:
        LOCAL_ROOT = str( dicc['local_root'] )
        DEPOT_ROOT = str( dicc['depot_root'] )
    else:
        LOCAL_ROOT = 'None'
        DEPOT_ROOT = 'None'
    return  LOCAL_ROOT ,DEPOT_ROOT 

def get_yaml_fil_data(path):
    """Read a yaml metadata file and return a dicc
    Args:
        path ([str]): [given yamel file path]
    Returns:
        [dicc]: [description]
    """
    data = {}
    if os.path.isfile( path ):
        with open(path , "r") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
            stream.close()
        return data
    else:
        return None

def separate_path_and_na(full_path):
    """Return separated values on a full path (path and file)
    Args:
        full_path ([str]): [full file path]
    Returns:
        [touple]: [touple of strings with path, and file name]
    """
    fi_na = full_path.split('/')[-1]
    path_ = full_path.split(fi_na)[0]
    return path_ , fi_na

def format_path(path):
    path = path.replace('\\','/')
    if not path.endswith('/'):
        path = path + '/'
    return path

def solve_path( root_state, asset_na, key_path, 
            local_root, depot_root, git_root, proj_settings ):
    """Retrun local desire path or depot path depending is_local value.
    Args:
        root_state (str): ['local', 'depot', 'git']
        asset_na ([str]): [asset name]
        key_path ([str]): [dicc key built in __settintgs__]
    Returns:
        [str]: [dep path or local path depending is_local value]
    """
    if proj_settings['Paths'][key_path].format(char_na = asset_na) != '':
        if root_state == 'local':
            return local_root + proj_settings['Paths'][key_path].format(char_na = asset_na)
        elif root_state == 'depot':
            return depot_root + proj_settings['Paths'][key_path].format(char_na = asset_na)
        elif root_state == 'git':
            return git_root + proj_settings['Paths'][key_path].format(char_na = asset_na)
    else:
        return ''

def only_name_out_extention( file_path , with_prefix = True, prefix = '' ):
    path, name = separate_path_and_na( file_path )
    file = name.split('.')[0]
    if with_prefix:
        if not file.startswith (prefix):
            file = prefix + file
    return file

def get_google_doc_data( app, QMessageBox, gs ,sheet_na ,sheet_num):
    """read_google_sheet.
    """
    goo_sheet = gs.GoogleSheetRequests()
    if sheet_na != '' and sheet_na != 'None':
        dicc =  goo_sheet.get_data_custom_google_sheet( sheet_na , sheet_num)
        if dicc[ de.key_errors ] == '[]':
            return dicc[ de.ls_result ] 
        else:
            QMessageBox.information(app, u'Googlesheet error.', str( dicc[de.key_errors] )  )
            return []
    else:
        return []

def edit_google_sheet_cell( app , QMessageBox , gs , sheet_na , sheet_num , goog_sh_col_ls , new_value_ls , rowIdx ):
    """read_google_sheet.
    """
    goo_sheet = gs.GoogleSheetRequests()
    if sheet_na != '' and sheet_na != 'None':
        dicc =  goo_sheet.edit_goog_sheet_cell(  sheet_na, sheet_num, goog_sh_col_ls , new_value_ls , rowIdx )
        if dicc[ de.key_errors ] == '[]':
            return dicc[ de.ls_result ] 
        else:
            QMessageBox.information( app, u'Googlesheet error.', str( dicc[de.key_errors] )  )
            return []
    else:
        return []

def run_py_stand_alone( python_file_na , with_console = False):
    """create a bat file witch run python stand alone
    Args:
        python_file_na ([str]): [python file path]
    """
    batPythonExec = '@echo off\n'
    batPythonExec = batPythonExec + '"'+ de.PY_PATH.replace('/','\\') + 'python.exe" "'+de.PY_PATH.replace('/','\\')+python_file_na+'.py" \n'
    with open( de.PY_PATH+"Execute_" + python_file_na + ".bat", "w") as fileFa:
        fileFa.write( batPythonExec )
        fileFa.close()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    if with_console == False:
        subprocess.call( [r'%sExecute_%s.bat'%( de.PY_PATH.replace('/','\\\\') , python_file_na ) ] , startupinfo = si )
    elif with_console == True:
        subprocess.Popen( [r'%sExecute_%s.bat'%( de.PY_PATH.replace('/','\\\\')  , python_file_na ) ] )
    elif with_console == 'Special':
        subprocess.call( [r'%sExecute_%s.bat'%( de.PY_PATH.replace('/','\\\\')  , python_file_na ) ] )
    #subprocess.call(["start", 'C:\\Python27\\Execute_google_sheet_query.bat'], shell=True)

def write_perforce_command_file ( line, if_result, result_fi_na, perf_server, perf_user, workspace):
    """Specific Perforce command, will be the content on a python file
        not possible to run Perforces commands directly in Maya.
    Args:
        line ([str]): [code line to insert on script]
        if_result ([Bool]): [if is able a return ending lines]
        result_fi_na ([str]): [name of file saved with the return result]
    Returns:
        [str]: [python script command content formated]
    """
    file_content =                'import sys \n'
    file_content = file_content + 'sys.path.append( "{path}" )\n'.format( path = de.SCRIPT_FOL )
    file_content = file_content + 'sys.path.append( "%s" )\n' %de.PY2_PACKAGES
    file_content = file_content + 'from P4 import P4,P4Exception \n' 
    file_content = file_content + 'import json\n'  
    file_content = file_content + 'import perforce_requests as pr\n' 
    file_content = file_content + 'reload (pr)\n'
    file_content = file_content + 'p4 = P4() \n'
    file_content = file_content + 'p4.port = "%s"   \np4.user = "%s"   \np4.client = "%s"   \n'%(perf_server, perf_user, workspace)
    file_content = file_content + 'error_ls = [] \n'
    file_content = file_content + '%s = [] \n' %de.ls_result
    file_content = file_content + 'try:\n'
    file_content = file_content + '    perf = pr.PerforceRequests()\n'
    file_content = file_content + '    p4.connect()\n'
    file_content = file_content + line +'\n'
    file_content = file_content + '    p4.disconnect()\n' 
    file_content = file_content + 'except P4Exception as err:\n'
    file_content = file_content + '    print( err )\n' 
    file_content = file_content + '    error_ls = ["Perforce Errors"] \n' 
    file_content = file_content + '    for e in p4.errors:\n'
    file_content = file_content + '        error_ls.append(str(e))\n'
    if if_result:
        file_content = file_content + de.dicc_result +' = {}\n'
        file_content = file_content + de.dicc_result + '["'+ de.ls_result +'"] = '+ de.ls_result+'\n'
        file_content = file_content + de.dicc_result + '["'+ de.key_errors +'"] = str(error_ls)\n'
        file_content = file_content +'json_object = json.dumps( {dicc_result}, indent = 2 )\n'.format( dicc_result = de.dicc_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content

def write_jira_command_file( line, if_result, result_fi_na , user , server, apikey, with_jira_q = True ):
    """Specific Jira command, will be the content on a python file
        not possible to run Jira commands when you launch Maya with Gearbox launcher.
    Args:
        line ([str]): [code line to insert on script]
        if_result ([Bool]): [if is able a return ending lines]
        result_fi_na ([str]): [name of file saved with the return result]
        user ([str]): [user email jira login]
        server ([str]): [example: "https://genvidtech.atlassian.net"]
        apikey ([str]): [jira api key instead of using password]
    Returns:
        [str]: [python script command content formated]
    """
    file_content =                   'import sys\n'
    file_content = file_content +    'sys.path.append( "{path}" )\n'.format( path = de.SCRIPT_FOL )
    file_content = file_content +    'import definitions as de\n'
    file_content = file_content +    'import jira_queries as jq\n'
    file_content = file_content +    'reload(de)\n'
    file_content = file_content +    'reload(jq)\n'
    file_content = file_content +    'sys.path.append( de.PY2_PACKAGES )\n'
    file_content = file_content +    'from jira import JIRA\n'
    file_content = file_content +    'import requests\n'
    file_content = file_content +    'from requests.auth import HTTPBasicAuth\n'
    file_content = file_content +    'import json\n'
    file_content = file_content +    'options = {"server": "%s" }\n'%( server )
    file_content = file_content +    'error_ls = []\n'
    file_content = file_content +    '%s = []\n' %de.ls_ji_result
    file_content = file_content +    'try:\n'
    file_content = file_content +    '    jira_m = jq.JiraQueries()\n'
    file_content = file_content +    '    jira =  JIRA(options, basic_auth=( "%s", "%s" ))\n'%( user, apikey )
    if with_jira_q :
        file_content = file_content +    '    ' + line.format( object = 'jira_m.')  + '\n'
    else:
        file_content = file_content +    '    ' + line + '\n'
    file_content = file_content +    'except Exception as err:\n'
    file_content = file_content +    '    error_ls = ["Jira Error"]\n'
    file_content = file_content +    '    error_ls.append(err)\n'
    file_content = file_content +    '    print( err )\n'
    if if_result:
        file_content = file_content + de.dicc_ji_result +' = {}\n'
        file_content = file_content + de.dicc_ji_result + '["'+ de.ls_ji_result +'"] = '+ de.ls_ji_result+'\n'
        file_content = file_content + de.dicc_ji_result + '["'+ de.key_errors +'"] = str(error_ls)\n'
        file_content = file_content +'json_object = json.dumps( {dicc_ji_result}, indent = 2 )\n'.format( dicc_ji_result = de.dicc_ji_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content

def write_request_jira_file( line, if_result, result_fi_na ):#
    """Specific Jira command, will be the content on a python file made with python requests.
        not possible to run Jira commands when you launch Maya with Gearbox launcher.
    Args:
        line ([str]): [code line to insert on script]
        if_result ([Bool]): [if is able a return ending lines]
        result_fi_na ([str]): [name of file saved with the return result]
    Returns:
        [str]: [python script command content formated]
    """
    file_content =                   'import sys\n'
    file_content = file_content +    'sys.path.append( "{path}" )\n'.format( path = de.SCRIPT_FOL )
    file_content = file_content +    'import definitions as de\n'
    file_content = file_content +    'reload(de)\n'
    file_content = file_content +    'sys.path.append( de.PY2_PACKAGES )\n'
    file_content = file_content +    'import requests\n'
    file_content = file_content +    'from requests.auth import HTTPBasicAuth\n'
    file_content = file_content +    'import json\n'
    file_content = file_content +    '%s = []\n' %de.ls_ji_result
    file_content = file_content +    'erro_ls = []\n'
    file_content = file_content +     line  + '\n'
    if if_result:
        file_content = file_content + de.dicc_ji_result +' = {}\n'
        file_content = file_content + de.dicc_ji_result + '["'+ de.ls_ji_result +'"] = '+ de.ls_ji_result+'\n'
        file_content = file_content + de.dicc_ji_result + '["'+ de.key_errors +'"] = erro_ls\n'
        file_content = file_content +'json_object = json.dumps( {dicc_ji_result}, indent = 2 )\n'.format( dicc_ji_result = de.dicc_ji_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content

def write_goo_sheet_request( line, if_result, result_fi_na , GOOGLE_SHET_DATA_NA , sheet_num ):
    """Specific Jira command, will be the content on a python file made with python requests.
        not possible to run Jira commands when you launch Maya with Gearbox launcher.
    Args:
        line ([str]): [code line to insert on script]
        if_result ([Bool]): [if is able a return ending lines]
        result_fi_na ([str]): [name of file saved with the return result]
    Returns:
        [str]: [python script command content formated]
    """
    file_content =                'import sys\n'
    file_content = file_content + 'import json\n'
    file_content = file_content + 'sys.path.append( "%s")\n' %de.SCRIPT_FOL
    file_content = file_content +'for path in sys.path:\n'
    file_content = file_content +'    if "Maya2020" in path or "Maya2021" in path or "Maya2022" in path or "Maya2023" in path:\n'
    file_content = file_content +'        sys.path.remove(path)\n'
    file_content = file_content + 'import definitions as de\n'
    file_content = file_content + 'reload( de )\n'
    file_content = file_content + 'sys.path.append( de.PY_PACK_MOD )\n'
    file_content = file_content + 'sys.path.append( de.PY2_PACKAGES )\n'
    file_content = file_content + 'import py2.oauth2client.service_account as ServiceAcc\n'
    file_content = file_content + 'import gspread\n'
    file_content = file_content + 'scope = [ "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets" ,\n'
    file_content = file_content + '    "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"  ]\n'
    file_content = file_content + 'creds = ServiceAcc.ServiceAccountCredentials.from_json_keyfile_name( de.PY2_PACKAGES.replace("\\\\","/") + "/creds/creds.json" , scope)\n'
    file_content = file_content + 'error_ls = []\n'
    file_content = file_content + '%s = []\n' %de.ls_result
    file_content = file_content + 'try:\n'
    file_content = file_content + '    client = gspread.authorize (creds)\n'
    file_content = file_content + '    sheetLs = client.openall( "%s" )\n' %( GOOGLE_SHET_DATA_NA )
    file_content = file_content + '    for she in sheetLs:\n'
    file_content = file_content + '        worksheets = she.worksheets()\n'
    file_content = file_content + '        for sheet in worksheets:\n'
    file_content = file_content + '           if "%s" in str(sheet):\n'%(sheet_num)
    file_content = file_content + '                ' +  line  + '\n'
    file_content = file_content + 'except Exception as err:\n'
    file_content = file_content + '    error_ls = ["G Sheet Error"]\n'
    file_content = file_content + '    error_ls.append(err)\n'
    file_content = file_content + '    print( err )\n'
    if if_result:
        file_content = file_content + de.dicc_result +' = {}\n'
        file_content = file_content + de.dicc_result + '["'+ de.ls_result +'"] = ' + de.ls_result+'\n'
        file_content = file_content + de.dicc_result + '["'+ de.key_errors +'"] = str(error_ls)\n'
        file_content = file_content +'json_object = json.dumps( {dicc_result}, indent = 2 )\n'.format( dicc_result = de.dicc_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content

def write_down_tools():
    """Specific Google Drive command, will be the content on a python file.
        not possible to run Google Drive commands when you launch Maya with Gearbox launcher.
    Returns:
        [str]: [python script command content formated]
    """
    file_content =                'import sys\n'
    file_content = file_content + 'sys.path.append( "%s")\n' %de.SCRIPT_FOL

    file_content = file_content +'for path in sys.path:\n'
    file_content = file_content +'    if "Maya2020" in path or "Maya2021" in path or "Maya2022" in path or "Maya2023" in path:\n'
    file_content = file_content +'        sys.path.remove(path)\n'
    
    file_content = file_content + 'import google_sheet_request as gs\n'
    file_content = file_content + 'reload( gs )\n'
    file_content = file_content + 'goo_dri = gs.GoogleDriveQuery()\n'
    file_content = file_content + 'goo_dri.update_tools()\n'
    return file_content

def create_python_file( python_file_na, python_file_content ):
    """Jus create python file with a given content
    Args:
        python_file_na ([str]): [python file name]
        python_file_content ([str]): [script content]
    """
    with open( de.PY_PATH + python_file_na + ".py", "w") as fileFa:
        fileFa.write( python_file_content )
        fileFa.close()
        
def set_logged_data_on_combo( comboB, data2check):
    """Set previus selected item on this particular combobox.
    Args:
        comboB ([qcombobox]): [combobox needed for]
        data2check ([str]): [the text value you wanted to combobox get focus on]
    """
    combo_item_ls = [comboB.itemText(i) for i in range(comboB.count())]
    for idx, item in enumerate ( combo_item_ls ):
        if str(data2check) == str(item):
            comboB.setCurrentIndex(idx)
            break