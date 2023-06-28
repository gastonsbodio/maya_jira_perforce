import sys
import os
import time
import ast
import webbrowser
try:
    from PySide  import QtCore
    from PySide.QtGui import *
    from PySide.QtUiTools import QUiLoader
except Exception as err:
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
import anim_subpath as asp
try:
    reload(gs)
    reload(jq)
    reload(de)
    reload(hlp)
    reload(ev)
    reload(pr)
    reload(asp)
except Exception:
    importlib.reload(gs)
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
    importlib.reload(ev)
    importlib.reload(pr)
    importlib.reload(asp) 

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
        self.get_google_asset_and_anims()
        self.load_combo_item_na( self.asset_tracked_ls_diccs, de.GOOGLE_SH_ASS_NA_COL, self.ui.comboB_asset_on_anim )
        self.load_combo_item_na( self.asset_tracked_ls_diccs, de.GOOGLE_SH_ASS_NA_COL, self.ui.comboB_item_names )
        self.load_combo_item_na( self.asset_tracked_ls_diccs, de.GOOGLE_SH_ASS_NA_COL, self.ui.comboB_asset_on_anim_tag )
        self.ui.radioBut_choose.clicked.connect(lambda:  self.radio_but_clic_action() )
        self.ui.radioBut_create.clicked.connect(lambda: self.radio_but_clic_action() )
        self.default_radio_states()
        self.ui.radioBut_choose.nextCheckState()
        hlp.set_logged_data_on_combo( self.ui.comboB_issue_type, de.issue_type_task )
        self.set_defualt_state_combo_anim_asset()
        self.set_deault_state_combo_anim_asset_tag( )
        self.ui.pushBut_create_one_issue.clicked.connect( lambda: self.create_full_task() )
        self.ui.pushBut_tag_issue.clicked.connect( lambda: self.tag_issue() )
        self.ui.pushBut_create_file_template.clicked.connect( lambda: self.create_template_but_action() )
        self.ui.comboB_item_area.currentIndexChanged.connect(lambda: self.issue_type_combo_change_action() )
        self.ui.comboB_item_area_tag.currentIndexChanged.connect(lambda: self.item_area_tag_combo_change_action() )
        self.ui.actionTrack_Sheet_View.triggered.connect( lambda:  self.get_track_sheet( )  )

    def get_track_sheet(self):
        """Browse help for get jira api token
        """
        link = de.TRACK_SHEET_ITEMS
        webbrowser.open(link, new=2) 

    def item_area_tag_combo_change_action(self):
        selection = str(self.ui.comboB_item_area_tag.currentText())
        if selection == self.PROJ_SETTINGS ['KEYWORDS']['anim']:
            self.load_combo_item_na( self.anim_tracked_ls_diccs, de.GOOGLE_SH_ANI_NA_COL, self.ui.comboB_item_names )
            self.ui.comboB_asset_on_anim_tag.setEnabled( True )
            self.ui.lab_asset_anim_tag.setEnabled( True )
        else:
            self.load_combo_item_na( self.asset_tracked_ls_diccs, de.GOOGLE_SH_ASS_NA_COL, self.ui.comboB_item_names )
            self.set_deault_state_combo_anim_asset_tag( )

    def set_deault_state_combo_anim_asset_tag( self ):
        self.ui.comboB_asset_on_anim_tag.setEnabled( False )
        self.ui.lab_asset_anim_tag.setEnabled( False )
        
    def set_defualt_state_combo_anim_asset(self):
        self.ui.comboB_asset_on_anim.setEnabled( False )
        self.ui.lab_asset_anim.setEnabled( False )

    def issue_type_combo_change_action(self):
        if str(self.ui.comboB_item_area.currentText()) == self.PROJ_SETTINGS ['KEYWORDS']['anim'] :
            self.ui.comboB_asset_on_anim.setEnabled( True )
            self.ui.lab_asset_anim.setEnabled( True )
        else:
            self.set_defualt_state_combo_anim_asset()
        
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
        #dicc = self.jira_m.get_issue_types( de.JI_SERVER , self.PROJECT_KEY , self.USER , self.APIKEY )
        for d in [ de.issue_type_task ]:#dicc:
            self.ui.comboB_issue_type.addItem( d )
            #self.ui.comboB_issue_type.addItem( str( d[ 'untranslatedName' ] ) ) #.encode('utf-8')

    def load_area_combo(self):
        """populate area combob.
        """
        list_ = [     self.PROJ_SETTINGS ['KEYWORDS']['mod']   ,    self.PROJ_SETTINGS ['KEYWORDS']['rig']    ,
                    self.PROJ_SETTINGS ['KEYWORDS']['text']    ,  self.PROJ_SETTINGS ['KEYWORDS']['anim']   ]
        self.ui.comboB_item_area_tag.clear()
        self.ui.comboB_item_area.clear()
        for item in list_:
            self.ui.comboB_item_area_tag.addItem( item )
            self.ui.comboB_item_area.addItem( item )

    def get_google_asset_and_anims(self):
        self.asset_tracked_ls_diccs = hlp.get_google_doc_data( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA ,
                                                        self.PROJECT_KEY+'_'+de.issue_type_asset )
        self.anim_tracked_ls_diccs = hlp.get_google_doc_data( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA ,
                                                        self.PROJECT_KEY+'_'+de.issue_type_anim )
        
    def load_combo_item_na( self , tracked_ls_diccs, goog_column, comboB ):
        item_ls =[ item[ goog_column ] for  item in  tracked_ls_diccs ]
        comboB.clear()
        for item in item_ls:
            comboB.addItem( item )

    def create_full_task( self ):
        """Creates a issue/task on jira  associated with the given arguments on the tool and creates local templates
        on this task.
        """
        area = str(self.ui.comboB_item_area.currentText())
        item_na = str(self.ui.lineEd_asset_na.text() )
        key_permission , area_done_dicc , row_idx , path_ls ,row_idx_crea_templa = hlp.check_created_task( self, QMessageBox, 
                                                                                                        gs ,area, item_na )
        if key_permission:
            assign_name = str(self.ui.comboBuser_4_assign.currentText())
            anim_asset = str(self.ui.comboB_asset_on_anim.currentText())
            assign_user_id = self.dicc_users_id [ assign_name ]
            if str( self.PROJ_SETTINGS ['KEYWORDS']['anim'] ) != str( area ):
                goo_colum , value_ls = hlp.jira_creation_task_issue( self, QMessageBox ,de.issue_type_task, assign_user_id , item_na , area , area_done_dicc , path_ls , anim_asset )
                item_area_path = self.create_template_and_submit( item_na , area , anim_asset , row_idx)
                hlp.set_new_values_on_sheet( self , gs , QMessageBox , area, goo_colum , value_ls, row_idx  )
                if item_area_path != None :
                    QMessageBox.information( self, u'Done', item_area_path + '   created!'  )
            else:
                self.execute_anim_sub_path( item_na , area , anim_asset, 'create_full_task', row_idx , path_ls , area_done_dicc, assign_user_id = assign_user_id )
        else:
            QMessageBox.information(self, u'No Creating', item_na + ' ' + area + '  is already created.')


    def get_asset_na_and_area(self):
        if self.ui.radioBut_choose.isChecked():
            asset_na = str( self.ui.comboB_item_names.currentText() )
        else:
            asset_na = str( self.ui.lineEd_new_asset_na.text() )
        area = str( self.ui.comboB_item_area_tag.currentText() )
        return asset_na, area

    def tag_issue(self):
        issue_key = str( self.ui.lineEd_issue_key.text() )
        item_na, area = self.get_asset_na_and_area()
        if area == self.PROJ_SETTINGS ['KEYWORDS']['anim']:
            anim_char = str(self.ui.comboB_asset_on_anim_tag.currentText())
        else:
            anim_char = ''
        key_permission , area_done_dicc , row_idx , path_ls , row_idx_crea_templa = hlp.check_created_task( self, QMessageBox,
                                                                                                        gs, area, item_na  )
        if key_permission:
            if ' ' not in issue_key:
                area_done_dicc[ area ] = issue_key
                label_ls , goo_colum , value_ls = hlp.define_main_item_vars( self, area , str(self.ui.comboB_asset_on_anim_tag.currentText()), item_na  , area_done_dicc , path_ls)
                hlp.set_issue_label( self,  QMessageBox ,label_ls, issue_key , self.jira_m )
                hlp.set_new_values_on_sheet(  self , gs, QMessageBox ,area, goo_colum , value_ls, row_idx  )
                QMessageBox.information(self, u'Done', 'Issue:  '+ issue_key +'   tagged. ' )
            else:
                QMessageBox.information(self, u'Issue key error', 'Check you have not spaces on issue key text. ' )
        else:
            QMessageBox.information(self, u'Issue Tagged', 'Issue tagged on track sheet registers' )

    def radio_but_clic_action(self):
        if self.ui.radioBut_choose.isChecked():
            self.default_radio_states()
        else:
            self.ui.label_choose_asset.setEnabled( False )
            self.ui.comboB_item_names.setEnabled( False )
            self.ui.label_ingest_asset.setEnabled( True )
            self.ui.lineEd_new_asset_na.setEnabled( True )
            
    def default_radio_states(self):
        self.ui.label_choose_asset.setEnabled( True )
        self.ui.comboB_item_names.setEnabled( True )
        self.ui.label_ingest_asset.setEnabled( False )
        self.ui.lineEd_new_asset_na.setEnabled( False )

    def create_template_and_submit( self, item_na , area , anim_asset , row_idx ):
        type, anim_asset_fullpath, template_full_path, item_area_full_path , item_depot_path = hlp.item_path_builder( self,  item_na , area , anim_asset  )
        if str( self.PROJ_SETTINGS ['KEYWORDS']['anim'] ) != str( area ):
            perf = pr.PerforceRequests()
            hlp.copy_and_submit( self, self.PROJ_SETTINGS, QMessageBox , perf ,  template_full_path , item_area_full_path , area ,
                                item_na  , type , anim_asset_fullpath )
            return item_area_full_path
        else:
            self.execute_anim_sub_path( item_na , area , anim_asset, 'create_temp', row_idx , [] ,{} )
            return None

    def create_template_but_action(self):
        anim_asset = str( self.ui.comboB_asset_on_anim_tag.currentText() )
        asset_na, area = self.get_asset_na_and_area()
        item_area_full_path = self.create_template_and_submit( asset_na, area , anim_asset , 'unknown')
        if item_area_full_path != None:
            QMessageBox.information( self, u'Done', item_area_full_path + '   template created!'  )
        
    def execute_anim_sub_path( self , anim_na , area , anim_asset , signal, row_idx, path_ls, area_done_dicc , assign_user_id = None  ):
        issue_key = str(self.ui.lineEd_issue_key.text())
        widget = asp.AnimSubPath( anim_na = anim_na , area = area , anim_asset = anim_asset , signal = signal, row_idx = row_idx ,
                                assign_user_id = assign_user_id ,  path_ls = path_ls, area_done_dicc = area_done_dicc, issue_key = issue_key)
        widget.ui.show()
        
if ev.ENVIROMENT == 'Windows':
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        widget = TaskCreationPanel()
        widget.ui.show()
        sys.exit(app.exec_())