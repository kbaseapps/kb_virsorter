# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
import sys
import os
import requests
import subprocess
import shutil
import traceback
import uuid
from pprint import pprint, pformat
from biokbase.workspace.client import Workspace as workspaceService
from KBaseReport.KBaseReportClient import KBaseReport
from ReadsUtils.ReadsUtilsClient import ReadsUtils

#END_HEADER


class kb_virsorter:
    '''
    Module Name:
    kb_virsorter

    Module Description:
    A KBase module: kb_virsorter
This module wraps the virsorter pipeline.
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/kb_virsorter.git"
    GIT_COMMIT_HASH = "fe6618ba6978f710becbc68bb9b136fa3d857f15"
    
    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    workspaceURL = None
    
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        #END_CONSTRUCTOR
        pass
    

    def run_virsorter(self, ctx, params):
        """
        Identify viral sequences in microbial reads
        :param params: instance of type "VirsorterParams" -> structure:
           parameter "assembly_ref" of String, parameter "genome_ref" of
           String
        :returns: instance of type "VirsorterResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN run_virsorter
        
        if 'assembly_ref' not in params and 'genome_ref' not in params:
            raise ValueError('Parameter assembly_ref or genome_ref is not set in input arguments')
        elif 'assembly_ref' in params:
            assembly_ref = params['assembly_ref']
        elif 'genome_ref' in params:
            genome_ref = params['genome_ref']
        
        token = ctx['token']
        wsClient = workspaceService(self.workspaceURL, token=token)
        headers = {'Authorization': 'OAuth ' + token}
        uuid_string = str(uuid.uuid4())
        file_path = self.scratch + "/" + uuid_string
        os.mkdir(file_path)
        
        if assembly_ref:
            returnVal = self.do_assembly(assembly_ref, file_path, wsClient)
        elif genome_ref:
            returnVal = self.do_genome(assembly_ref, file_path, wsClient)
        
        #END run_virsorter

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method run_virsorter return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION,
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
