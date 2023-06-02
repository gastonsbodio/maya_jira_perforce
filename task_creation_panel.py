import sys
import os
import time
import ast
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import shutil
try:
	import importlib
except Exception:
    pass
import google_sheet_request as gs
import jira_queries as jq
import definitions as de
import helper as hlp
import enviroment as ev
import perforce_requests as pr
try:
    reload(gs)
    reload(jq)
    reload(de)
    reload(hlp)
    reload(ev)
    reload(pr)
except Exception:
    importlib.reload(gs)
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
    importlib.reload(ev)
    importlib.reload(pr) 

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
        self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = hlp.load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = hlp.load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = hlp.load_root_vars()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.load_assign_user_combo()
        self.load_issues_types_combo()
        self.load_area_combo()
        self.load_combo_asset_na()
        hlp.set_logged_data_on_combo( self.ui.comboB_issue_type, de.issue_type_asset)
        self.ui.pushBut_create_one_issue.clicked.connect( self.create_issue )
        self.ui.pushBut_tag_issue.clicked.connect( self.tag_issue )

    def load_assign_user_combo(self):
        """populate assignable users combob.
        """
        self.ui.comboBuser_4_assign.clear()
        dicc = self.jira_m.get_assignable_users( de.JI_SERVER ,self.PROJECT_KEY ,self.USER , self.APIKEY )
        self.dicc_users_id = {}
        for d in ['None'] + dicc:
            try:
                self.ui.comboBuser_4_assign.addItem( str( d[ 'displayName' ].encode('utf-8') ) )
                self.dicc_users_id[ str( d[ 'displayName' ].encode('utf-8') ) ] = d[ 'accountId' ]
            except Exception:
                self.ui.comboBuser_4_assign.addItem( str( d ) )
            
    def load_issues_types_combo(self):
        """populate issues types combob.
        """
        self.ui.comboB_issue_type.clear()
        dicc = self.jira_m.get_issue_types( de.JI_SERVER , self.PROJECT_KEY , self.USER , self.APIKEY )
        for d in dicc:
            self.ui.comboB_issue_type.addItem( str( d[ 'untranslatedName' ].encode('utf-8') ) )

    def load_area_combo(self):
        """populate area combob.
        """
        list_ = [     self.PROJ_SETTINGS ['KEYWORDS']['mod']   ,    self.PROJ_SETTINGS ['KEYWORDS']['rig']    ,
                    self.PROJ_SETTINGS ['KEYWORDS']['text']   ]
        self.ui.comboB_asset_area_tag.clear()
        self.ui.comboB_asset_area.clear()
        for item in list_:
            self.ui.comboB_asset_area_tag.addItem( item )
            self.ui.comboB_asset_area.addItem( item )

    def load_combo_asset_na( self ):
        asset_tracked_ls_diccs = hlp.get_google_doc_data( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , self.PROJECT_KEY )
        asset_ls =[ asset[de.GOOGLE_SH_ASS_NA_COL] for  asset in  asset_tracked_ls_diccs ]
        self.ui.comboB_asset_names.clear()
        for item in asset_ls:
            self.ui.comboB_asset_names.addItem( item )

    def create_issue( self ):
        """Creates a issue/task on jira  associated with the given arguments on the tool and creates local templates
        on this task.
        """
        area = str(self.ui.comboB_asset_area.currentText())
        asset_na = str(self.ui.lineEd_asset_na.text() )
        key_permission , area_done_dicc , row_idx = self.check_created_task( area, asset_na )
        if key_permission:
            assign_name = str(self.ui.comboBuser_4_assign.currentText())
            assign_user_id = self.dicc_users_id [ assign_name ]
            issue_key = self.jira_creation_task_issue( assign_user_id , asset_na , area  )
            area_done_dicc [ area ] = issue_key
            if str( self.PROJ_SETTINGS ['KEYWORDS']['rig'] ) == str( area ):
                template_full_path = hlp.solve_path( 'local', '', 'RigTemplateMalePath' , self.LOCAL_ROOT,  '', '' ,  self.PROJ_SETTINGS)
                asset_area_full_path = hlp.solve_path( 'local', asset_na , 'Rig_Char_Path' , self.LOCAL_ROOT ,  '', '' ,  self.PROJ_SETTINGS)
            elif str( self.PROJ_SETTINGS ['KEYWORDS']['mod'] ) == str( area ):
                template_full_path = hlp.solve_path( 'local', '', 'ModTemplateMalePath' , self.LOCAL_ROOT,  '', '' ,  self.PROJ_SETTINGS)
                asset_area_full_path = hlp.solve_path( 'local', asset_na , 'Mod_Char_Path' , self.LOCAL_ROOT ,  '', '' ,  self.PROJ_SETTINGS)
            if template_full_path != '':
                source_path , source_name = hlp.separate_path_and_na( template_full_path )
            else:
                source_path , source_name = ('','')
            target_path , target_name = hlp.separate_path_and_na( asset_area_full_path )
            self.copy_local_asset_template(  target_path, source_path, target_name , source_name )
            self.perf_task_submit( asset_na, area, target_path+target_name )
            self.set_new_values_on_sheet( asset_na, area_done_dicc , row_idx )
        else:
            QMessageBox.information(self, u'Task already created', asset_na + ' ' + area )


    def set_new_values_on_sheet( self, asset_na, area_done_dicc , row_idx ):
        column_ls = [ de.GOOGLE_SH_ASS_NA_COL , de.GOOGLE_SH_CREAT_AREA_COL  ]
        value_ls  = [         asset_na,             str(area_done_dicc)      ]
        hlp.edit_google_sheet_cell( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , self.PROJECT_KEY ,
                                                column_ls , value_ls , row_idx )


    def jira_creation_task_issue( self , assign_user_id , asset_na , area  ):
        issue_type = str( self.ui.comboB_issue_type.currentText() )
        description = 'Jira Manager Tool'
        summary = area + '  task  for: '+ asset_na
        issue_key = self.jira_m.create_issue( self.USER, de.JI_SERVER, self.APIKEY, self.PROJECT_KEY , summary , description, issue_type, self.USER )
        self.jira_m.assign_2_user ( issue_key, assign_user_id, self.USER ,de.JI_SERVER , self.APIKEY)
        self.set_issue_label( area, asset_na, str( issue_key.key ) )
        return str( issue_key.key )

    def set_issue_label( self, area, asset_na, issue_key):
        for label in [ de.area+'_'+area  , de.asset_na+'_'+asset_na ]:
            self.jira_m.set_label( issue_key , label , self.USER , de.JI_SERVER , self.APIKEY  )

    def copy_local_asset_template( self, target_path, source_path, target_name , source_name):
        if not os.path.exists ( target_path ):
            os.makedirs( target_path )
        if source_path != '':
            shutil.copy2( os.path.join( source_path , source_name  ),
                            os.path.join( target_path , target_name ) )
        else:
            ev.create_empty_task( target_path + target_name  )
            
    def perf_task_submit(self, asset_na, area, asset_rig_full_path):
        perf = pr.PerforceRequests()
        perf.checkout_file( asset_rig_full_path , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE)
        hlp.make_read_write( asset_rig_full_path )
        comment = asset_na + ' ' + area +' template created'
        dicc = perf.add_and_submit( asset_rig_full_path, comment , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE )

    def check_created_task( self , area, asset_na):
        asset_tracked_ls_diccs = hlp.get_google_doc_data( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , self.PROJECT_KEY )
        key_permission = True
        area_done_dicc = {}
        asset_created_ls = [ asset[ de.GOOGLE_SH_ASS_NA_COL ] for asset in asset_tracked_ls_diccs ]
        row_idx = len( asset_tracked_ls_diccs )
        for char in asset_na:
            if char in de.FORBIDDEN_CHARS:
                key_permission = False
                QMessageBox.information(self, u'invalid character', "Please don't use characters on this list:\n" + str(de.FORBIDDEN_CHARS) )
                break
        if key_permission:
            if asset_na in asset_created_ls:
                for idx, asset in enumerate ( asset_tracked_ls_diccs ):
                    if asset[ de.GOOGLE_SH_ASS_NA_COL ] == asset_na:
                        area_done_dicc = ast.literal_eval( asset[ de.GOOGLE_SH_CREAT_AREA_COL ] )
                        if area in str(area_done_dicc):
                            key_permission = False
                            break
                        else:
                            row_idx = idx
                            break
        return key_permission , area_done_dicc, row_idx

    def tag_issue(self):
        issue_key = str( self.ui.lineEd_issue_key.text() )
        asset_na = str( self.ui.comboB_asset_names.currentText() )
        area = str( self.ui.comboB_asset_area_tag.currentText() )
        key_permission , area_done_dicc , row_idx = self.check_created_task( area, asset_na )
        if key_permission:
            if ' ' not in issue_key:
                area_done_dicc[ area ] = issue_key
                self.set_issue_label( area, asset_na, issue_key )
                self.set_new_values_on_sheet( asset_na, area_done_dicc , row_idx )
            else:
                QMessageBox.information(self, u'Issue key error', 'Check you have not spaces on issue key text. ' )
        else:
            QMessageBox.information(self, u'Issue Tagged', 'Issue tagged on track sheet registers' )
