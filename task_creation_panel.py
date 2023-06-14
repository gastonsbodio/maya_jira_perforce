import sys
import os
import time
import ast
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
        hlp.set_logged_data_on_combo( self.ui.comboB_issue_type, de.issue_type_asset )
        self.set_defualt_state_combo_anim_asset()
        self.set_deault_state_combo_anim_asset_tag( )
        self.ui.pushBut_create_one_issue.clicked.connect( lambda: self.create_issue() )
        self.ui.pushBut_tag_issue.clicked.connect( lambda: self.tag_issue() )
        self.ui.pushBut_create_file_template.clicked.connect( lambda: self.create_template_but_action() )
        self.ui.comboB_issue_type.currentIndexChanged.connect(lambda: self.issue_type_combo_change_action() )
        self.ui.comboB_item_area_tag.currentIndexChanged.connect(lambda: self.item_area_tag_combo_change_action() )

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
        if str(self.ui.comboB_issue_type.currentText()) == de.issue_type_anim :
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
        for d in [ de.issue_type_asset , de.issue_type_anim ]:#dicc:
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


    def create_issue( self ):
        """Creates a issue/task on jira  associated with the given arguments on the tool and creates local templates
        on this task.
        """
        area = str(self.ui.comboB_item_area.currentText())
        item_na = str(self.ui.lineEd_asset_na.text() )
        key_permission , area_done_dicc , row_idx = self.check_created_task( area, item_na , '')
        if key_permission:
            assign_name = str(self.ui.comboBuser_4_assign.currentText())
            assign_user_id = self.dicc_users_id [ assign_name ]
            issue_key = self.jira_creation_task_issue( assign_user_id , item_na , area  )
            area_done_dicc [ area ] = issue_key
            self.create_template_and_submit( item_na , area )
            if area == self.PROJ_SETTINGS ['KEYWORDS']['anim']:
                anim_asset = str(self.ui.comboB_asset_on_anim.currentText())
                item_na_colum, created_area_col = (de.GOOGLE_SH_ANI_NA_COL , de.GOOGLE_SH_CREAT_AREA_COL )
                anim_asset_col_ls , anim_asset_ls = ([de.GOOGLE_SH_ANIM_ASSET_COL],[anim_asset])
            else:
                item_na_colum, created_area_col = (de.GOOGLE_SH_ASS_NA_COL , de.GOOGLE_SH_CREAT_AREA_COL )
                anim_asset_col_ls , anim_asset_ls = ([],[])
            self.set_new_values_on_sheet( item_na , area, area_done_dicc , row_idx , item_na_colum,
                                        created_area_col , anim_asset_col_ls , anim_asset_ls)
        else:
            QMessageBox.information(self, u'Task already created', item_na + ' ' + area )


    def set_new_values_on_sheet( self, asset_na, area, area_done_dicc , row_idx , item_na_colum,
                                created_area_col , anim_asset_col_ls , anim_asset_ls ):
        column_ls = [  item_na_colum  ,    created_area_col      ] + anim_asset_col_ls
        value_ls  = [      asset_na   ,   str(area_done_dicc)     ] + anim_asset_ls
        if area == self.PROJ_SETTINGS ['KEYWORDS']['anim']:
            sheet_num = self.PROJECT_KEY+'_'+de.issue_type_anim
        else:
            sheet_num = self.PROJECT_KEY+'_'+de.issue_type_asset
        hlp.edit_google_sheet_cell( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , sheet_num,
                                                column_ls , value_ls , row_idx )


    def jira_creation_task_issue( self , assign_user_id , item_na , area  ):
        issue_type = str( self.ui.comboB_issue_type.currentText() )
        description = 'Jira Manager Tool'
        summary = area + '  task  for: '+ item_na
        issue_key = self.jira_m.create_issue( self.USER, de.JI_SERVER, self.APIKEY, self.PROJECT_KEY , summary ,
                                            description, issue_type, self.USER )
        self.jira_m.assign_2_user ( issue_key, assign_user_id, self.USER ,de.JI_SERVER , self.APIKEY)
        if area == self.PROJ_SETTINGS ['KEYWORDS']['anim']:
            anim_char = str(self.ui.comboB_asset_on_anim.currentText())
            label_ls = [ de.area+'_'+area  , de.anim_na+'_'+item_na , de.anim_char+'_'+anim_char] 
        else:
            anim_char = ''
            label_ls = [ de.area+'_'+area  , de.asset_na+'_'+item_na  ] 
        self.set_issue_label( label_ls, str( issue_key.key ) )
        return str( issue_key.key.encode('utf-8') )

    def set_issue_label( self, label_ls, issue_key):
        for label in label_ls: #[ de.area+'_'+area  , de.asset_na+'_'+asset_na ]:
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
        if dicc[de.key_errors] == '[]':
            print('Submmition Done')
        else:
            QMessageBox.information(self, u'submittion perf error.', str( dicc[de.key_errors] )  )
        
        

    def check_created_task( self , area, item_na, anim_char):
        if area == self.PROJ_SETTINGS ['KEYWORDS']['anim']:
            item_na_colum  = de.GOOGLE_SH_ANI_NA_COL 
            sheet_num = self.PROJECT_KEY+'_'+de.issue_type_anim
        else:
            item_na_colum  = de.GOOGLE_SH_ASS_NA_COL
            sheet_num = self.PROJECT_KEY+'_'+de.issue_type_asset
        item_tracked_ls_diccs = hlp.get_google_doc_data( self, QMessageBox , gs , de.GOOGLE_SHET_DATA_NA , sheet_num )
        key_permission = True
        area_done_dicc = {} 
        item_created_ls = [ item[ item_na_colum ] for item in item_tracked_ls_diccs ]
        row_idx = len( item_tracked_ls_diccs )
        for char in item_na:
            if char in de.FORBIDDEN_CHARS:
                key_permission = False
                QMessageBox.information(self, u'invalid character', "Please don't use characters on this list:\n" + str(de.FORBIDDEN_CHARS) )
                break
        if key_permission:
            if item_na in item_created_ls:
                for idx, asset in enumerate ( item_tracked_ls_diccs ):
                    if asset[ item_na_colum ] == item_na:
                        area_done_dicc = ast.literal_eval( asset[ de.GOOGLE_SH_CREAT_AREA_COL ] )
                        if area in str(area_done_dicc):
                            key_permission = False
                            break
                        else:
                            row_idx = idx
                            break
        return key_permission , area_done_dicc, row_idx

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
            item_na_prefix = de.anim_na
        else:
            anim_char = ''
            item_na_prefix = de.asset_na
        key_permission , area_done_dicc , row_idx = self.check_created_task( area, item_na , anim_char )
        if key_permission:
            if ' ' not in issue_key:
                area_done_dicc[ area ] = issue_key
                if anim_char != '':
                    label_ls = [ de.area+'_'+area  , item_na_prefix+'_'+item_na , de.anim_char+'_'+anim_char] 
                    anim_asset = str(self.ui.comboB_asset_on_anim_tag.currentText())
                    item_na_colum, created_area_col = (de.GOOGLE_SH_ANI_NA_COL , de.GOOGLE_SH_CREAT_AREA_COL )
                    anim_asset_col_ls , anim_asset_ls = ([de.GOOGLE_SH_ANIM_ASSET_COL],[anim_asset])
                else:
                    label_ls = [ de.area+'_'+area  , item_na_prefix+'_'+item_na ] 
                    item_na_colum, created_area_col = (de.GOOGLE_SH_ASS_NA_COL , de.GOOGLE_SH_CREAT_AREA_COL )
                    anim_asset_col_ls , anim_asset_ls = ([],[])
                self.set_issue_label( label_ls, issue_key )
                self.set_new_values_on_sheet( item_na , area, area_done_dicc , row_idx , item_na_colum,
                                        created_area_col , anim_asset_col_ls , anim_asset_ls)
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
        
    def create_template_and_submit(self, item_na, area , anim_asset, subpath=''):
        projsett = self.PROJ_SETTINGS
        localr = self.LOCAL_ROOT
        dicc = { 'char_na' : item_na }
        if str( projsett ['KEYWORDS']['rig'] ) == str( area ):
            type = 'asset'
            template_full_path = hlp.solve_path( 'local', 'RigTemplateMalePath' , localr,  '', '' ,  projsett)
            item_area_full_path = hlp.solve_path( 'local' , 'Rig_Char_Path' , localr ,  '', '' ,  projsett, dicc_key = dicc)
        elif str( projsett ['KEYWORDS']['mod'] ) == str( area ):
            type = 'asset'
            template_full_path = hlp.solve_path( 'local', 'ModTemplateMalePath' , localr,  '', '' ,  projsett)
            item_area_full_path = hlp.solve_path( 'local' , 'Mod_Char_Path' , localr ,  '', '' ,  projsett, dicc_key = dicc)
        elif str( projsett ['KEYWORDS']['anim'] ) == str( area ):
            type = 'anim'
            dicc = { 'anim_char' : anim_asset }
            template_full_path = hlp.solve_path( 'local', 'AnimRigPath' , localr ,  '', '' ,  projsett, dicc_key = dicc)
            item_area_full_path = hlp.solve_path( 'local' , 'Anim_Root' , localr ,  '', '' ,  projsett )
            self.execute_anim_sub_path( item_na )
        if type == 'asset':
            source_path , source_name = hlp.separate_path_and_na( template_full_path )
            target_path , target_name = hlp.separate_path_and_na( item_area_full_path )
        elif type == 'anim':
            print('')
        if not os.path.isfile( os.path.join(  source_path , source_name ) ):
            QMessageBox.information(self, u'PLease Get this file:  ' + source_path + source_name +'''\n
                                    from Perforce Depot.''')
        else:
            self.copy_local_asset_template(  target_path, source_path, target_name , source_name )
            self.perf_task_submit( item_na, area, target_path+target_name )
        
    def create_template_but_action(self):
        asset_na, area = self.get_asset_na_and_area()
        self.create_template_and_submit( asset_na, area )
        
    def execute_anim_sub_path( self, anim_na ):
        widget = asp.AnimSubPath( anim_na = anim_na )
        widget.ui.show()
        
if ev.ENVIROMENT == 'Windows':
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        widget = TaskCreationPanel()
        widget.ui.show()
        sys.exit(app.exec_())