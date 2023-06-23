# -*- coding: utf-8 -*-
## Jira queries.
import sys
import os
import definitions as de
import json
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
if de.PY_PACKAGES not in sys.path:
    sys.path.append( de.PY_PACKAGES )
try:
    from jira import JIRA
except Exception:
    pass
try:
    import requests
    from requests.auth import HTTPBasicAuth
except Exception:
    pass

class JiraQueries():
    def jira_connection( self, user, server, apikey ):
        """jira main connection
        Args:
            user ([str]): [user email jira login]
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            apikey ([str]): [jira api key instead of using password]
        Returns:
            [jira obj]: [this object already connected will be able to do the queries]
        """
        options = {'server': server}
        return JIRA(options, basic_auth=( user, apikey ))

    def get_custom_user_issues( self, user, server, apikey , user_type, project_key, jira , pyStAl = True ):
        """
        Args:
            user ([str]): [ user email jira login]
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            apikey ([str]): [jira api key instead of using password]
            user_type ([str]): [parameter like ( assignee, reporter )]
            project_key ([str]): [description]
        Returns:
            [ls]: [list of jira issues obj]
        """
        if pyStAl == False:
            issues_ls = jira.search_issues(jql_str="project = %s AND %s = '%s'" %( project_key, user_type, user ) )#status = 'User Acceptance'")
            issue_dicc_ls = []
            for issue in issues_ls:
                main_args_issue_dicc = {}
                reporter = issue.fields.reporter.displayName
                main_args_issue_dicc[de.reporter] = reporter.encode('utf-8')
                status = str(issue.fields.status)
                main_args_issue_dicc[de.status] = status
                title = issue.fields.summary
                main_args_issue_dicc[de.title] = title
                labels_ls = issue.fields.labels
                if labels_ls != []:
                    main_args_issue_dicc[ de.area ] = self.dicc_label_value( labels_ls, de.area )
                    main_args_issue_dicc[ de.asset_na ] = self.dicc_label_value( labels_ls, de.asset_na )
                else:
                    main_args_issue_dicc[de.area] = ''
                    main_args_issue_dicc[de.asset_na] = ''
                assignee = issue.fields.assignee
                if assignee != None:
                    main_args_issue_dicc[de.assignee] = assignee.displayName.encode('utf-8')
                else:
                    main_args_issue_dicc[de.assignee] = str(assignee)
                main_args_issue_dicc[de.spec] = server +'/browse/'+str(issue.key)
                main_args_issue_dicc[de.id] = str(issue.key)
                issue_dicc_ls.append( main_args_issue_dicc )
            return issue_dicc_ls
        else:
            line = '%s = {object}get_custom_user_issues( "%s", "%s", "%s" , "%s", "%s", jira ,pyStAl = False ) \n' %(de.ls_ji_result, user, server, apikey , user_type, project_key)
            file_content = hlp.write_jira_command_file ( line , True, 'task_dicc_request.json', user, server, apikey)
            hlp.create_python_file ('get_task_dicc', file_content)
            hlp.run_py_stand_alone( 'get_task_dicc' )
            return hlp.json2dicc_load( de.PY_PATH  + 'task_dicc_request.json')

    def dicc_label_value(self, label_ls, prefix):
        result = ''
        for label_item in label_ls:
            if len ( label_item.split(prefix+'_') ) > 1:
                result =  str( label_item.split(prefix+'_')[-1] )
        return result

    def get_issues_by_status(self, user, server, apikey, status, API_KEY, pyStAl = True):
        """query issues setted previusly with some status
        Args:
            user ([str]): [user email jira login]
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            apikey ([str]): [jira api key instead of using password]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        Returns:
            [ls]: [list of jira issues obj]
        """
        if pyStAl == False:
            jira = self.jira_connection(user, server, apikey)
            issues_ls = jira.search_issues (jql_str = "status = '{status_label}'".format( status_label = status ))
            return issues_ls
        else:
            line =   'issues_ls = jira.search_issues (jql_str = "status = %s"\n' %( '"'+status +'"' )
            file_content = hlp.write_jira_command_file ( line , True, 'get_issue_by_status.json', user, server, API_KEY)
            hlp.create_python_file ('get_issue_by_status', file_content)
            hlp.run_py_stand_alone( 'get_issue_by_status' )
            return hlp.json2dicc_load( de.PY_PATH  + 'get_issue_by_status.json')#[de.ls_ji_result]

    def get_all_statuses_types( self ,user, server, apikey ,pyStAl = True ):
        """get all possibles jira status types
        Args:
            user ([str]): [user email jira login]
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            apikey ([str]): [jira api key instead of using password]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        Returns:
            [ls]: [status list]
        """
        if pyStAl == False:
            jira = self.jira_connection( user, server, apikey )
            status_type = jira.statuses()
            return status_type
        else:
            line = 'result = jira.statuses()\n'
            line = line + '    %s = [str(st) for st in result]\n' %de.ls_ji_result 
            file_content = hlp.write_jira_command_file ( line , True, 'status_request.json', user, server, apikey)
            hlp.create_python_file ('get_status_types', file_content)
            hlp.run_py_stand_alone( 'get_status_types' )
            return hlp.json2dicc_load( de.PY_PATH  + 'status_request.json')#[de.ls_ji_result]
    
    def change_issue_status(self, issue_key, user, server, apikey, new_status, pyStAl= True):
        """
        Args:
            issue_key (str): [issue string code to identify]
            user ([str]): [user email jira login]
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            apikey ([str]): [jira api key instead of using password]
            new_status ([str]): [slected status]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        """
        if pyStAl == False:
            jira = self.jira_connection(user, server, apikey)
            issue = jira.issue( issue_key )
            try:
                jira.transition_issue(issue, transition= new_status)
                return new_status
            except Exception:
                return 'None'
        else:
            line =         'issue = jira.issue( "%s" )\n' %issue_key
            line = line + '    jira.transition_issue(issue, transition= "{status}")\n'.format( status = new_status ) 
            line = line + '    {var} = "{status}"\n'.format( status = new_status , var = de.ls_ji_result )  
            file_content = hlp.write_jira_command_file ( line , True, 'jira_request.json', user, server, apikey)
            hlp.create_python_file ('change_status', file_content)
            hlp.run_py_stand_alone( 'change_status' )
            return hlp.json2dicc_load( de.PY_PATH  + 'jira_request.json')#[de.ls_ji_result]
        
    def get_request_jira_templ( self, server, proj_key , user, api_key,
                                url_line , py_fi_na, pyStAl= True ):
        """Make a Get Request on Jira Api.
        Args:
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            proj_key ([str]): [description]
            user ([str]): [ user email jira login]]
            api_key ([str]): [jira api key instead of using password]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        Returns:
            [ls]: [list of dicctionaries with users data]
        """
        if pyStAl == False:
            url = "%s%s" %( server, url_line )
            auth = HTTPBasicAuth( user, api_key )
            headers = {"Accept": "application/json"}
            query = {'jql': 'project = %s' %proj_key }
            response = requests.request("GET", url, headers=headers , params=query , auth=auth )
            data = json.loads( response.text )
            return data
        else:
            line =        'url = "%s%s"\n' %( server, url_line )
            line = line + 'auth = HTTPBasicAuth("%s", "%s")\n' %( user, api_key )
            line = line + 'headers = {"Accept": "application/json"}\n'
            line = line + 'query = {"jql": "project = %s" }\n' %proj_key
            line = line + 'response = requests.request("GET", url, headers=headers , params=query , auth=auth )\n'
            line = line + '%s = json.loads( response.text )' %de.ls_ji_result
            file_content = hlp.write_request_jira_file ( line , True, py_fi_na + '.json')
            hlp.create_python_file ( py_fi_na, file_content)
            hlp.run_py_stand_alone( py_fi_na )
            dicc = hlp.json2dicc_load( de.PY_PATH  + py_fi_na +'.json')[de.ls_ji_result]
            return dicc
        
    def get_assignable_users( self, server, proj_key , MASTER_USER, MASTER_API_KEY ):
        url_line = "/rest/api/2/user/assignable/search?project=%s" %( proj_key )
        result = self.get_request_jira_templ( server, proj_key , MASTER_USER, MASTER_API_KEY, 
                                            url_line, 'get_assig_users' , pyStAl = True )
        return result
    
    def get_issue_types( self, server, proj_key , MASTER_USER, MASTER_API_KEY ):
        url_line = "/rest/api/3/issuetype"
        result = self.get_request_jira_templ( server, proj_key , MASTER_USER, MASTER_API_KEY, 
                                            url_line ,'get_issue_types' , pyStAl = True )
        return result


    def put_request_jira_templ( self, server, user, api_key,
                                url_line , py_fi_na, payload):
        """Make a Put Request on Jira Api.
        Args:
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            proj_key ([str]): [description]
            user ([str]): [ user email jira login]]
            api_key ([str]): [jira api key instead of using password]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        """
        line =        'url = "%s%s"\n' %( server, url_line )
        line = line + 'auth = HTTPBasicAuth("%s", "%s")\n' %( user, api_key )
        line = line + 'headers = { "Accept": "application/json", "Content-Type": "application/json" }\n'
        line = line + payload
        line = line + 'response = requests.request( "PUT",url, data=payload, headers = headers, auth=auth )\n'
        file_content = hlp.write_request_jira_file ( line , True, py_fi_na + '.json')
        hlp.create_python_file ( py_fi_na, file_content)
        hlp.run_py_stand_alone( py_fi_na )
        dicc = hlp.json2dicc_load( de.PY_PATH  + py_fi_na +'.json')
        return dicc

    def assign_2_user (self, issue_key, assign_user_id, user ,server , apikey):
        url_line = "/rest/api/3/issue/%s/assignee" %issue_key
        payload = 'payload = json.dumps( { "accountId": "%s" } )\n' %assign_user_id
        dicc = self.put_request_jira_templ( server , user, apikey, url_line , 'assign_user' , payload )
        return dicc
        
    def get_projects(self, server, MASTER_USER, MASTER_API_KEY, pyStAl= True):
        """get projects list
        Args:
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        Returns:
            [ls]: [list of jira object project]
        """
        if pyStAl == False:
            jira = self.jira_connection( MASTER_USER, server, MASTER_API_KEY )
            projects = jira.projects()
            projects = [ str(p) for p in projects ]
            return projects
        else:
            line =        '{result} = jira.projects()\n'.format( result = de.ls_ji_result )
            line = line + '    {result} = [ str(p) for p in {result} ]\n'.format( result = de.ls_ji_result )
            file_content = hlp.write_jira_command_file ( line , True, 'jira_request.json', MASTER_USER, server, MASTER_API_KEY )
            hlp.create_python_file ('get_projects', file_content)
            hlp.run_py_stand_alone( 'get_projects' )
            dicc = hlp.json2dicc_load( de.PY_PATH  + 'jira_request.json')#[de.ls_ji_result]
            os.remove ( de.PY_PATH  + 'jira_request.json' )
            os.remove ( de.PY_PATH  + 'get_projects.py' )
            return dicc

    def set_label(self, issue_key, text, user ,server , apikey , pyStAl= True):
        """Tagger for create labels on issues for storage data.
        Args:
            issue_key (str): [description]
            text ([str]): [label text for add]
            user ([str]): [user email jira login]
            server ([str]): [example: "https://genvidtech.atlassian.net"]
            apikey ([str]): [jira api key instead of using password]
            pyStAl ([bool]): [True or False if you want to run the command com python stand alone mode]
        """
        if pyStAl == False:
            jira = self.jira_connection(user, server, apikey)
            issue = jira.issue(issue_key)
            issue.fields.labels.append( text )
            issue.update(fields={"labels": issue.fields.labels})
        else:
            line =         'issue = jira.issue("%s")\n' %issue_key
            line = line +  '    issue.fields.labels.append( "{text}" )\n'.format( text = text )
            line = line +  '    issue.update(fields={"labels": issue.fields.labels})\n'
            file_content = hlp.write_jira_command_file ( line , True, 'set_label.json', user, server, apikey, with_jira_q = False)
            hlp.create_python_file ('generate_labels', file_content)
            hlp.run_py_stand_alone( 'generate_labels' )
            return hlp.json2dicc_load( de.PY_PATH  + 'set_label.json')

    def create_issue( self, user, server, apikey, proj_key ,summary , description, type, assign_name , pyStAl = True ):
        issue_dict = {
            'project': {'key': proj_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': '%s' %type},
            'assignee':  {'name': assign_name },
                    }#'components': [{'name': 'SKS'}],
        if pyStAl == False:
            jira = self.jira_connection(user, server, apikey)
            new_issue = jira.create_issue( fields = issue_dict )
            return new_issue
        else:
            line  =         '%s = jira.create_issue( fields = %s )\n' %( de.ls_ji_result, issue_dict )
            line  =  line + '    %s = str(%s.key.encode("utf-8") )'%( de.ls_ji_result , de.ls_ji_result )
            file_content = hlp.write_jira_command_file ( line , True, 'create_issue.json', user, server, apikey, with_jira_q = False)
            hlp.create_python_file ('create_issue', file_content)
            hlp.run_py_stand_alone( 'create_issue' )
            return hlp.json2dicc_load( de.PY_PATH  + 'create_issue.json')

    def issue_types_for_project( self, user, server, apikey , proj_key):
        jira = self.jira_connection( user, server, apikey )
        issues_types = jira.issue_types_for_project( proj_key ) 