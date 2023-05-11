####          maya launch      ####
#import sys
#import ctypes
#from ctypes.wintypes import MAX_PATH
#dll = ctypes.windll.shell32
#buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
#if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
#	USER_DOC = buf.value
#SCRIPT_FOL = USER_DOC + "\\prod_manager\\jira_manager"
#sys.path.append(SCRIPT_FOL)
#
#try:
#	import importlib
#except Exception:
#    pass
#import jira_project_manager as jiraM
#try:
#	reload(jiraM)
#except Exception:
#    importlib.reload( jiraM )
#widget = jiraM.MyMainWindow()
#widget.ui.show()

import sys
import webbrowser
import os
import time
from threading import Thread
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
import perforce_requests as pr
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

class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__( ) # Call the inherited classes __init__ method
        loader = QUiLoader()
        uifile = QtCore.QFile( de.SCRIPT_FOL.replace('\\','/') +'/'+ de.MANAGE_PROD_UI)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load( uifile, ev.getWindow(QWidget) )
        self.initialize_widget_conn()

    def initialize_widget_conn(self):
        """Initializing functions, var and features.
        """
        self.get_master_creds()
        #procees = ThreadReturn(target=self.get_master_creds ) #, args=(, ))
        #procees.start()
        self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = load_root_vars()
        self.load_project_combo()
        #while procees.join() == None:
        #    time.sleep(0.2)
        self.set_logged_data_on_combo( self.ui.comboB_projects, self.PROJECT_KEY)
        self.load_workspace_combo()
        self.set_logged_data_on_combo( self.ui.comboB_workSpace, self.PERF_WORKSPACE)
        self.set_roots()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.ui.comboB_projects.currentIndexChanged.connect(lambda: self.jira_combo_change_ac(1))
        self.ui.lineEd_jira_user.setText( self.USER )
        self.ui.pushBut_set_jira_user.clicked.connect(lambda: self.jira_combo_change_ac(2))
        self.ui.pushBut_set_apiK.clicked.connect(lambda: self.jira_combo_change_ac(3))

        self.ui.pushBut_set_user_per.clicked.connect(lambda: self.perf_combo_change_ac(1))
        self.ui.lineEd_perforce_user.setText( self.PERF_USER )
        self.ui.comboB_workSpace.currentIndexChanged.connect(lambda: self.perf_combo_change_ac(3))

        self.t_fea = table_features( self )
        
        self.t_fea.populate_table( self.ui.table_assetsTasks)
        self.t_fea.initialized_features_table(self.ui.table_assetsTasks)
        self.t_fea.generate_menu_dicc()
        self.ui.pushBut_reload_tables.clicked.connect( self.t_fea.refresh_tables )
        self.ui.actionGet_Jira_Api_Key.triggered.connect(self.get_api_token_help)

    def get_master_creds( self ):
        """initialize master jira credentials.
        """
        goo_sheet = gs.GoogleSheetRequests()
        dicc = goo_sheet.get_master_credentials()[0]
        self.MASTER_USER = dicc['master_user']
        self.MASTER_API_KEY = dicc['master_pass']

    def get_api_token_help(self):
        """Browse help for get jira api token
        """
        link = de.JIRA_API_TOKEN_HELP
        webbrowser.open(link, new=2) 
            
    def load_project_combo(self):
        """populate projects combob.
        """
        self.ui.comboB_projects.clear()
        dicc = self.jira_m.get_projects( de.SERVER , self.MASTER_USER, self.MASTER_API_KEY )
        if dicc[ de.key_errors ] != '[]':
            QMessageBox.information(self, u'Loading projects error.', str( dicc[de.key_errors] )  )
        for proj in ['None'] + dicc[ de.ls_ji_result ]:
            self.ui.comboB_projects.addItem(str(proj))

    def set_roots(self):
        """instancing local root and depot root related with the choosen workspace.
        """
        dicc = {}
        for proj in self.worksp_ls:
            try:
                if str(proj['client']) == self.PERF_WORKSPACE:
                    self.LOCAL_ROOT = str(proj['Root']).replace('\\','/')
                    dicc['local_root'] = self.LOCAL_ROOT
                    self.DEPOT_ROOT = str(proj['Stream']).replace('\\','/')
                    dicc['depot_root'] = self.DEPOT_ROOT
                    break
            except:
                pass
        hlp.metadata_dicc2json( de.TEMP_FOL+de.ROOTS_METAD_FI_NA , dicc)


    def load_workspace_combo(self):
        """populate workspace combob.
        """
        self.ui.comboB_workSpace.clear()
        perf = pr.PerforceRequests()
        dicc = perf.workspaces_ls( True , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE)
        self.worksp_ls = dicc[de.ls_result]
        if dicc[de.key_errors] == '[]':
            for proj in ['None']+self.worksp_ls:
                try:
                    self.ui.comboB_workSpace.addItem(proj['client'])
                except:
                    pass
        else:
            QMessageBox.information(self, u'Loading perf workspaces error.', str( dicc[de.key_errors] )  )
            
    def jira_combo_change_ac(self, signal):
        """ComboB or other widget action triggered when user changes values on Jira logging
        Args:
            signal ([int]): [number for distinguish witch particular widget change you want to work with]
        """
        dicc = hlp.json2dicc_load( de.TEMP_FOL+de.LOGIN_METADATA_FI_NA )
        if dicc!={}:
            self.USER , self.APIKEY, self.PROJECT_KEY = load_jira_vars()
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

    def perf_combo_change_ac( self, signal ):
        """ComboB or other widget action triggered when user changes values perforce logging
        Args:
            signal ([int]): [number for distinguish witch particular widget change you want to work with]
        """
        dicc = hlp.json2dicc_load( de.TEMP_FOL+de.PERF_LOG_METADATA_FI_NA )
        if dicc =={}:
            dicc['perf_user'] = 'None'
            dicc['perf_server'] = 'None'
            dicc['perf_workspace'] = 'None'
        else:
            self.PERF_USER ,self.PERF_SERVER ,self.PERF_WORKSPACE = load_perf_vars()
        if signal == 1:
            dicc['perf_user'] = str(self.ui.lineEd_perforce_user.text() )
            self.PERF_USER = dicc['perf_user']

            dicc['perf_server'] = str(self.ui.lineEd_perforce_server.text() )
            self.PERF_SERVER = dicc['perf_server']
            QMessageBox.information(self, u'', "Perforce server and sser \n         setting done"  )
        elif signal == 3:
            dicc['perf_workspace'] = str(self.ui.comboB_workSpace.currentText())
            self.PERF_WORKSPACE = str( dicc['perf_workspace'] )
            self.set_roots()
        hlp.metadata_dicc2json( de.TEMP_FOL+de.PERF_LOG_METADATA_FI_NA , dicc)
        self.set_logged_data_on_combo( self.ui.comboB_workSpace, self.PERF_WORKSPACE)

    def set_logged_data_on_combo(self, comboB, data2check):
        """Set previus selected item on this particular combobox.
        Args:
            comboB ([qcombobox]): [combobox needed for]
            data2check ([str]): [the text value you wanted to combobox get focus on]
        """
        combo_item_ls = [comboB.itemText(i) for i in range(comboB.count())]
        for idx, item in enumerate ( combo_item_ls ):
            if str(data2check) == str(item):
                comboB.setCurrentIndex(idx)
                break

