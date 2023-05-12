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
import google_sheet_request as gs
import jira_queries as jq
import definitions as de
import helper as hlp
import enviroment as ev
try:
    reload(gs)
    reload(jq)
    reload(de)
    reload(hlp)
    reload(pr)
    reload(ev)
except Exception:
    importlib.reload(gs)
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
    importlib.reload(pr) 
    importlib.reload(ev) 

class TaskCreationPanel(QMainWindow):
    def __init__(self):
        super(TaskCreationPanel, self).__init__( )
        loader = QUiLoader()
        uifile = QtCore.QFile( de.SCRIPT_FOL.replace('\\','/') +'/'+ de.TASK_CREATION_UI)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load( uifile, ev.getWindow(QWidget) )
        self.initialize_widget_conn()

    def initialize_widget_conn(self):
        """Initializing functions, var and features.
        """
        self.get_master_creds()
        self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = hlp.load_jira_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = hlp.load_root_vars()
        self.load_project_combo()

        hlp.set_logged_data_on_combo( self.ui.comboB_projects, self.PROJECT_KEY)
        self.load_workspace_combo()
        hlp.set_logged_data_on_combo( self.ui.comboB_workSpace, self.PERF_WORKSPACE)
        self.set_roots()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.ui.comboB_projects.currentIndexChanged.connect(lambda: self.jira_combo_change_ac(1))
        self.ui.lineEd_jira_user.setText( self.USER )
        self.ui.pushBut_set_jira_user.clicked.connect(lambda: self.jira_combo_change_ac(2))
        self.ui.pushBut_set_apiK.clicked.connect(lambda: self.jira_combo_change_ac(3))

        self.ui.pushBut_set_user_per.clicked.connect(lambda: self.perf_combo_change_ac(1))
        self.ui.lineEd_perforce_user.setText( self.PERF_USER )
        self.ui.comboB_workSpace.currentIndexChanged.connect(lambda: self.perf_combo_change_ac(3))

        self.ui.actionGet_Jira_Api_Key.triggered.connect(self.get_api_token_help)

    def get_master_creds( self ):
        """initialize master jira credentials.
        """
        goo_sheet = gs.GoogleSheetRequests()
        self.MASTER_USER, self.MASTER_API_KEY = goo_sheet.get_master_credentials()

    def load_project_combo(self):
        """populate projects combob.
        """
        self.ui.comboB_projects.clear()
        dicc = self.jira_m.get_projects( de.SERVER , self.MASTER_USER, self.MASTER_API_KEY )
        if dicc[ de.key_errors ] != '[]':
            QMessageBox.information(self, u'Loading projects error.', str( dicc[de.key_errors] )  )
        for proj in ['None'] + dicc[ de.ls_ji_result ]:
            self.ui.comboB_projects.addItem(str(proj))

    def jira_combo_change_ac(self, signal):
        """ComboB or other widget action triggered when user changes values on Jira logging
        Args:
            signal ([int]): [number for distinguish witch particular widget change you want to work with]
        """
        dicc = hlp.json2dicc_load( de.TEMP_FOL+de.LOGIN_METADATA_FI_NA )
        if dicc!={}:
            self.USER , self.APIKEY, self.PROJECT_KEY = hlp.load_jira_vars()
        else:
            dicc['project'] = 'None'
            dicc['emailAddress'] = 'None'
            dicc['apikey'] = 'None'
        if signal == 1 :
            dicc['project'] = str( self.ui.comboB_projects.currentText() )
            self.PROJECT_KEY = dicc['project']
            self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        elif signal == 2:
            dicc['emailAddress'] = str( self.ui.lineEd_jira_user.text() )
            self.USER = dicc['emailAddress']
            self.ui.lineEd_jira_user.setText( self.USER )
            QMessageBox.information(self, u'', "Jira user email\n setting done"  )
        elif signal == 3:
            dicc['apikey'] = str(self.ui.lineEd_apiKey.text())
            self.APIKEY = str( dicc['apikey'] )
            self.ui.lineEd_apiKey.setText('')
            QMessageBox.information(self, u'', " Jira apikey\nsetting done"  )
        hlp.metadata_dicc2json( de.TEMP_FOL+de.LOGIN_METADATA_FI_NA , dicc)
        self.t_fea.populate_table( self.ui.table_assetsTasks)




