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
#import task_creation_panel as tc
try:
    reload(gs)
    reload(jq)
    reload(de)
    reload(hlp)
    reload(ev)
    reload(pr)
    #reload(tc)
except Exception:
    importlib.reload(gs)
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
    importlib.reload(ev)
    importlib.reload(pr) 
    #importlib.reload(tc) 

class AnimSubPath( QMainWindow ):
    def __init__( self, anim_na = '' , area = '' , anim_asset = '' ):
        super(AnimSubPath, self).__init__( )
        loader = QUiLoader()
        uifile = QtCore.QFile( de.SCRIPT_FOL.replace('\\','/') +'/'+ de.ANIM_PATH_TREE_UI)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load( uifile, ev.getWindow( QWidget ) )
        self.anim_na = anim_na
        self.area = area
        self.anim_asset = anim_asset
        self.initialize()

    def initialize(self):
        """Initializing functions, var and features.
        """
        #self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = hlp.load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = hlp.load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = hlp.load_root_vars()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        anim_root = hlp.solve_path( 'depot' , 'Anim_Root' , '' ,  self.DEPOT_ROOT, '' ,  self.PROJ_SETTINGS )
        self.ui.lineEdit_anim_root.setText( anim_root )
        self.load_first_qwlist(  self.ui.listWid_lavel1, 0 )
        self.ui.listWid_lavel1.currentItemChanged.connect( lambda: self.load_first_qwlist( self.ui.listWid_lavel2 , 1 ))
        self.ui.listWid_lavel2.currentItemChanged.connect( lambda: self.load_first_qwlist( self.ui.listWid_lavel3 , 2 ))
        self.ui.listWid_lavel3.currentItemChanged.connect( lambda: self.load_first_qwlist( self.ui.listWid_lavel4 , 3 ))
        self.ui.listWid_lavel4.currentItemChanged.connect( lambda: self.load_first_qwlist( self.ui.listWid_lavel4 , 4 ))
        self.ui.pushBut_create_new_folder.clicked.connect( lambda: self.pushBut_create_new_folder_action() )
        self.ui.pushBut_set_this_path.clicked.connect( lambda: self.done())
        
    def load_first_qwlist(self, target_list_widget , signal):
        path_root = hlp.solve_path( 'depot' , 'Anim_Root' , '' ,  self.DEPOT_ROOT, '' ,  self.PROJ_SETTINGS )
        subpaths = self.generate_subpaths( signal )
        perf = pr.PerforceRequests()
        dicc = perf.get_fol_fi_on_folder( 'dirs' ,path_root + subpaths, True, self.PERF_SERVER , self.PERF_USER , self.PERF_WORKSPACE )
        if dicc[de.key_errors] == '[]':
            folder_ls = dicc[de.ls_result]
            for item in folder_ls:
                target_list_widget.addItem( item['dir'].split('/')[-1] )
            self.get_final_path ( subpaths , self.anim_na)
        else:
            QMessageBox.information(self, u'getting folders perf error.', str( dicc[de.key_errors] )  )

    def generate_subpaths(self, signal):
        if signal != 0:
            try:
                if signal == 1:
                    sub1 = str( self.ui.listWid_lavel1.currentItem().text() )
                    subpaths =  sub1 + '/'
                    self.ui.listWid_lavel2.clear()
                    self.ui.listWid_lavel3.clear()
                    self.ui.listWid_lavel4.clear()
                elif signal == 2:
                    sub1 = str( self.ui.listWid_lavel1.currentItem().text() )
                    sub2= str( self.ui.listWid_lavel2.currentItem().text() )
                    subpaths = sub1 + '/' + sub2 + '/'
                    self.ui.listWid_lavel3.clear()
                    self.ui.listWid_lavel4.clear()
                elif signal == 3:
                    sub1 = str( self.ui.listWid_lavel1.currentItem().text() )
                    sub2= str( self.ui.listWid_lavel2.currentItem().text() )
                    sub3= str( self.ui.listWid_lavel3.currentItem().text() )
                    subpaths =  sub1 + '/' + sub2 + '/' + sub3 + '/'
                    self.ui.listWid_lavel4.clear()
                elif signal == 4:
                    sub1 = str( self.ui.listWid_lavel1.currentItem().text() )
                    sub2= str( self.ui.listWid_lavel2.currentItem().text() )
                    sub3= str( self.ui.listWid_lavel3.currentItem().text() )
                    sub4= str( self.ui.listWid_lavel4.currentItem().text() )
                    subpaths =  sub1 + '/' + sub2 + '/' + sub3 + '/' + sub4 + '/'
            except Exception:
                subpaths = ''
        else:
            subpaths = ''
        return subpaths

    def get_final_path (self, subpaths , anim_na):
        dicc = { 'subpath': subpaths ,'anim_na': anim_na }
        anim_full_path_fileroot = hlp.solve_path( 'depot' , 'Anim_Path' , '' ,  self.DEPOT_ROOT, '' ,  self.PROJ_SETTINGS , dicc_ = dicc)
        self.ui.lab_final_anim_path.setText( anim_full_path_fileroot )
        self.ui.lab_final_anim_path.setStyleSheet("color: rgb( 0, 175 ,0 )")

    def pushBut_create_new_folder_action(self):
        text_folder = str( self.ui.lineEd_new_fol.text() )
        if self.ui.radioButt_level1.isChecked():
            self.ui.listWid_lavel1.addItem( text_folder )
        elif self.ui.radioButt_level2.isChecked():
            self.ui.listWid_lavel2.addItem( text_folder )
        elif self.ui.radioButt_level3.isChecked():
            self.ui.listWid_lavel3.addItem( text_folder )
        elif self.ui.radioButt_level4.isChecked():
            self.ui.listWid_lavel4.addItem( text_folder )
        else:
            QMessageBox.information(self, u'No radio button checked', 'Choose one radio button first. '  )

    def done( self ):
        item_area_full_path = str( self.ui.lab_final_anim_path.text() )
        type = 'anim'
        dicc = { 'anim_char' : self.anim_asset }
        anim_asset_fullpath = hlp.solve_path( 'local', 'AnimRigPath' , self.LOCAL_ROOT ,  '', '' ,  self.PROJ_SETTINGS , dicc_ = dicc)
        template_full_path = hlp.solve_path( 'local', 'AnimRigPath_template' , self.LOCAL_ROOT ,  '', '' ,  self.PROJ_SETTINGS )
        perf = pr.PerforceRequests()
        hlp.copy_and_submit( self, self.PROJ_SETTINGS, QMessageBox , perf ,  template_full_path ,
                                item_area_full_path , self.area , self.anim_na  , type , anim_asset_fullpath )
        self.ui.close()
        
if ev.ENVIROMENT == 'Windows':
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        widget = AnimSubPath()
        widget.ui.show()
        sys.exit(app.exec_())
        
        