def load_jira_vars():
    """instancing loging vars for make it run Jira queries.
    """
    dicc = hlp.json2dicc_load( de.TEMP_FOL+de.LOGIN_METADATA_FI_NA )
    if dicc != {}:
        USER = str( dicc['emailAddress'] ) 
        APIKEY = str( dicc['apikey'] )
        PROJECT_KEY = str( dicc['project'] )
    else:
        USER = 'None'
        APIKEY = 'None'
        PROJECT_KEY = 'None'
    return  USER , APIKEY, PROJECT_KEY

def load_perf_vars():
    """instancing loging vars for make it run  Perforce queries.
    """    
    dicc = hlp.json2dicc_load( de.TEMP_FOL+de.PERF_LOG_METADATA_FI_NA )
    if dicc != {}:
        PERF_USER = str( dicc['perf_user'] ) #'user'])
        PERF_WORKSPACE = str( dicc['perf_workspace'] )
        PERF_SERVER = str( dicc['perf_server'] )
    else:
        PERF_USER = 'None'
        PERF_WORKSPACE = 'None'
        PERF_SERVER = 'None'
    return  PERF_USER ,PERF_SERVER ,PERF_WORKSPACE 

def load_root_vars():
    """instancing roots vars for path building.
    """    
    dicc = hlp.json2dicc_load( de.TEMP_FOL+de.ROOTS_METAD_FI_NA )
    if dicc != {}:
        LOCAL_ROOT = str( dicc['local_root'] )
        DEPOT_ROOT = str( dicc['depot_root'] )
    else:
        LOCAL_ROOT = 'None'
        DEPOT_ROOT = 'None'
    return  LOCAL_ROOT ,DEPOT_ROOT 

