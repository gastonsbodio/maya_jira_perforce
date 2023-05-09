### Main Constants on the manager System. 
import sys
import tempfile
import enviroment as ev
import os
import ctypes
from ctypes.wintypes import MAX_PATH

dll = ctypes.windll.shell32
buf = ctypes.create_unicode_buffer(MAX_PATH + 1)

## general vars
if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
	USER_DOC = buf.value
SCRIPT_FOL = USER_DOC + "\\prod_manager\\jira_manager"

PY2_PACKAGES = USER_DOC + "\\prod_manager\\packages\\py2" 
PY3_PACKAGES = USER_DOC + "\\prod_manager\\packages\\py3" 
if sys.version_info.major == 2:
	PY_PACKAGES = PY2_PACKAGES
elif sys.version_info.major == 3:
	PY_PACKAGES = PY3_PACKAGES

TEMP_FOL = tempfile.gettempdir().replace("\\","/") + "/"
LOGIN_METADATA_FI_NA ='login_metadata.json'
PERF_LOG_METADATA_FI_NA ='perf_log_metadata.json'
SERVER = "https://genvidtech.atlassian.net"
JIRA_API_TOKEN_HELP = 'https://docs.searchunify.com/Content/Content-Sources/Atlassian-Jira-Confluence-Authentication-Create-API-Token.htm'
PY_PATH = 'C:/Python27/'
JIRA_MANAGE_FOL = 'jira_manager'
SETTINGS_SUFIX = '__settings__.yaml'
MANAGE_PROD_UI = 'management_tool.ui'

#MASTER_USER = ""
#MASTER_API_KEY = ""

GOOGLE_SHET_DATA_NA = "jira_manager_data"
GOOG_CONTENT_TOOLS_FOL = "jira_manager"

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
THUMB_IDX = 0
ASSET_NA_IDX = 1
AREA_IDX = 2
TITLE_IDX = 3
STATUS_IDX = 6

width_as_thum = 100
height_as_thum = 65

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