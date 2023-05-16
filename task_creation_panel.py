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
    reload(ev)
except Exception:
    importlib.reload(gs)
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
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
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.load_assign_user_combo()
        self.load_issues_types_combo()
        self.load_area_combo()
        hlp.set_logged_data_on_combo( self.ui.comboB_issue_type, de.issue_type_asset)
        self.ui.pushBut_create_one_issue.clicked.connect( self.create_issue )

    def get_master_creds( self ):
        """initialize master jira credentials.
        """
        goo_sheet = gs.GoogleSheetRequests()
        self.MASTER_USER, self.MASTER_API_KEY = goo_sheet.get_master_credentials()

    def load_assign_user_combo(self):
        """populate assignable users combob.
        """
        self.ui.comboBuser_4_assign.clear()
        dicc = self.jira_m.get_assignable_users( de.SERVER ,self.PROJECT_KEY ,self.USER , self.APIKEY )
        for d in ['None'] + dicc:
        #if dicc[ de.key_errors ] != '[]':
        #    QMessageBox.information(self, u'Loading assignable users error.', str( dicc[de.key_errors] )  )
        #for proj in ['None'] + dicc[ de.ls_ji_result ]:
            try:
                self.ui.comboBuser_4_assign.addItem( str( d[ 'displayName' ].encode('utf-8') ) )
            except Exception:
                self.ui.comboBuser_4_assign.addItem( str( d ) )
            
    def load_issues_types_combo(self):
        """populate issues types combob.
        """
        self.ui.comboB_issue_type.clear()
        dicc = self.jira_m.get_issue_types( de.SERVER , self.PROJECT_KEY , self.USER , self.APIKEY )
        for d in dicc:
            self.ui.comboB_issue_type.addItem( str( d[ 'untranslatedName' ].encode('utf-8') ) )

    def load_area_combo(self):
        """populate area combob.
        """
        list_ = [     self.PROJ_SETTINGS ['KEYWORDS']['mod']   ,    self.PROJ_SETTINGS ['KEYWORDS']['rig']    ,
                    self.PROJ_SETTINGS ['KEYWORDS']['text']   ]
        self.ui.comboB_asset_area.clear()
        for item in list_:
            self.ui.comboB_asset_area.addItem( item )

    def create_issue( self ):
        """Creates a issue/task on jira  associated with the given arguments on the tool and creates local templates
        on this task.
        """
        area = str(self.ui.comboB_asset_area.currentText())
        asset_na = str(self.ui.lineEd_asset_na.text() )
        assign_name = str(self.ui.comboB_asset_area.currentText())
        issue_type = str(self.ui.comboB_issue_type.currentText())
        description = 'gaston test'
        summary = area + '  task  for: '+ asset_na
        self.jira_m.create_issue( self.USER, de.SERVER, self.APIKEY, self.PROJECT_KEY , summary , description, issue_type, assign_name )