class table_features( ):#QWidget ):
    """All Table functionality
    """
    def __init__(self, main_widg = None):
        self.jira_m = jq.JiraQueries()
        self.USER , self.APIKEY, self.PROJECT_KEY  = load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = load_root_vars()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        self.main_widg = main_widg
    
    def get_self_tasks(self):
        """Query Jira for get own assigned issues.
        Returns:
            [ls]: [list of jira issues]
        """
        dicc = self.jira_m.get_custom_user_issues(self.USER, de.SERVER, self.APIKEY, 'assignee', self.PROJECT_KEY, self.APIKEY, 'jira' )
        if dicc[ de.key_errors ] != '[]':
            QMessageBox.information(self.main_widg, u'getting user task errors', str( dicc[de.key_errors] )  )
        return dicc[de.ls_ji_result]

    def  populate_table(self, table):
        """populate qtable with values.
        Args:
            table ([qtablewid]): [description]
        """
        self.USER , self.APIKEY, self.PROJECT_KEY= load_jira_vars()
        self.PERF_USER ,self.PERF_SERVER , self.PERF_WORKSPACE = load_perf_vars()
        self.LOCAL_ROOT, self.DEPOT_ROOT = load_root_vars()
        self.PROJ_SETTINGS = hlp.get_yaml_fil_data( de.SCRIPT_FOL +'\\' + self.PROJECT_KEY + de.SETTINGS_SUFIX )
        table.clear()
        try:
            tasks_ls_diccs = self.get_self_tasks( )
        except Exception as err:
            print (err)
            tasks_ls_diccs = []
        for i, header in enumerate (de.HEADER_LS):
            locals()["item"+ str(i)] = QTableWidgetItem(header)
            locals()["item"+ str(i)].setBackground(QColor(180, 75, 65))
            table.setHorizontalHeaderItem( i,locals()["item"+ str(i)] )
            #self.tablaWidgShots.horizontalHeader().setFixedHeight(40)
        table.setColumnWidth( de.THUMB_IDX , de.width_as_thum )
        self.id_rows = {}
        for i, task in enumerate(tasks_ls_diccs):
            table.setRowHeight(i, de.height_as_thum )
            self.id_rows[str(i)] = task['Id']
            char_thumb_path = hlp.solve_path( True, task[de.asset_na], 'Char_Thumb_Path' ,
                                            self.LOCAL_ROOT, self.DEPOT_ROOT, self.PROJ_SETTINGS)
            thumbMediaPath, thumb_fi_na = hlp.separate_path_and_na( char_thumb_path )
            label_thumb = getThumbnClass( table,  thumbMediaPath+thumb_fi_na,  (de.width_as_thum , de.height_as_thum )   )
            table.setCellWidget( i , de.THUMB_IDX, label_thumb )
            for idx, column in enumerate (de.HEADER_LS):
                try:
                    item = QTableWidgetItem( str( task[column] ) )
                    table.setItem(i ,idx, item)
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    if idx ==  de.TITLE_IDX:
                        item.setToolTip(str( task[column] ))
                except Exception as e:
                    pass

    def generate_menu_dicc(self):
        """Generate a Dictionary Specifying with menu will be triggered depending column selection.
        """
        self.dicc_menu_func = {}
        for header in de.HEADER_LS:
            if header == de.status:
                self.dicc_menu_func [header+'_menu_func'] = self.status_menu_func
            elif header == de.thumbnail:
                self.dicc_menu_func [header+'_menu_func'] = self.thumb_menu_func
            elif header == de.spec:
                self.dicc_menu_func [header+'_menu_func'] = self.issueLink_menu_func
            elif header == de.asset_na:
                self.dicc_menu_func [de.asset_na+'_menu_func'] = self.asset_na_menu_func

    def menues_asset_table(self, position):
        """keep initialize the proper menu function on each column.
        Args:
            position ([qposition]): [not need to set this arg]
        """
        for header in de.HEADER_LS:
            if self.current_table.horizontalHeaderItem( self.current_table.currentColumn()).text() == header:
                self.dicc_menu_func [ header + '_menu_func']( self.current_table, position )

    def initialized_features_table(self, table):
        """initialize table menues and actions.
        """
        self.current_table = table
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect( self.menues_asset_table )
        table.setEditTriggers( QTableWidget.NoEditTriggers )

    def refresh_tables(self):
        """Refresh given tables
        """
        table_ls= [ self.current_table ]#, self.ui.table_animTasks ]
        for table in table_ls:
            self.populate_table(table)

    def get_text_item_colum( self, table , colum_idx):
        """Return the text value for t he current row and specified column index of  table.
        Args:
            table ([qtablewidget]): [description]
            colum_idx ([int]): [column headers have internally assigned an index begining the first as 0, etc]
        Returns:
            [type]: [description]
        """
        item_text = table.currentRow()
        item_text = table.item( item_text, colum_idx )
        return str(item_text.text())

    def asset_na_menu_func(self, table, position ):
        """Floatting menu on asset name column.
        Args:
            table ([qtablewidget obj]): []
            position ([qposition]): [not need to set this arg]
        """
        menu_asset_na = QMenu()
        asset_na = str( table.currentItem().text() )
        area = self.get_text_item_colum(table, de.AREA_IDX)
        exploreAction = menu_asset_na.addAction(de.open_fi_fol)
        getFiAction = menu_asset_na.addAction( de.dowload_fi_perf )
        actionMenu = menu_asset_na.exec_(table.mapToGlobal(position))
        if actionMenu != None:
            if str(actionMenu.text()) == de.open_fi_fol:
                self.explore_char_fol(asset_na, area)
            elif str(actionMenu.text()) == de.dowload_fi_perf:
                self.get_task_file( asset_na, area)

    def get_task_file(self, asset_na, area):
        """dowload given asset data file to local
        Args:
            asset_na ([str]): [asset name]
            area ([str]): [could be Rig|Mod|Surf]
        """
        local_full_path, depot_full_path = self.get_asset_path( asset_na, area)
        perf = pr.PerforceRequests()
        dicc = perf.pull_file_2_local( depot_full_path, True , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE )
        if dicc[de.key_errors] != '[]':
            QMessageBox.information(self.main_widg, u'Downloading task error', str( dicc[de.key_errors] )  )
            
    def get_asset_path(self, asset_na, area):
        """return depot and local asset path
        Args:
            asset_na ([str]): [asset name]
            area ([str]): [asset area]
        Returns:
            [tuple]: [return to arg as touple format: local full path and perforce repo full path]
        """
        local_full_path = hlp.solve_path( True, asset_na, area+'_Char_Path',
                                            self.LOCAL_ROOT, self.DEPOT_ROOT, self.PROJ_SETTINGS)
        depot_full_path = hlp.solve_path( False, asset_na, area+'_Char_Path',
                                            self.LOCAL_ROOT, self.DEPOT_ROOT, self.PROJ_SETTINGS)
        return local_full_path, depot_full_path

    def explore_char_fol(self, asset_na, area):
        """this function will open the file containing folder
        Args:
            asset_na ([str]): [asset name]
            area ([str]): [asset area]
        """
        local_full_path, depot_full_path = self.get_asset_path( asset_na, area)
        path_, fi_na = hlp.separate_path_and_na(local_full_path)
        os.startfile(path_)
    
    def thumb_menu_func(self, table, position ):
        """thumbnail menu generator
        Args:
            table ([qtable]): [qtable widget]
            position ([qposition]): [don t need to be instanced]
        """
        asset_na = self.get_text_item_colum( table, de.ASSET_NA_IDX)
        thumbLocalPath, thumb_fi_na = hlp.separate_path_and_na(    hlp.solve_path( True, asset_na, 'Char_Thumb_Path',
                                                                                self.LOCAL_ROOT, self.DEPOT_ROOT, self.PROJ_SETTINGS ) )
        thumbDepotPath, thumb_fi_na = hlp.separate_path_and_na(    hlp.solve_path( False, asset_na, 'Char_Thumb_Path' ,
                                                                                self.LOCAL_ROOT, self.DEPOT_ROOT, self.PROJ_SETTINGS)  )
        menu_thumb = QMenu()
        doThumbnailAc1 = menu_thumb.addAction( de.do_thumb, lambda: self.do_row_thumb( thumbLocalPath, thumb_fi_na, table , de.THUMB_IDX ) )
        doThumbnailAc2 = menu_thumb.addAction( de.get_thumb , lambda: self.get_thumb_from_depot( thumbDepotPath , thumb_fi_na , table , de.THUMB_IDX) )
        actionThumb = menu_thumb.exec_(table.mapToGlobal(position))

    def get_thumb_from_depot( self, thumbDepotPath, thumb_fi_na , table , colum_idx ):
        """trigging action to dowload depot thumbnail on local and load it on task
        Args:
            thumbMediaPath ([str]): [path]
            thumb_fi_na ([str]): [file name]
            table ([qtalbe]): [qtable widget]
            colum_idx ([int]): [integer related to the column index]
        """
        local_path = thumbDepotPath.replace( self.DEPOT_ROOT, self.LOCAL_ROOT )
        try:
            os.remove( local_path+thumb_fi_na )
        except Exception:
            pass
        perf = pr.PerforceRequests()
        dicc = perf.pull_file_2_local( thumbDepotPath+thumb_fi_na, True , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE )
        thumb_fi = os.path.join(  local_path, thumb_fi_na)
        if dicc[de.key_errors] == '[]':
            if os.path.isfile( thumb_fi ):
                label_thumb = getThumbnClass( table, local_path +thumb_fi_na,   (de.width_as_thum , de.height_as_thum)   )
                table.setCellWidget(table.currentRow(), colum_idx, label_thumb )
        else:
            QMessageBox.information(self.main_widg, u'Dowloading humbnail error.', str( dicc[de.key_errors] )  )

    def do_row_thumb ( self, thumbLocalPath, thumb_fi_na, table , colum_idx ):
        """Creates thumbnail, applies this thumbnail to the task, and submits it to perforce depot
        Args:
            thumbMediaPath ([str]): [thumb path]
            thumb_fi_na ([str]): [thumb file name]
            table ([qtalbe]): [qtable widget]
            colum_idx ([int]): [integer related to the column index]
        """
        try:
            if ev.current_scene().startswith( thumbLocalPath ):
                if os.path.exists(thumbLocalPath):
                    perf = pr.PerforceRequests()
                    try:
                        perf.checkout_file( thumbLocalPath+thumb_fi_na , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE, True)
                        hlp.make_read_write( thumbLocalPath+thumb_fi_na )
                        os.remove( thumbLocalPath+thumb_fi_na )
                    except Exception as er:
                        print(er)
                    ev.com.thumbnail_cmd( de.height_as_thum, de.width_as_thum, thumbLocalPath, thumb_fi_na)
                    label_thumb = getThumbnClass( table, thumbLocalPath+thumb_fi_na,  (de.width_as_thum , de.height_as_thum)   )
                    table.setCellWidget(table.currentRow(), colum_idx, label_thumb )
                    comment='new thumbnail created'
                    dicc = perf.add_and_submit( thumbLocalPath+thumb_fi_na, comment , self.PERF_SERVER, self.PERF_USER, self.PERF_WORKSPACE ,True )
                    if dicc[de.key_errors] != '[]':
                        QMessageBox.information(self.main_widg, u' ', str(dicc[de.key_errors]))
                else:
                    QMessageBox.information(self.main_widg, u' ', " Check if you have localized this task ")
            else:
                QMessageBox.information(self.main_widg, u' ', " Check if current Scene is matching with selected task ")
        except AttributeError: 
            QMessageBox.information(self.main_widg, u' ',  " No Scene Opened ")

    def status_menu_func(self, table, position):
        """Menu on Status column witch change jira issue status.
        Args:
            table ([qtablewidget]): [needed table]
            position ([qposition]): [not instantiable var]
        """
        dicc = self.jira_m.get_all_statuses_types(self.USER, de.SERVER, self.APIKEY)
        if dicc[ de.key_errors ] != '[]':
            QMessageBox.information(self.main_widg, u'Getting status types error.', str( dicc[de.key_errors] )  )
        menu_status = QMenu()
        for status in dicc[de.ls_ji_result]:
            statusAction = menu_status.addAction(str(status))
        actionStatus = menu_status.exec_(table.mapToGlobal(position))
        row = table.currentRow()
        issue_key = self.id_rows[str(row)]
        if actionStatus != None:
            dicc = self.jira_m.change_issue_status( issue_key, self.USER, de.SERVER, self.APIKEY, actionStatus.text())
            if dicc[ de.key_errors ] != '[]':
                QMessageBox.information(self.main_widg, u'Changing status error.', str( dicc[de.key_errors] )  )
            if dicc [de.ls_ji_result ] != []:
                item = QTableWidgetItem( actionStatus.text() )
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                table.setItem( row ,de.STATUS_IDX, item )
    
    def issueLink_menu_func(self, table, position):
        """Menu on Spec column witch browse you to the jira issue link.
        Args:
            table ([qtablewidget]): [needed table]
            position ([qposition]): [not instantiable var]
        """
        link = table.currentItem().text()
        menu_link = QMenu()
        linkAction = menu_link.addAction('open issue link')
        actionLink = menu_link.exec_(table.mapToGlobal(position))
        if actionLink != None:
            if actionLink.text() == "open issue link":
                webbrowser.open(link, new=2) 
    

