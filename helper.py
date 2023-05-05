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
    else:
        print('no json file found')
    return dicc

def get_yaml_fil_data(path):
    """Read a yaml metadata file and return a dicc
    Args:
        path ([str]): [given yamel file path]
    Returns:
        [dicc]: [description]
    """
    data = {}
    with open(path , "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        stream.close()
    return data

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


def solve_path( is_local, asset_na, key_path, 
            local_root, depot_root, proj_settings ):
    """Retrun local desire path or depot path depending is_local value.
    Args:
        is_local (bool): [value]
        asset_na ([str]): [asset name]
        key_path ([str]): [dicc key built in __settintgs__]
    Returns:
        [str]: [dep path or local path depending is_local value]
    """
    if is_local:
        return local_root + proj_settings['Paths'][key_path].format(char_na = asset_na) 
    else:
        return depot_root + proj_settings['Paths'][key_path].format(char_na = asset_na)

def run_py_stand_alone( python_file_na ):
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
    subprocess.call( [r'%sExecute_%s.bat'%( de.PY_PATH , python_file_na ) ] , startupinfo=si)

def write_perforce_command_file ( line, if_result, result_fi_na):
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
    file_content = file_content + 'sys.path.append( "%s" )\n' %de.PY2_PACKAGES
    file_content = file_content + 'from P4 import P4,P4Exception \n' 
    file_content = file_content + 'import json\n'  
    file_content = file_content + 'p4 = P4() \n'
    file_content = file_content + 'error_ls = [] \n'
    file_content = file_content + '%s = [] \n' %de.ls_result
    file_content = file_content + 'try:\n'
    file_content = file_content + '    p4.connect()\n'
    file_content = file_content + line +'\n'
    file_content = file_content + '    p4.disconnect()\n' 
    file_content = file_content + 'except P4Exception:\n'
    file_content = file_content + '    for e in p4.errors:\n'
    file_content = file_content + '        error_ls.append(str(e))\n'
    if if_result:
        file_content = file_content + de.dicc_result +' = {}\n'
        file_content = file_content + de.dicc_result + '["'+ de.ls_result +'"] = '+ de.ls_result+'\n'
        file_content = file_content + de.dicc_result + '["'+ de.key_errors +'"] = error_ls\n'
        file_content = file_content +'json_object = json.dumps( {dicc_result}, indent = 2 )\n'.format( dicc_result = de.dicc_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content

def write_jira_command_file( line, if_result, result_fi_na , user , server, apikey ):
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
    file_content = file_content +    'reload(de)\n'
    file_content = file_content +    'sys.path.append( de.PY2_PACKAGES )\n'
    file_content = file_content +    'from jira import JIRA\n'
    file_content = file_content +    'import requests\n'
    file_content = file_content +    'from requests.auth import HTTPBasicAuth\n'
    file_content = file_content +    'import json\n'
    file_content = file_content +    'options = {"server": "%s" }\n'%( server )
    file_content = file_content +    'try:\n'
    file_content = file_content +    '    jira =  JIRA(options, basic_auth=( "%s", "%s" ))\n'%( user, apikey )
    file_content = file_content +    '    %s = True \n'%( de.key_connected )
    file_content = file_content +    'except Exception:\n    %s = False\n' % de.key_connected
    file_content = file_content +     line  + '\n'
    if if_result:
        file_content = file_content + de.dicc_ji_result +' = {}\n'
        file_content = file_content + 'if %s :\n' %de.key_connected
        file_content = file_content + '    '+de.dicc_ji_result + '["'+ de.ls_ji_result +'"] = '+ de.ls_ji_result+'\n'
        file_content = file_content + 'else:\n    '+de.dicc_ji_result + '["'+ de.ls_ji_result +'"] = []\n'
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
    file_content = file_content +     line  + '\n'
    if if_result:
        file_content = file_content + de.dicc_ji_result +' = {}\n'
        file_content = file_content + de.dicc_ji_result + '["'+ de.ls_ji_result +'"] = '+ de.ls_ji_result+'\n'
        file_content = file_content +'json_object = json.dumps( {dicc_ji_result}, indent = 2 )\n'.format( dicc_ji_result = de.dicc_ji_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
    return file_content

def write_goo_sheet_request( line, if_result, result_fi_na ):
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
    file_content = file_content + 'sys.path.append( "%s")\n' %de.SCRIPT_FOL#.replace( "/" , "\\\\" )
    file_content = file_content + 'import definitions as de\n'
    file_content = file_content + 'try:\n'
    file_content = file_content + '	import importlib\n'
    file_content = file_content + 'except Exception:\n'
    file_content = file_content + '    pass\n'
    file_content = file_content + 'try:\n'
    file_content = file_content + '    reload( de )\n'
    file_content = file_content + 'except Exception:\n'
    file_content = file_content + '    importlib.reload(de)\n'
    file_content = file_content + 'sys.path.append( de.PY2_PACKAGES )\n'
    file_content = file_content + 'import oauth2client.service_account as ServiceAcc\n'
    file_content = file_content + 'import gspread\n'
    file_content = file_content + 'scope = [ "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets" ,\n'
    file_content = file_content + '    "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"  ]\n'
    file_content = file_content + 'creds = ServiceAcc.ServiceAccountCredentials.from_json_keyfile_name( de.PY2_PACKAGES.replace("\\\\","/") + "/creds/creds.json" , scope)\n'
    file_content = file_content + 'client = gspread.authorize (creds)\n'
    file_content = file_content + 'sheet = client.open( de.GOOGLE_SHET_DATA_NA ).sheet1\n'
    file_content = file_content +     line  + '\n'
    if if_result:
        file_content = file_content +'json_object = json.dumps( {dicc_ji_result}, indent = 2 )\n'.format( dicc_ji_result = de.dicc_ji_result ) 
        file_content = file_content + 'with open( "{path}", "w") as fileFa:\n'.format( path = de.PY_PATH + result_fi_na )
        file_content = file_content +'    fileFa.write( str(json_object) )\n'
        file_content = file_content +'    fileFa.close()\n'
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