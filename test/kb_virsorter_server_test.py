# -*- coding: utf-8 -*-
import unittest
import os
import shutil
import json
import time
import requests

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint

from biokbase.workspace.client import Workspace as workspaceService


from kb_virsorter.kb_virsorterImpl import kb_virsorter
from kb_virsorter.kb_virsorterServer import MethodContext
from ReadsUtils.ReadsUtilsClient import ReadsUtils


class kb_virsorterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        user_id = requests.post(
            'https://kbase.us/services/authorization/Sessions/Login',
            data='token={}&fields=user_id'.format(token)).json()['user_id']
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_virsorter',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_virsorter'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_virsorter(cls.cfg)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_virsorter_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_virsorter_ok(self):
        #upload_assembly()
    
        params = {}
        #params['assembly_ref'] = self.testobjdata[0]['data'][0]['info'][6] +"/"+ self.testobjdata[0]['data'][0]['info'][0]
        params['genome_ref'] = '14690/2'
        
        result = self.getImpl().run_virsorter(self.getContext(), params)
        print('RESULT run_virsorter:')
        pprint(result)
    
        testresult = [
            {'blah': 'blah', 'bleh': 'bleh'}]
    
        self.assertEqual(sorted(result), sorted(testresult))

    def upload_assembly(self):

        if not self.testobjref:
            print "upload_assembly start"
    
            indata = 'EcoliMG1655.fasta'
            ftarget = os.path.join(self.scratch, indata)
            print "ftarget " + ftarget
            ret = shutil.copy('../test_data/' + indata, ftarget)
    
            self.readsUtilClient = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
    
            if not self.testwsname:
                self.testwsname.append(self.create_random_string())
    
            print "upload_assembly self.testwsname[0] " + self.testwsname[0]
    
            try:
                ret = self.wsClient.create_workspace({'workspace': self.testwsname[0]})  #test_ws_name
            except Exception as e:
                #print "ERROR"
                #print(type(e))
                #print(e.args)
                print(e)
                pass
    
            try:
                print "attempt upload"
                print "ftarget " + ftarget
                ref = self.readsUtilClient.upload_assembly(
                    {
                     'wsname': self.testwsname[0],
                     'name': 'filereads1'})
        
                print "upload_assembly"
                print ref
                #self.testobjref = []
                self.testobjref.append(self.testwsname[0] + '/ecoli_assembly')
                #self.testobjdata = []
                self.testobjdata.append(self.dfu.get_objects(
                    {'object_refs': [self.testobjref[0]]}))  #['data'][0]
        
                print "self.testobjdata[0]"
                print self.testobjdata[0]
    
            except Exception as e:
                print e
                pass
    
            print "self.testobjref[0]"
            print self.testobjref[0]