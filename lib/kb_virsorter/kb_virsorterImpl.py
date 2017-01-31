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

from KBaseReport.KBaseReportClient import KBaseReport
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from DataFileUtil.DataFileUtilClient import DataFileUtil
from Workspace.WorkspaceClient import Workspace as workspaceService


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
    GIT_COMMIT_HASH = "adfa71ac12dba6f6df1d363b682041234723fd4a"
    
    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
 
 
    def do_assembly(self, assembly_ref, file_path, wsClient):
        try:
            assembly = wsClient.get_objects2({'objects': [{'ref': assembly_ref}]})['data'][0]
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error from workspace:\n' + orig_error)

        fasta_handle_ref = assembly['fasta_handle_ref']
        print fasta_handle_ref

        param = []
        param['fasta_handle_ref'] = fasta_handle_ref
        #TODO create file here /kb/module/work
        #TODO set output file name
        input_fasta_file = ""
        AssemblyUtil.get_assembly_as_fasta(self, param)


        #cmdstring = "".join('docker run -v ', '/data:/data', ' -v ', '/kb/module/work:/wdir',
        #                    ' -w ', '/wdir', ' --rm ', 'discoenv/virsorter:v1.0.3', ' --db ', 2, ' --fna  ',
        #                    '/wdir/', input_fasta_file)

        cmdstring = "".join("wrapper_phage_contigs_sorter_iPlant.pl ",
                            "--db 2 ",
                            "--fna ", "/kb/module/work", input_fasta_file,
                            "--wdir ", "/kb/module/work")

        cmdProcess = subprocess.Popen(cmdstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = cmdProcess.communicate()
        report += "cmdstring: " + cmdstring + " stdout: " + stdout + " stderr: " + stderr

        return [report]

        
    def do_genome(self, genome_ref, file_path, wsClient):
        try:
            genome = wsClient.get_objects2({'objects': [{'ref': genome_ref}]})['data'][0]
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            orig_error = ''.join('    ' + line for line in lines)
            raise ValueError('Error from workspace:\n' + orig_error)
        
        print(str(genome))
        assembly_ref = genome['Assembly_ref']
        returnVal = self.do_assembly(assembly_ref, file_path, wsClient)
        
        return [returnVal]
    
    
    
    #def _download_assembly_from_shock(self, ref, obj_name, handle, file_type):
    #    params = {'shock_id': handle['id'],
    #              'unpack': 'uncompress',
    #              'file_path': os.path.join(self.scratch, handle['id'])
    #              }
    #    dfu = DataFileUtil(self.callback_url)
    #    ret = dfu.shock_to_file(params)
    #    fn = ret['node_file_name']
    #    if file_type and not file_type.startswith('.'):
    #        file_type = '.' + file_type
    #    ok = False
    #    for f, n in zip([fn, handle['file_name'], file_type],
    #                    ['Shock file name',
    #                     'Handle file name from reads Workspace object',
    #                     'File type from reads Workspace object']):
    #        if f:
    #            if not self._filename_ok(f):
    #                raise ValueError(
    #                    ('{} is illegal: {}. Expected FASTQ file. Reads ' +
    #                     'object {} ({}). Shock node {}')
    #                    .format(n, f, obj_name, ref, handle['id']))
    #            ok = True
    #    # TODO this is untested. You have to try pretty hard to upload a file without a name to Shock. @IgnorePep8 # noqa
    #    if not ok:
    #        raise ValueError(
    #            'Unable to determine file type from Shock or Workspace ' +
    #            'data. Reads object {} ({}). Shock node {}'
    #            .format(obj_name, ref, handle['id']))
    #    if not fn:
    #        self.log('No filename available from Shock')
    #    else:
    #        self.log('Filename from Shock: ' + fn)
    #    return ret['file_path'], fn
        
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        self.scratch = config['scratch']

        print "workspaceURL " + self.workspaceURL
        print "scratch "+self.scratch

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
