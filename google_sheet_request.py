import sys
import os
import definitions as de
import helper as hlp

try:
    import importlib
except Exception:
    pass
try:
    reload( de )
    reload( hlp )
except Exception:
    importlib.reload( de )
    importlib.reload( hlp )
    

sys.path.append( de.PY2_PACKAGES )
import pydrive
from pydrive import auth
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
        
class GoogleSheetRequests():
    def get_master_credentials( self ):
        """Get master user and pass for getting jira projects
        Returns:
            [dicc]: [dicc with master user and pass]
        """
        line = '%s  = sheet.get_all_records()\n' %de.dicc_ji_result
        file_content = hlp.write_goo_sheet_request ( line , True, 'google_sheet_query.json')
        hlp.create_python_file ( 'google_sheet_query', file_content )
        hlp.run_py_stand_alone( 'google_sheet_query' )
        dicc = hlp.json2dicc_load( de.PY_PATH  + 'google_sheet_query.json')
        os.remove( de.PY_PATH  + 'google_sheet_query.json' )
        os.remove( de.PY_PATH  + 'google_sheet_query.py' )
        return dicc
        

class GoogleDriveQuery():

    def login(self):
        gauth = GoogleAuth( )
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = de.PY2_PACKAGES.replace('\\','/') + "/creds/client_secrets.json"
        c = gauth.LoadCredentialsFile( de.PY2_PACKAGES.replace('\\','/')  + "/creds/mycreds.txt" )
        if gauth.credentials is None or c is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            try:
                gauth.Refresh()
            except Exception:
                gauth.Authorize(c)
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile( de.PY2_PACKAGES.replace('\\','/') + "/creds/mycreds.txt" )
        return GoogleDrive(gauth)

    def dowload_fi(self, googleFi, targuet_full_path):
        googleFi.GetContentFile( targuet_full_path )
        
    def listContentFold( self, credenciales, idFather ):
        query = " '%%%s%%' in parents and trashed=false"%(idFather)
        query = query.replace('%','')
        contentLs = credenciales.ListFile({'q':query}).GetList()
        return contentLs
        
    def list_goog_root_fol_fi( self, credentials ):
        #### para listar los folders o archivos raices
        top_list = credentials.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        return top_list

    def find_goo_tools_fol( self , credentials ):
        for goo_obj in self.list_goog_root_fol_fi( credentials ):
            for dicc_key in goo_obj:
                try:
                    if str( dicc_key ) == 'title' and str( goo_obj[ dicc_key ] ) == de.GOOG_CONTENT_TOOLS_FOL: 
                        return goo_obj
                except Exception:
                    pass
        return None
    
    def update_tools (self):
        credentials = self.login()
        goo_obj_tool_fol = self.find_goo_tools_fol(credentials)
        tool_fi_ls = self.listContentFold(  credentials , goo_obj_tool_fol['id'] )
        for goo_fi in tool_fi_ls:
            goo_fi.dowload_fi ( de.SCRIPT_FOL.replace('\\','/') + '/' + goo_fi['title']   )
            print ( ' downloading:      ' + goo_fi['title'] )
