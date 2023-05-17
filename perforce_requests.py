### perforce requests. 
## each request has 'direct', or by 'python standalone' way.

import sys
from subprocess import call
try:
	import importlib
except Exception:
    pass
import definitions as de
import helper as hlp
try:
    reload(de)
    reload(hlp)
except Exception:
    importlib.reload(de)
    importlib.reload(hlp)
sys.path.append( de.PY_PACKAGES )
try:
    from P4 import P4,P4Exception    # Import the module
except Exception as e:
    pass

class PerforceRequests():
    def connection(self, server, user, workspace ):
        """Perforce connection
        Args:
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
        Returns:
            [P4 object connected]: [with this obj you will do all the requests]
        """
        p4 = P4()                        # Create the P4 instance
        p4.port = server
        p4.user = user
        p4.client = workspace           # Set some environment variables
        try:                             # Catch exceptions with try/except
            p4.connect()                   # Connect to the Perforce server
        except P4Exception:
            for e in p4.errors:            # Display errors
                print (e)
            return None
        return p4

    def add_and_submit(self, file, comment, server, user, workspace, pyStAl ):
        """Add and submit requests.
        Args:
            file ([str]): [file to submit]
            comment ([str]): [comment on the submition]
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        """
        if pyStAl == False:
            p4 = self.connection(server, user, workspace)
            p4.run_add(file)
            p4.run_submit('-d', comment)
            p4.disconnect()
        else:
            line =        '    p4.run_add("%s")\n' %file
            line = line + '    p4.run_submit("-d", "%s")\n' %comment
            file_content = hlp.write_perforce_command_file ( line , True, 'addsubmit_perf_query.json')
            hlp.create_python_file ( 'add_and_submit', file_content )
            hlp.run_py_stand_alone( 'add_and_submit' )
            return hlp.json2dicc_load( de.PY_PATH  + 'addsubmit_perf_query.json')

    def get_info(self, server, user, workspace):
        """get Perforce Info
        Args:
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
        """
        p4 = self.connection(server, user, workspace)
        info = p4.run( "info" )  
        # Run "p4 info" (returns a dict)
        print ( info )
        for key in info[0]:            # and display all key-value pairs
            print (key, "=", info[0][key])
        p4.disconnect() 

    def get_all_depo_files(self, server, user, workspace):
        """get all depo files
        Args:
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
        Returns:
            [ls]: [description]
        """
        p4 = self.connection(server, user, workspace)
        depo_files = p4.run_filelog()  ##### list of files query
        p4.disconnect() 
        return depo_files 

    def get_fol_fi_on_folder( self, type ,folder, pyStAl, server, user, workspace ):
        """get files or dirs on given perforce depot directory
        Args:
            type ([str]): [('files', 'dirs')]
            folder ([str]): [full file path]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description] 
        Returns:
            [type]: [description]
        """
        if pyStAl == False:
            try:
                p4 = self.connection( server, user, workspace)
                items = p4.run(type ,folder + "*")
                p4.disconnect()
                return items
            except Exception as err:
                print (err)
                return []
        else:
            line = '    {files_ls} = p4.run("{type}" ,"{folder}" + "*")'.format( files_ls= de.ls_result, type= type,folder= folder)
            file_content = hlp.write_perforce_command_file ( line , True, 'get_perf_fi_dirs.json')
            hlp.create_python_file ('get_files_in_dir', file_content)
            hlp.run_py_stand_alone( 'get_files_in_dir'  )
            return hlp.json2dicc_load( de.PY_PATH  + 'get_perf_fi_dirs.json')

    def workspaces_ls(self, pyStAl, server, user, workspace):
        """AI is creating summary for workspaces_ls
        Args:
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
        Returns:
            [ls]: [list of dictionaries with all workspaces data]
        """
        if pyStAl == False:
            p4 = self.connection( server, user, workspace)
            p4.disconnect()
            return p4.run_clients()
        else:
            line = '    {files_ls} = p4.run_clients()'.format( files_ls= de.ls_result )
            file_content = hlp.write_perforce_command_file ( line , True, 'workspace_request.json')
            hlp.create_python_file ('get_workspaces', file_content)
            hlp.run_py_stand_alone( 'get_workspaces' )
            return hlp.json2dicc_load( de.PY_PATH  + 'workspace_request.json')

    def pull_file_2_local(self, file, pyStAl, server, user, workspace):
        """ 'pull' , 'dowload' , 'get' a file (if file is already locally it will bring error)
        Args:
            file ([str]): [depot file file path]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
        """
        if pyStAl == False:
            p4 = self.connection( server, user, workspace )
            p4.run("sync",file)
            p4.disconnect()
        else:
            line = '    p4.run("sync", "-f" , "{file}")\n'.format( file = file)
            file_content = hlp.write_perforce_command_file ( line , True, 'pull_perf_query.json')
            hlp.create_python_file ('pull_file', file_content)
            hlp.run_py_stand_alone( 'pull_file' )
            return hlp.json2dicc_load( de.PY_PATH  + 'pull_perf_query.json')

    def checkout_file( self, local_path_file ,server, user, workspace, pyStAl):
        """Make a file editable after dowloading from perforce ( checkout file)
        Args:
            local_path_file ([str]): [local file file path]
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        """
        if pyStAl == False:
            p4 = self.connection( server, user, workspace )
            p4.run( "edit", local_path_file )
            p4.disconnect()
        else:
            line = '    p4.run( "edit", "{file}" )\n'.format( file = local_path_file)
            file_content = hlp.write_perforce_command_file ( line , True, 'result_perf_query.json')
            hlp.create_python_file ('edit_file', file_content)
            hlp.run_py_stand_alone( 'edit_file' )
            return hlp.json2dicc_load( de.PY_PATH  + 'result_perf_query.json')
        
    def get_all_dir_fol( self, path_root, server, user, workspace, return_ls = [] , pyStAl = False ):
        """List all folders and subfolders on a given path
        Args:
            path_root ([str]): [ directory for search in ]
            server ([str]): [description]
            user ([str]): [description]
            workspace ([str]): [description]
            return_ls (list, optional): [list of getting depot folders]. Defaults to [].
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        Returns:
            [ls]: [list of getting depot folders]
        """
        if pyStAl == False:
            if not path_root.endswith('/'):
                path_root = path_root + '/'
            if path_root not in return_ls:
                return_ls.append( path_root )
            folder_ls = self.get_fol_fi_on_folder( 'dirs' ,path_root, False, server, user, workspace )
            folder_ls = [ key['dir'] for key in folder_ls ]
            for directory in folder_ls:
                if not directory.endswith('/'):
                    directory = directory + '/'
                if directory not in return_ls:
                    return_ls.append( directory )
                print ( directory )
                line = '    %s = perf.get_all_dir_fol( "%s", "%s", "%s", "%s", return_ls = [] , pyStAl = False )' %( de.ls_result, 
                                                                                                                directory, 
                                                                                                                server, user, 
                                                                                                                workspace )
                file_content = hlp.write_perforce_command_file ( line , True, 'get_perf_sub_fold.json')
                hlp.create_python_file ('get_perf_sub_fold', file_content)
                hlp.run_py_stand_alone( 'get_perf_sub_fold','Special' )
                return_ls = return_ls + hlp.json2dicc_load( de.PY_PATH  + 'get_perf_sub_fold.json')[ de.ls_result ]
            return  return_ls
        else:
            line = '    %s = perf.get_all_dir_fol( "%s", "%s", "%s", "%s", return_ls = [] , pyStAl = False )' %( de.ls_result, 
                                                                                                                path_root, 
                                                                                                                server, user, 
                                                                                                                workspace )
            file_content = hlp.write_perforce_command_file ( line , True, 'get_perf_fold.json')
            hlp.create_python_file ('get_perf_fold', file_content)
            hlp.run_py_stand_alone( 'get_perf_fold','Special' )
            return hlp.json2dicc_load( de.PY_PATH  + 'get_perf_fold.json')