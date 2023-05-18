import sys
import os
import time
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
from PySide2.QtGui import *
from PySide2.QtWidgets import *
try:
	import importlib
except Exception:
    pass
import perforce_requests as pr
import google_sheet_request as gs
import jira_queries as jq
import definitions as de
import helper as hlp
import enviroment as ev
try:
    reload(pr)
    reload(gs)
    reload(jq)
    reload(de)
    reload(hlp)
    reload(ev)
except Exception:
    importlib.reload(pr)
    importlib.reload(gs)
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
    importlib.reload(ev) 

class AnimCheckerApp(QMainWindow):
    def __init__(self):
        super(AnimCheckerApp, self).__init__( )
        loader = QUiLoader()
        uifile = QtCore.QFile( de.SCRIPT_FOL.replace('\\','/') +'/'+ de.ANIM_CHECK_UI)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load( uifile, ev.getWindow( QWidget ) )
        self.initialize_widget_conn()

    def initialize_widget_conn(self):
        """Initializing functions, var and features.
        """
        #self.get_master_creds()
        self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = hlp.load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = hlp.load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = hlp.load_root_vars()
        self.GIT_ROOT = self.LOCAL_ROOT
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.load_table( self.ui.table_anim_check, 'populate' ) 
        self.ui.push_butt_start_check.clicked.connect( lambda: self.load_table( self.ui.table_anim_check, 'check' ) )
        

    #def get_master_creds( self ):
    #    """initialize master jira credentials.
    #    """
    #    goo_sheet = gs.GoogleSheetRequests()
    #    self.MASTER_USER, self.MASTER_API_KEY = goo_sheet.get_master_credentials()

    def get_google_doc_data( self ):
        """initialize master jira credentials.
        """
        goo_sheet = gs.GoogleSheetRequests()
        return goo_sheet.get_data_custom_google_sheet( de.GOOGLE_SHET_ANIM_CHECK )

    def set_table_columns(self, table):
        for i, header in enumerate (de.CHECK_ANIM_LS):
            locals()["item"+ str(i)] = QTableWidgetItem(header)
            #locals()["item"+ str(i)].setBackground(QColor(180, 75, 65))
            table.setHorizontalHeaderItem( i,locals()["item"+ str(i)] )
        table.setColumnWidth( de.THUMB_IDX , de.width_as_thum )
        table.setColumnWidth( 0,  200 )
        table.setColumnWidth( 1,  40 )
        table.setColumnWidth( 2,  40 )
        table.setColumnWidth( 3,  40 )

    def  load_table(self, table, type):
        """populate qtable with values.
        Args:
            table ([qtablewid]): [description]
        """
        table.clear()
        self.set_table_columns( self.ui.table_anim_check )
        if type == 'check':
            unreal_anim_fi_ls = self.list_unreal_files()
            for f in unreal_anim_fi_ls:
                print( f )
            try:
                table_anims, ma_files_ls, fbx_files_ls = self.get_all_anim_check_files()#self.get_google_doc_data( )
            except Exception as err:
                print (err)
                table_anims = []
                ma_files_ls = []
                fbx_files_ls = []
        try:
            tasks_ls_diccs = self.get_google_doc_data( )
        except Exception as err:
            print (err)
            tasks_ls_diccs = []
        table.setRowCount( len( tasks_ls_diccs ) )
        self.id_rows = {}
        for i, task in enumerate( tasks_ls_diccs ):
            table.setRowHeight( i, de.height_anim_ch_row )
            for idx, column in enumerate ( de.CHECK_ANIM_LS ):
                if column == de.anim:
                    item = QTableWidgetItem( str( task[ de.anim_check_colum_sheet_column]  ) )
                else:
                    item = QTableWidgetItem( '' )
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                    #checkB = QCheckBox( None )
                    #checkB.setParent( item )
                    if type == 'check':
                        table_anim = hlp.only_name_out_extention( task[ de.anim_check_colum_sheet_column ], with_prefix = True, prefix = 'AS_' )
                        if column == de.maya:
                            if table_anim in ma_files_ls :
                                item.setCheckState( QtCore.Qt.CheckState.Checked )
                        elif column == de.fbx:
                            if table_anim in fbx_files_ls :
                                item.setCheckState( QtCore.Qt.CheckState.Checked )
                        elif column == de.unreal:
                            if table_anim in unreal_anim_fi_ls :
                                item.setCheckState( QtCore.Qt.CheckState.Checked )
                table.setItem(i ,idx, item)
                #item.setTextAlignment(QtCore.Qt.AlignCenter)

    def get_all_anim_check_files(self):
        perf = pr.PerforceRequests()
        depot_path_root = hlp.solve_path( 'depot', '', 'Anim_Check_Root' , self.LOCAL_ROOT, 
                                self.DEPOT_ROOT,  self.GIT_ROOT,  self.PROJ_SETTINGS)
        dicc_fol = perf.get_all_dir_fol( depot_path_root, self.PERF_SERVER , self.PERF_USER ,
                                        self.PERF_WORKSPACE, return_ls = [], pyStAl = True )
        if dicc_fol[de.key_errors] == '[]':
            table_anim_ls = []
            return_ma_list = []
            return_fbx_list = []
            for depot_folder in dicc_fol[de.ls_result] :
                folder_ls = perf.get_fol_fi_on_folder( 'files' ,depot_folder, True, self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE )
                for file in folder_ls[de.ls_result]:
                    print( file['depotFile'] )
                    talbe_fi = hlp.only_name_out_extention( file['depotFile'] , with_prefix = False )
                    if talbe_fi not in table_anim_ls:
                        table_anim_ls.append(  talbe_fi  )
                    if file['depotFile'].endswith('.ma') or file['depotFile'].endswith('.mb'):
                        maya_fi = hlp.only_name_out_extention( file['depotFile'] , with_prefix = True, prefix = 'AS_' )
                        if maya_fi not in return_ma_list:
                            return_ma_list.append(  maya_fi )
                    if file['depotFile'].endswith('.fbx'):
                        fbx_fi = hlp.only_name_out_extention( file['depotFile'] , with_prefix = True, prefix = 'AS_' )
                        if fbx_fi not in return_fbx_list:
                            return_fbx_list.append( fbx_fi )
            return table_anim_ls, return_ma_list, return_fbx_list
        else:
            QMessageBox.information(self, u'getting perf folders error.', str( dicc_fol[de.key_errors] )  )
            return None

    def list_unreal_files( self ):
        unreal_root_anim_path = hlp.solve_path( 'git', '', 'Unreal_Anim_Root' , '', 
                                '',  self.GIT_ROOT,  self.PROJ_SETTINGS)
        unreal_fi_ls = []
        for pathhh, subdirs, files in os.walk( unreal_root_anim_path ):
            for fi in files:
                if fi.endswith('.uasset'):
                    un_fi = hlp.only_name_out_extention( fi , with_prefix = True, prefix = 'AS_' )
                    unreal_fi_ls.append( un_fi )
        return unreal_fi_ls
