#### Runing the manager in differents platforms, like Maya, Houdini, Windows we need to same vars with different contents.
import sys
try:
	import importlib
except Exception:
    pass


ENVIROMENT = ''
for path in sys.path:
    if "Maya2020" in path or "Maya2021" in path or "Maya2022" in path or "Maya2023" in path:
        ENVIROMENT = 'Maya'
        break
if ENVIROMENT == 'Maya': 
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
