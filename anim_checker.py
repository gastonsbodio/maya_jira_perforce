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
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.populate_table( self.ui.table_anim_check )
        self.get_all_anim_check_files()
        

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

    def  populate_table(self, table):
        """populate qtable with values.
        Args:
            table ([qtablewid]): [description]
        """
        table.clear()
        try:
            tasks_ls_diccs = self.get_google_doc_data( )
        except Exception as err:
            print (err)
            tasks_ls_diccs = []
        table.setRowCount = len( tasks_ls_diccs )
        for i, header in enumerate (de.CHECK_ANIM_LS):
            locals()["item"+ str(i)] = QTableWidgetItem(header)
            #locals()["item"+ str(i)].setBackground(QColor(180, 75, 65))
            table.setHorizontalHeaderItem( i,locals()["item"+ str(i)] )
        table.setColumnWidth( de.THUMB_IDX , de.width_as_thum )
        
        table.setColumnWidth( 0,  220 )
        table.setColumnWidth( 1,  40 )
        table.setColumnWidth( 2,  40 )
        table.setColumnWidth( 3,  40 )
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
                table.setItem(i ,idx, item)
                item.setTextAlignment(QtCore.Qt.AlignCenter)

    def get_all_anim_check_files(self):
        perf = pr.PerforceRequests()
        depot_path_root = hlp.solve_path( False, '', 'Anim_Check_Root' ,
                    self.LOCAL_ROOT, self.DEPOT_ROOT, self.PROJ_SETTINGS)
        dicc_fi = perf.get_all_dir_files( depot_path_root, self.PERF_SERVER , self.PERF_USER , self.PERF_WORKSPACE, return_ls = [], pyStAl = True )
        if dicc_fi[de.key_errors] == '[]':
            for fi in dicc_fi[de.ls_result] :
                print( fi['dir'])
        else:
            QMessageBox.information(self, u'gettingperf files error.', str( dicc_fi[de.key_errors] )  )