class getThumbnClass(QLabel):
    def __init__(self, parent=None, path=None, size=(0,0)):
        """Qlabel class for asume as thumbnail
        Args:
            parent ([q object], optional): [q object for been parented]. Defaults to None.
            path ([str], optional): [thumbnail path]. Defaults to None.
            size (touple, optional): [touple with height and width values]. Defaults to (0,0).
        """
        super(getThumbnClass, self).__init__(parent)
        pic = QPixmap( path ).scaled(QtCore.QSize(size[0],size[1]), QtCore.Qt.KeepAspectRatio)
        self.setPixmap(pic)


if str(sys.version).startswith('2'): #ThreadReturnPy2
	class ThreadReturn(Thread):
		def __init__(self, group=None, target=None, name=None,args=(), kwargs={}, Verbose=None):
			Thread.__init__(self, group, target, name, args, kwargs) #, Verbose
			self._return = None
		def run(self):
			try:
				print (self._Thread__target)
			except Exception:
				self._Thread__target = None
			if self._Thread__target is not None:
				self._return = self._Thread__target(*self._Thread__args,
												   **self._Thread__kwargs)
		def join(self):
			Thread.join(self)
			return self._return

elif str(sys.version).startswith('3'):
	class ThreadReturn(Thread): #ThreadReturnPy3
		def __init__(self, group=None, target=None, name=None,
					args=(), kwargs={}, Verbose=None):
			Thread.__init__(self, group, target, name, args, kwargs)
			self._return = None
		def run(self):
			print(type(self._target))
			if self._target is not None:
				self._return = self._target(*self._args,
													**self._kwargs)
		def join(self, *args):
			Thread.join(self, *args)
			return self._return