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
if de.PY_PACK_MOD not in sys.path:
    sys.path.append( de.PY_PACK_MOD )
if de.PY2_PACKAGES not in sys.path:
    sys.path.append( de.PY2_PACKAGES )
#try:
import py2.pydrive
from py2.pydrive import auth
from py2.pydrive.auth import GoogleAuth
from py2.pydrive.drive import GoogleDrive
#except Exception as err:
#    print (err)
        
class GoogleSheetRequests():
    def get_master_credentials( self ):
        """Get master user and pass for getting jira projects
        Returns:
            [dicc]: [dicc with master user and pass]
        """
        line = '%s  = sheet.get_all_records()\n' %de.dicc_ji_result
        file_content = hlp.write_goo_sheet_request ( line , True, 'google_sheet_query.json', de.GOOGLE_SHET_DATA_NA )
        hlp.create_python_file ( 'google_sheet_query', file_content )
        hlp.run_py_stand_alone( 'google_sheet_query' )
        dicc = hlp.json2dicc_load( de.PY_PATH  + 'google_sheet_query.json')[0]
        os.remove( de.PY_PATH  + 'google_sheet_query.json' )
        os.remove( de.PY_PATH  + 'google_sheet_query.py' ) 
        os.remove( de.PY_PATH  + 'Execute_google_sheet_query.bat' )
        return dicc['master_user'], dicc['master_pass']
    
    def get_data_custom_google_sheet( self , google_sheet_doc_na):
        """Get data on custom google sheet
        Returns:
            [dicc]: [dicc with master user and pass]
        """
        line = '%s  = sheet.get_all_records()\n' %de.dicc_ji_result
        file_content = hlp.write_goo_sheet_request ( line , True, 'custom_google_doc.json', google_sheet_doc_na)
        hlp.create_python_file ( 'custom_google_doc', file_content )
        hlp.run_py_stand_alone( 'custom_google_doc' )
        dicc = hlp.json2dicc_load( de.PY_PATH  + 'custom_google_doc.json')
        return dicc

class GoogleDriveQuery():
    def login(self):
        """Creates a google drive object ( with the proper log in )able to do queries
        Returns:
            [type]: [description]
        """
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
        """Download to local a file, with the given google file object.
        Args:
            googleFi ([google file obj]): [description]
            targuet_full_path ([str]): [local target full path]
        """
        googleFi.GetContentFile( targuet_full_path )
        
    def listContentFold( self, credenciales, idFather , final_ls = []):
        """
        Args:
            credenciales ([google drive obj]): [given logged in google drive obj]
            idFather ([str]): [id code associated to a google file or folder]
        Returns:
            [ls]: [list of google files objects]
        """
        query = " '%%%s%%' in parents and trashed=false"%(idFather)
        query = query.replace('%','')
        contentLs = credenciales.ListFile({'q':query}).GetList()
        for file in contentLs:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                self.listContentFold( credenciales, file['id'] , final_ls = final_ls)
            else:
                final_ls.append( file )
        return final_ls
        
    def list_goog_root_fol_fi( self, credentials ):
        """List and return all files or folder on google drive top level.
        Args:
            credenciales ([google drive obj]): [given logged in google drive obj]
        Returns:
            [ls]: [list of google files objects]
        """
        top_list = credentials.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        return top_list

    def find_goo_tools_fol( self , credentials ):
        """it uses tools files content folder name to get this google folder obj.
        Args:
            credenciales ([google drive obj]): [given logged in google drive obj]
        Returns:
            [google folder obj]: [description]
        """
        for goo_obj in self.list_goog_root_fol_fi( credentials ):
            for dicc_key in goo_obj:
                try:
                    if str( dicc_key ) == 'title' and str( goo_obj[ dicc_key ] ) == de.GOOG_CONTENT_TOOLS_FOL: 
                        return goo_obj
                except Exception:
                    pass
        return None
    
    def update_tools (self):
        """log in list tool files and download them to local.
        """
        credentials = self.login()
        goo_obj_tool_fol = self.find_goo_tools_fol( credentials )
        tool_fi_ls = self.listContentFold(  credentials , goo_obj_tool_fol['id'] )
        if not os.path.exists( de.SCRIPT_FOL.replace('\\','/')  ):
            try:
                os.makedirs( de.SCRIPT_FOL.replace('\\','/') )
            except Exception:
                pass
        for goo_fi in tool_fi_ls:
            full_path_name = de.SCRIPT_FOL.replace('\\','/') + '/' + goo_fi['title'] 
            if '.cpython-39.py' in full_path_name:
                full_path_name = de.SCRIPT_FOL.replace('\\','/') +'/'+ de.PY3CACHE_FOL +'/'+ goo_fi['title'] 
            self.dowload_fi ( goo_fi, full_path_name  )
            print ( ' downloading:      ' + full_path_name )


    def shelf_butt_launch_update_tools():
        """is not a real function, it is just to preserve the code to call -update tools-
        """
        import sys
        import ctypes
        from ctypes.wintypes import MAX_PATH
        dll = ctypes.windll.shell32
        buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
        if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
            USER_DOC = buf.value
        SCRIPT_FOL = USER_DOC + "\\prod_manager\\jira_manager"
        sys.path.append( SCRIPT_FOL )
        import helper as hlp
        try:
            reload(hlp)
        except Exception:
            importlib.reload(hlp)
        file_content = hlp.write_down_tools ( )
        hlp.create_python_file ('update_tools', file_content)
        hlp.run_py_stand_alone( 'update_tools', True)