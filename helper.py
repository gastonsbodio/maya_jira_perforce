### common functions module
import sys
import json
import ast
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
import shutil

def make_read_writeable(filename):
    """set file as read-only false
    Args:
        filename ([str]): [description]
    """
    os.chmod(filename, stat.S_IWRITE)

def metadata_dicc2json( path, dicc ):
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

def fix_perf_mapped_root_path( path, proj_settings ):
    real_dp_fol_root = proj_settings['KEYWORDS']['real_depot_fol_root']
    mapped_dp_fol_root = proj_settings['KEYWORDS']['maped_depot_fol_root']
    local_fol_root = proj_settings['KEYWORDS']['local_fol_root']
    path_ = path.replace(    real_dp_fol_root+'/'+local_fol_root     ,   mapped_dp_fol_root    )
    return path_

def is_local_fi_mod( local_mod_date , gdrive_mod_date ):
    day_hour_ls = []
    key_ = False
    for day_hour in [local_mod_date , gdrive_mod_date ]:
        day = day_hour.split('T')[0]
        day = int(day.split('-')[0] + day.split('-')[1] + day.split('-')[2] )
        day_hour_ls.append( day )
        hour = day_hour.split('T')[-1]
        hour = int(hour.split(':')[0] + hour.split(':')[1] + hour.split(':')[2] )
        day_hour_ls.append( hour )
    if day_hour_ls[0] > day_hour_ls[2]:
        key_ = True
    elif day_hour_ls[0] == day_hour_ls[2]:
        if day_hour_ls[1] > day_hour_ls[3]:
            key_ = True
    return key_

def go_2_perf_root_path( path, proj_settings , depot_root ):
    real_dp_fol_root = proj_settings['KEYWORDS']['real_depot_fol_root']
    mapped_dp_fol_root = proj_settings['KEYWORDS']['maped_depot_fol_root']
    local_fol_root = proj_settings['KEYWORDS']['local_fol_root']
    path_ = path.replace(    '/'+local_fol_root+'/'  ,    '/'+mapped_dp_fol_root+'/'   )
    new_root = depot_root.split( '/'+real_dp_fol_root )[0]
    path_ = new_root+'/'+mapped_dp_fol_root+'/'+ path_.split( '/'+mapped_dp_fol_root+'/' )[-1]
    return path_

def go_2_local_root_path( path, proj_settings , local_root ):
    mapped_dp_fol_root = proj_settings['KEYWORDS']['maped_depot_fol_root']
    local_fol_root = proj_settings['KEYWORDS']['local_fol_root']
    path_ = path.replace(    '/'+mapped_dp_fol_root+'/'     ,   '/'+local_fol_root+'/'    )
    path_ = local_root+'/'+local_fol_root+'/'+ path_.split( '/'+local_fol_root+'/' )[-1]
    return path_

def solve_path( root_state, key_path, local_root,
                depot_root, git_root, proj_settings , dicc_ = {}):
    """Retrun local desire path or depot path depending is_local value.
    Args:
        root_state (str): ['local', 'depot', 'git']
        asset_na ([str]): [asset name]
        key_path ([str]): [dicc key built in __settintgs__]
    Returns:
        [str]: [dep path or local path depending is_local value]
    """
    if proj_settings['Paths'][ key_path ].format( **dicc_) != '': 
        if root_state == 'local':
            return local_root + proj_settings['Paths'][key_path].format(**dicc_)
        elif root_state == 'depot':
            depot_path = depot_root + proj_settings['Paths'][key_path].format(**dicc_)
            depot_path = fix_perf_mapped_root_path( depot_path , proj_settings )
            return depot_path
        elif root_state == 'git':
            return git_root + proj_settings['Paths'][key_path].format(**dicc_)
    else:
        return ''
    
def transform_given_path( path, way_key , proj_settings , local_root , depot_root ):
    if way_key == 'local':
        path = go_2_local_root_path( path, proj_settings ,local_root )
    elif way_key == 'depot':
        path = go_2_perf_root_path( path, proj_settings ,depot_root )
    return path

