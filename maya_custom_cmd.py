import maya.cmds as cmds
#import pymel.core as pm
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as mui
from shiboken2 import wrapInstance

def getWindow(QWidget):
    pointer = mui.MQtUtil.mainWindow()
    if pointer is not None:
        try:
            return wrapInstance(long(pointer), QWidget)
        except Exception:
            return wrapInstance(int(pointer), QWidget)

def thumbnail_cmd( h, w, path, name):
    """Maya thumbnail generator command
    Args:
        h ([int]): [description]
        w ([int]): [description]
        path ([str]): [description]
        name ([str]): [description]
    """
    frame = cmds.currentTime(q=1)
    currentPanel = cmds.playblast( ae = True )
    cmds.modelEditor (currentPanel, edit = True, grid = False, hud = False  ,alo = False)
    cmds.modelEditor (currentPanel, edit = True, polymeshes = True,str = True , da = "smoothShaded")
    cmds.setAttr ('defaultRenderGlobals.imageFormat', 8)
    cmds.playblast( format = "image", cf = path + "/" + name , h = h, w = w,
                fr = [frame], viewer = False, orn = False, fp = 0, fo = True, p = 100, qlt = 100)

def get_script_fol():
    cmds.internalVar(usd=True)

def get_current_sc():
    return cmds.file(query=True, sceneName=True)
    #return str( pm.sceneName() ).split('Path(')[-1].split(')')[0]