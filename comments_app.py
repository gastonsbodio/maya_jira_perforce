import sys
import os
try:
    from PySide  import QtCore
    from PySide.QtGui import *
    from PySide.QtUiTools import QUiLoader
except Exception as err:
    from PySide2.QtUiTools import QUiLoader
    from PySide2 import QtCore
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
try:
    import importlib
except Exception:
    pass
import jira_queries as jq
import definitions as de
import helper as hlp
import enviroment as ev

try:
    reload(jq)
    reload(de)
    reload(hlp)
    reload(ev)
except Exception:
    importlib.reload(jq)
    importlib.reload(de)
    importlib.reload(hlp)
    importlib.reload(ev)

class CommentsApp( QMainWindow ):
    def __init__( self, mainApp = ev.getWindow( QWidget )  ,issue_key = '' , dicc_comment_ls = [] , area_ls = [] ,
                    item_na = '' , area = '' ):
        super(CommentsApp, self).__init__( )
        loader = QUiLoader()
        uifile = QtCore.QFile( de.SCRIPT_FOL.replace('\\','/') +'/'+ de.COMMENTS_UI)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load( uifile, mainApp )
        self.issue_key = issue_key
        self.area_ls = area_ls
        self.item_na = item_na
        self.area = area
        self.initialize()
        dicc_comment_ls = self.get_refreshes_comment_dicc(  area_ls )
        self.load_old_comments( dicc_comment_ls )
        self.ui.pushBut_refresh.clicked.connect( lambda: self.get_task_values( self.area_ls ) )

    def initialize(self):
        """Initializing functions, var and features.
        """
        self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = hlp.load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = hlp.load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = hlp.load_root_vars()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )

    def load_old_comments( self , dicc_comment_ls):
        self.ui.textBrow_comments.clear()
        for dicc in dicc_comment_ls:
            text_body = dicc[de.comment_body]
            author = dicc[de.comment_author]
            date = dicc[de.comment_date]
            self.ui.textBrow_comments.append( text_body )
            self.ui.textBrow_comments.append( '____________________________________________' )
            self.ui.textBrow_comments.append( author + '   ////   ' + date)
            self.ui.textBrow_comments.append( '-------------------------------------------------------' )
            self.ui.textBrow_comments.append( '-------------------------------------------------------' )
            
    def get_refreshes_comment_dicc( self , area_ls ):
        item_na_label = hlp.get_item_na_label(  self.area , self.PROJ_SETTINGS )
        tasks_ls_diccs = hlp.get_self_tasks( self, QMessageBox , area_ls )
        for task in tasks_ls_diccs:
            if task[ de.area ] == self.area and task[ item_na_label ] == self.item_na :
                dicc_comment_ls = task[ de.comments ]
                break
        return dicc_comment_ls 

    def get_task_values( self , area_ls ):
        dicc_comment_ls = self.get_refreshes_comment_dicc(  area_ls )
        self.load_old_comments( dicc_comment_ls )

    def add_comment( self,issue_key):
        comment_body = str(  self.ui.textEd_new_comment.toPlainText())
        if comment_body != '':
            self.jira_m.add_comment( de.JI_SERVER , self.USER, self.APIKEY, issue_key , comment_body )


if ev.ENVIROMENT == 'Windows':
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        widget = CommentsApp()
        widget.ui.show()
        sys.exit(app.exec_())
        
        