def only_name_out_extention( file_path , with_prefix = True, prefix = '' ):
    path, name = separate_path_and_na( file_path )
    file = name.split('.')[0]
    if with_prefix:
        if not file.startswith (prefix):
            file = prefix + file
    return file

def get_item_na_label(  area , PROJ_SETTINGS ):
    if area in PROJ_SETTINGS['List']['area_assets_ls']:
        item_na = de.asset_na
    elif area  in PROJ_SETTINGS['List']['area_anim_ls']:  
        item_na = de.ani_na
    return item_na

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
    file_content = file_content + '            if "%s" in str(sheet):\n'%(sheet_num)
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

def write_googld_func( func_na, result_fi_na, if_result):
    """Specific Google Drive command, will be the content on a python file.
        not possible to run Google Drive commands when you launch Maya with Gearbox launcher.
    Returns:
        [str]: [python script command content formated]
    """
    file_content =                'import sys\n'
    file_content = file_content + 'sys.path.append( "%s")\n' %de.SCRIPT_FOL
    file_content = file_content + 'import json\n'
    file_content = file_content +'for path in sys.path:\n'
    file_content = file_content +'    if "Maya2020" in path or "Maya2021" in path or "Maya2022" in path or "Maya2023" in path:\n'
    file_content = file_content +'        sys.path.remove(path)\n'

    file_content = file_content + 'error_ls = []\n'
    file_content = file_content + '%s = []\n' %de.ls_result
    file_content = file_content + 'try:\n'
    file_content = file_content + '    import google_sheet_request as gs\n'
    file_content = file_content + '    reload( gs )\n'
    file_content = file_content + '    goo_dri = gs.GoogleDriveQuery()\n'
    file_content = file_content + '    %s = goo_dri.%s\n' %( de.ls_result , func_na ) #update_tools

    file_content = file_content + 'except Exception as err:\n'
    file_content = file_content + '    error_ls = ["G Sheet Error"]\n'
    file_content = file_content + '    error_ls.append(err)\n'
    file_content = file_content + '    print( err )\n'
    if if_result:
        file_content = file_content + de.dicc_result +' = {}\n'
        file_content = file_content + de.dicc_result + '["'+ de.ls_result +'"] = '+ de.ls_result+'\n'
        file_content = file_content + de.dicc_result + '["'+ de.key_errors +'"] = error_ls\n'
        file_content = file_content +'json_object = json.dumps( {dicc_result}, indent = 2 )\n'.format( dicc_result = de.dicc_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content
    
    
    
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

def copy_local_asset_template(  target_path, source_path, target_name , source_name):
    if not os.path.exists ( target_path ):
        os.makedirs( target_path )
    shutil.copy2( os.path.join( source_path , source_name  ),
                        os.path.join( target_path , target_name ) )
    
def change_reference( PROJ_SETTINGS, full_file_path_2_replace , new_asset_file_rig_name):
    generic_asset_fileRig_pattern_na = str( PROJ_SETTINGS ['KEYWORDS']['asset_rig_template'] )
    generic_asset_name = str( PROJ_SETTINGS ['KEYWORDS']['asset_name_template'] )
    new_asset_name = new_asset_file_rig_name.split(   '_'+str( PROJ_SETTINGS ['KEYWORDS']['rig'] )  )[0]
    make_read_writeable( full_file_path_2_replace  )
    with open( full_file_path_2_replace , 'r') as fi:
        fiLinesLsStrings = fi.readlines()
        fi.close()
    edited_file_ls = []
    for line in fiLinesLsStrings:
        if generic_asset_fileRig_pattern_na in line :
            line = line.replace( generic_asset_fileRig_pattern_na , new_asset_file_rig_name )
        if generic_asset_name in line :
            line = line.replace( '/'+generic_asset_name+'/' , '/'+new_asset_name+'/' )
        edited_file_ls.append( line )
    with open( full_file_path_2_replace, "w") as fileFa:
        fileFa. writelines(edited_file_ls)
        fileFa.close()
        
def perf_task_submit( app, QMessageBox , perf , item_na, area, asset_rig_full_path, PERF_SERVER, PERF_USER, PERF_WORKSPACE):
    # 
    perf.checkout_file( asset_rig_full_path , PERF_SERVER, PERF_USER, PERF_WORKSPACE)
    make_read_writeable( asset_rig_full_path )
    comment = item_na + ' ' + area +' template created'
    dicc = perf.add_and_submit( asset_rig_full_path, comment , PERF_SERVER, PERF_USER, PERF_WORKSPACE )
    if dicc[de.key_errors] == '[]':
        print('Submmition Done')
    else:
        QMessageBox.information( app, u'submittion perf error.', str( dicc[de.key_errors] )  )

def check_template_exists(  app, QMessageBox, source_path , source_name , perf ):
    if True:#not os.path.exists ( os.path.join( source_path , source_name ) ):
        dicc = perf.pull_file_2_local( source_path + source_name , True , app.PERF_SERVER, app.PERF_USER, app.PERF_WORKSPACE )
        if dicc[de.key_errors] != '[]':
            QMessageBox.information( app, u'Downloading perforce error', str( dicc[de.key_errors] )  )

def copy_and_submit( app, PROJ_SETTINGS, QMessageBox , perf ,template_full_path , item_area_full_path 
                    , area, item_na  , type , anim_asset_fullpath ):
    if type == de.issue_type_asset:
        source_path , source_name = separate_path_and_na( template_full_path )
        target_path , target_name = separate_path_and_na( item_area_full_path )
    elif type == de.issue_type_anim:
        source_path , source_name = separate_path_and_na( template_full_path )
        target_path , target_name = separate_path_and_na( item_area_full_path )
        anim_asset_path , anim_asset_name = separate_path_and_na( anim_asset_fullpath )
        anim_asset_na = anim_asset_name.split('.')[0]
    if True:#else:
        if os.path.isfile( os.path.join(  target_path , target_name ) ):
            make_read_writeable( target_path + target_name  )
        check_template_exists(  app , QMessageBox , source_path , source_name , perf )
        copy_local_asset_template(  target_path, source_path, target_name , source_name )
        if str( PROJ_SETTINGS ['KEYWORDS']['anim'] ) == str( area ):
            change_reference(  PROJ_SETTINGS, item_area_full_path , anim_asset_na )
        perf_task_submit( app, QMessageBox, perf, item_na, area, target_path+target_name , app.PERF_SERVER, app.PERF_USER, app.PERF_WORKSPACE )

def set_new_values_on_sheet( app, gs , QMessageBox , area , column_ls , value_ls , row_idx ):
    if area == app.PROJ_SETTINGS ['KEYWORDS']['anim']:
        sheet_num = app.PROJECT_KEY+'_'+de.issue_type_anim
    else:
        sheet_num = app.PROJECT_KEY+'_'+de.issue_type_asset
    edit_google_sheet_cell( app, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , sheet_num,
                                                column_ls , value_ls , row_idx )
    
def check_forbiden_char( app, full_word_2_analize, QMessageBox):
    key_permission = True
    for char in full_word_2_analize:
        if char in de.FORBIDDEN_CHARS:
            key_permission = False
            QMessageBox.information(app, u'invalid character', "Please don't use characters on this list:\n" + str(de.FORBIDDEN_CHARS) )
            break
    return key_permission
        
def check_created_task( app , QMessageBox , gs, area, item_na ):
    if area == app.PROJ_SETTINGS ['KEYWORDS']['anim']:
        item_na_colum  = de.GOOGLE_SH_ANI_NA_COL 
        sheet_num = app.PROJECT_KEY+'_'+de.issue_type_anim
    else:
        item_na_colum  = de.GOOGLE_SH_ASS_NA_COL
        sheet_num = app.PROJECT_KEY+'_'+de.issue_type_asset
    item_tracked_ls_diccs = get_google_doc_data( app, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , sheet_num )
    area_done_dicc = {} 
    path_ls = []
    item_created_ls = [ item[ item_na_colum ] for item in item_tracked_ls_diccs ]
    row_idx = len( item_tracked_ls_diccs )
    row_idx_crea_templa = len( item_tracked_ls_diccs )
    key_permission = check_forbiden_char( app, item_na , QMessageBox )
    if key_permission:
        if item_na in item_created_ls:
            for idx, item in enumerate ( item_tracked_ls_diccs ):
                if item[ item_na_colum ] == item_na:
                    area_done_dicc = ast.literal_eval( item[ de.GOOGLE_SH_CREAT_AREA_COL ] )
                    if item[ de.GOOGLE_SH_CREAT_PATH ] != u'':
                        path_ls = ast.literal_eval( item[ de.GOOGLE_SH_CREAT_PATH ] )
                    if area in str(area_done_dicc):
                        key_permission = False
                        row_idx_crea_templa = idx
                        break
                    else:
                        row_idx = idx
                        row_idx_crea_templa = idx
                        break
    return key_permission , area_done_dicc, row_idx , path_ls, row_idx_crea_templa

def item_path_builder( app, item_na , area , anim_asset  ):
    projsett = app.PROJ_SETTINGS
    localr = app.LOCAL_ROOT
    dicc = { 'char_na' : item_na }
    anim_asset_fullpath = ''
    if str( projsett ['KEYWORDS']['rig'] ) == str( area ):
        type = de.issue_type_asset
        template_full_path = solve_path( 'local', 'RigTemplateMalePath' , localr,  '', '' ,  projsett)
        item_area_full_path = solve_path( 'local' , 'Rig_Char_Path' , localr ,  '', '' ,  projsett, dicc_ = dicc)
        item_depot_path = solve_path( 'depot' , 'Rig_Char_Path' , localr ,  app.DEPOT_ROOT, '' ,  projsett, dicc_ = dicc)
    elif str( projsett ['KEYWORDS']['mod'] ) == str( area ):
        type = de.issue_type_asset
        template_full_path = solve_path( 'local', 'ModTemplateMalePath' , localr,  '', '' ,  projsett)
        item_area_full_path = solve_path( 'local' , 'Mod_Char_Path' , localr ,  '', '' ,  projsett, dicc_ = dicc)
        item_depot_path = solve_path( 'depot' , 'Mod_Char_Path' , localr ,  app.DEPOT_ROOT, '' ,  projsett, dicc_ = dicc)
    elif str( projsett ['KEYWORDS']['anim'] ) == str( area ):
        type = de.issue_type_anim
        dicc = { 'anim_char' : anim_asset }
        anim_asset_fullpath = solve_path( 'local', 'AnimRigPath' , localr ,  '', '' ,  projsett , dicc_ = dicc)
        template_full_path = solve_path( 'local', 'AnimRigPath_template' , localr ,  '', '' ,  projsett )
        item_area_full_path = solve_path( 'local' , 'Anim_Root' , localr ,  '', '' ,  projsett )
        item_depot_path = solve_path( 'depot' , 'Anim_Root' , localr ,  app.DEPOT_ROOT, '' ,  projsett )
    return type, anim_asset_fullpath, template_full_path, item_area_full_path, item_depot_path

def get_area_path_from_path_ls (path_ls, area):
    if len(path_ls) == 1 :
        path = path_ls[0]
    elif len(path_ls) > 1 :
        for p in path_ls:
            if area in p:
                path = p
    elif len(path_ls) == 0 :
        path = ''
    return path

def define_main_item_vars( app, area , anim_asset, item_na , area_done_dicc  , path_ls ):
    type, anim_asset_fullpath, template_full_path, item_area_full_path , item_depot_path = item_path_builder( app, item_na , area , ''  ) #
    if area == app.PROJ_SETTINGS ['KEYWORDS']['anim']:
        item_na_prefix = de.ani_na
        item_depot_path = get_area_path_from_path_ls ( path_ls, area )
        if item_depot_path != '':
            label_ls = [ de.area+'_'+area  , item_na_prefix + '_' + item_na , de.item_path+'_'+item_depot_path , de.anim_char+'_'+anim_asset] 
        else:
            label_ls = [ de.area+'_'+area  , item_na_prefix + '_' + item_na  ,  de.anim_char+'_'+anim_asset] 
        goo_colum = [ de.GOOGLE_SH_ANI_NA_COL , de.GOOGLE_SH_CREAT_AREA_COL , de.GOOGLE_SH_CREAT_PATH  , de.GOOGLE_SH_ANIM_ASSET_COL ]
        value_ls =   [         item_na        ,           str(area_done_dicc)     ,          str(path_ls)        ,        anim_asset           ]
    else:
        if item_depot_path not in path_ls:
            path_ls.append( item_depot_path )
        item_na_prefix = de.asset_na
        label_ls = [ de.area+'_'+area  , item_na_prefix + '_' + item_na  , de.item_path+'_'+item_depot_path ] 
        goo_colum  = [ de.GOOGLE_SH_ASS_NA_COL ,  de.GOOGLE_SH_CREAT_AREA_COL ,  de.GOOGLE_SH_CREAT_PATH        ]
        value_ls =   [         item_na         ,        str(area_done_dicc)        ,          str(path_ls)               ]
    return label_ls , goo_colum , value_ls

def set_issue_label( app, QMessageBox , label_ls, issue_key, jira_m):
    for label in label_ls:
        dicc = jira_m.set_label( issue_key , label , app.USER , de.JI_SERVER , app.APIKEY  )
        if dicc[ de.key_errors ] != '[]':
            QMessageBox.information( app, u'Jira  setting tags labels Error.', str( dicc[de.key_errors] )  )
            return False
    return True

def jira_creation_task_issue( app ,QMessageBox ,issue_type ,assign_user_id , item_na , area , area_done_dicc , path_ls , anim_asset ):
    description = 'Jira Manager Tool'
    summary = area + '  task  for: '+ item_na
    dicc = app.jira_m.create_issue( app.USER, de.JI_SERVER, app.APIKEY, app.PROJECT_KEY , summary ,
                                        description, issue_type, app.USER )
    if dicc[ de.key_errors ] != '[]':
        QMessageBox.information( app, u'Jira  creating issue Error.', str( dicc[de.key_errors] )  )
    else:
        issue_key = dicc [ de.ls_ji_result ]
    area_done_dicc [ area ] =  issue_key
    dicc = app.jira_m.assign_2_user ( issue_key, assign_user_id, app.USER ,de.JI_SERVER , app.APIKEY )
    if dicc[ de.key_errors ] != []:
        QMessageBox.information( app, u'Jira  assigning user Error.', str( dicc[de.key_errors] )  )
    else:
        label_ls , goo_colum , value_ls = define_main_item_vars( app, area , anim_asset , item_na , area_done_dicc , path_ls )
        key = set_issue_label( app,  QMessageBox ,label_ls, issue_key  , app.jira_m)
        if key:
            return  goo_colum , value_ls

def get_self_tasks( app , QMessageBox , area_ls ):
    """Query Jira for get own assigned issues.
    Returns:
        [ls]: [list of jira issues]
    """
    if app.PROJECT_KEY != '' and app.PROJECT_KEY != 'None':
        if app.APIKEY != 'None' and app.USER != 'None':
            dicc = app.jira_m.get_custom_user_issues(app.USER, de.JI_SERVER, app.APIKEY, 'assignee', app.PROJECT_KEY , 'jira'  )
            if dicc[ de.key_errors ] != '[]':
                QMessageBox.information(app.main_widg, u'getting user task errors', str( dicc[de.key_errors] )  )
        filtered_tasks_ls = []
        for task_dicc in dicc[de.ls_ji_result]:
            if task_dicc[ de.area ] in area_ls:
                filtered_tasks_ls.append( task_dicc )
        return  filtered_tasks_ls
    else:
        return []