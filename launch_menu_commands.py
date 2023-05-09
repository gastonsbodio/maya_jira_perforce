import sys
import ctypes
from ctypes.wintypes import MAX_PATH
dll = ctypes.windll.shell32
buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
    USER_DOC = buf.value
SCRIPT_FOL = USER_DOC + "\\prod_manager\\jira_manager"
sys.path.append( SCRIPT_FOL )
import pymel.core as pm
import helper as hlp
import jira_project_manager as jiraM
try:
    import importlib
    importlib.reload(hlp)
    importlib.reload( jiraM )
except Exception:
    reload(hlp)
    reload(jiraM)
    
def launch_manager():
    widget = jiraM.MyMainWindow()
    widget.ui.show()
    
def update_tools():
    file_content = hlp.write_down_tools ( )
    hlp.create_python_file ('update_tools', file_content)
    hlp.run_py_stand_alone( 'update_tools', True)

main_window = pm.language.melGlobals['gMainWindow']
menu_obj='ManagerMenu'
menu_lable='Jira Manager Tool'

if pm.menu( menu_obj, label = menu_lable, exists = True, parent = main_window ):
    pm.deleteUI( pm.menu( menu_obj, e=True,deleteAllItems=True ))
    
custom_tools_menu = pm.menu ( menu_obj, label = menu_lable, parent = main_window, tearOff=True)
pm.menuItem( label='launch manager tool', command='launch_manager()' )
#pm.menuItem( label='Rigging', subMenu=True, parent = custom_tools_menu , tearOff = True )
#pm.menuItem( label='Mirror Joints', command='launch_manager()' )
pm.setParent( '..', menu = True )
pm.menuItem( label='update tools', command='update_tools()' )