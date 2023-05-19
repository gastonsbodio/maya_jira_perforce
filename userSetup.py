import sys
import maya.cmds as cmd
import ctypes
from ctypes.wintypes import MAX_PATH
dll = ctypes.windll.shell32
buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
    USER_DOC = buf.value
SCRIPT_FOL = USER_DOC + "\\prod_manager\\jira_manager"
if SCRIPT_FOL not in sys.path:
    sys.path.append( SCRIPT_FOL )
import helper as hlp
import jira_project_manager as jiraM
import definitions as de
try:
    import importlib
    importlib.reload(hlp)
    importlib.reload( jiraM )
    importlib.reload( de )
except Exception:
    reload(hlp)
    reload(jiraM)
    reload(de)
if de.PY_PACKAGES not in sys.path:
    sys.path.append( de.PY_PACKAGES )
import pymel.core as pm

def launch_manager():
    widget = jiraM.MyMainWindow()
    widget.ui.show()
def update_tools():
    file_content = hlp.write_down_tools ( )
    hlp.create_python_file ('update_tools', file_content)
    hlp.run_py_stand_alone( 'update_tools', True)

def runScr():
    print ('         * *         inizializing userSetup         * *   ')
    main_window = pm.language.melGlobals['gMainWindow']
    menu_obj='ManagerMenu'
    menu_lable='Jira Manager Tool'
    try:
        if pm.menu( menu_obj, label = menu_lable, exists = True, parent = main_window ):
            pm.deleteUI( pm.menu( menu_obj, e=True,deleteAllItems=True ))
    except Exception:
        pass
    custom_tools_menu = pm.menu ( menu_obj, label = menu_lable, parent = main_window, tearOff=True)
    pm.menuItem( label='launch manager tool', command='launch_manager()' )
    #pm.menuItem( label='example', subMenu=True, parent = custom_tools_menu , tearOff = True )
    #pm.menuItem( label='sub example', command='ecample_func()' )
    pm.setParent( '..', menu = True )
    pm.menuItem( label='update tools', command='update_tools()' )

cmd.evalDeferred(runScr)