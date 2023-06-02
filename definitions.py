### Main Constants on the manager System. 
import sys
import tempfile
import os
import ctypes
from ctypes.wintypes import MAX_PATH

dll = ctypes.windll.shell32
buf = ctypes.create_unicode_buffer(MAX_PATH + 1)

## general vars
if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
	USER_DOC = buf.value
SCRIPT_FOL = USER_DOC + "\\prod_manager\\jira_manager"

PY_PACK_MOD = USER_DOC + "\\prod_manager\\packages"
PY2_PACKAGES = PY_PACK_MOD + "\\py2" 
PY3_PACKAGES = PY_PACK_MOD + "\\py3" 
if sys.version_info.major == 2:
	PY_PACKAGES = PY2_PACKAGES
elif sys.version_info.major == 3:
    
	PY_PACKAGES = PY3_PACKAGES
PY3CACHE_FOL = '__pycache__'
TEMP_FOL = tempfile.gettempdir().replace("\\","/") + "/"
JI_SERVER = "https://genvidtech.atlassian.net"
JIRA_API_TOKEN_HELP = 'https://docs.searchunify.com/Content/Content-Sources/Atlassian-Jira-Confluence-Authentication-Create-API-Token.htm'
INSTRUCTION_CHECK_ANIM_TOOL = 'https://docs.google.com/document/d/1gAxtH1fhukNAWPnWSfflYai9NQe0qsh6OVcnn7FzlKU/edit?usp=sharing'
ANIM_CHECK_TOOL_SETTING ='anim_check_settings.json'
LOGIN_METADATA_FI_NA ='login_metadata.json'
PERF_LOG_METADATA_FI_NA ='perf_log_metadata.json'
ROOTS_METAD_FI_NA = 'roots_metadata.json'
PY_PATH = 'C:/Python27/'
JIRA_MANAGE_FOL = 'jira_manager'
SETTINGS_SUFIX = '__settings__.yaml'
MANAGE_PROD_UI = 'management_tool.ui'
TASK_CREATION_UI = 'task_creation_panel.ui'
ANIM_CHECK_UI = 'checker_anim_tool.ui'
FORBIDDEN_CHARS = [" ","-","_","@","%", "$","?", "!", "|","*",".",",",";"]

###########
#MASTER_USER = ""
#MASTER_API_KEY = ""

#### Googlesheets vars
GOOGLE_SHET_DATA_NA = "jira_manager_data"
GOOGLE_SHET_ANIM_CHECK = "Task_001"
GOOG_CONTENT_TOOLS_FOL = "jira_manager"
GOOGLE_SH_ASS_NA_COL = "asset_name"
GOOGLE_SH_CREAT_AREA_COL = 'created_area'
GOOGLE_SH_ISSUE_KEY = 'jira_issue_key'
GOOG_SH_ALPHA_LS =   ["A","B","C","D","E","F","G","H","I","J", "K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
GOOG_SH_NUM_COL =[ 1,  2,  3,  4,  5,  6,  7,  8,  9,  10,  11, 12, 13, 14, 15, 16, 17,18, 19, 20, 21, 22, 23, 24, 25, 26]




## asset table vars
assignee = 'Assignee'
reporter = 'Reporter'
id = 'Id'
status = "Status"
comments = 'Comments'
spec = 'Spec'
title= 'Title'
area = 'Area'
asset_na = 'Asset_na'
thumbnail = 'Thumbnail'
HEADER_LS = [ thumbnail , asset_na , area , title , spec, comments , status ]

### check anim tool
anim = 'Animation'
maya = 'Maya'
fbx = 'FBX'
unreal = 'Unreal'
anim_check_colum_sheet_column = 'Narrative Request Outline'
CHECK_ANIM_LS = [ anim , maya , fbx , unreal ]

THUMB_IDX = 0
ASSET_NA_IDX = 1
AREA_IDX = 2
TITLE_IDX = 3
STATUS_IDX = 6

width_as_thum = 100
height_as_thum = 65
height_anim_ch_row = 20

##  menues texts
open_fi_fol = 'explore file dir'
dowload_fi_perf = 'get file from depot'
do_thumb = 'do thumbnail'
get_thumb = 'get thumbnail from depot'

## perforce vars
dicc_result = 'dicc_result'
ls_result = 'ls_result'

## jira vars
issue_type_asset = 'Asset'
dicc_ji_result = 'dicc_result'
ls_ji_result = 'ls_result'
key_connected = 'keyConnected'

### commons keys
key_errors= 'errors'

#######  anim check tool vars
UNR_EXCEPTION_SUFIXS = [ "_Cinematics.uasset", "_Montage.uasset"]