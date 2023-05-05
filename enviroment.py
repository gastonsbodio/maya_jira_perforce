#### Runing the manager in differents platforms, like Maya, Houdini, Windows we need to same vars with different contents.
import sys
try:
	import importlib
except Exception:
    pass

excutSource = type (sys.stdout)
ENVIROMENT = ''
if len(str(excutSource).split("maya")) >1:
    ENVIROMENT = 'Maya'

if ENVIROMENT == 'Maya': 
    try:
        import maya_custom_cmd as com
        try:
            reload(com)
        except Exception:
            importlib.reload(com)
        ENV_SCRIPT_FOL = com.get_script_fol()
        def current_scene ():
            return com.get_current_sc()
        def getWindow(QWidget):
            return com.getWindow(QWidget)
    except Exception as e:
        print (e)