import sys
import os
import definitions as de
import helper as hlp
try:
	import importlib
except Exception:
    pass
try:
    reload( de )
    reload( hlp )
except Exception:
    importlib.reload( de )
    importlib.reload( hlp )

class GoogleSheetRequests():
    def get_master_credentials( self ):
        """Get master user and pass for getting jira projects
        Returns:
            [dicc]: [dicc with master user and pass]
        """
        line = '%s  = sheet.get_all_records()\n' %de.dicc_ji_result
        file_content = hlp.write_goo_sheet_request ( line , True, 'google_sheet_query.json')
        hlp.create_python_file ( 'google_sheet_query', file_content )
        hlp.run_py_stand_alone( 'google_sheet_query' )
        dicc = hlp.json2dicc_load( de.PY_PATH  + 'google_sheet_query.json')
        os.remove( de.PY_PATH  + 'google_sheet_query.json' )
        os.remove( de.PY_PATH  + 'google_sheet_query.py' )
        return dicc



