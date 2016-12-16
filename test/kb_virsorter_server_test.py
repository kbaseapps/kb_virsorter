# -*- coding: utf-8 -*-
import unittest
import os
import shutil
import json
import time
import requests
import random
import string

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
from DataFileUtil.DataFileUtilClient import DataFileUtil

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

        cls.testobjref = []
        cls.testobjdata = []
        cls.testwsname = []

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

        if hasattr(cls, 'testwsname') and len(cls.testwsname) > 0:
            try:
                print('Deleting workspace 2 ' + cls.testwsname[0])
                cls.wsClient.delete_workspace({'workspace': cls.testwsname[0]})
                print('Test workspace 2 was deleted ' + cls.testwsname[0])
            except Exception as e:
                print e

        #if hasattr(cls, 'testobjdata'):
        #    try:
        #        print('Deleting shock data ' + str(len(cls.testobjdata)))
        #        print('Deleting shock data ' + str(len(cls.testobjdata[0]['data'][0])))
        #        print('Deleting shock data ' + str(cls.testobjdata[0]))
        #        node = cls.testobjdata[0]['data'][0]['lib']['file']['id']
        #        cls.delete_shock_node(node)
        #        print('Test shock data was deleted')
        #    except Exception as e:
        #        print e

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
    
    
    def write_file(self, filename, content):
        tmp_dir = self.cfg['scratch']
        file_path = os.path.join(tmp_dir, filename)
        with open(file_path, 'w') as fh1:
            fh1.write(content)
        return file_path

    def test_aaa_upload_to_shock(self):
    
        self.dfUtil = DataFileUtil(os.environ['SDK_CALLBACK_URL'])
        #file_path =  self.write_file('Phage_gene_catalog.tar.gz', 'Test')
                   
        file_path = "/data/Phage_gene_catalog.tar.gz"# os.path.join(tmp_dir, input_file_name)
        print "file_path " + file_path
        
        ret1 = self.dfUtil.file_to_shock(
            {'file_path': file_path})
        
        print str(ret1)
        shock_id = ret1['shock_id']
        
        print "shock_id "+shock_id

    def zzz_test_virsorter_ok(self):
        self.upload_assembly()
    
        params = {}
        params['assembly_ref'] = self.testobjref
        
        result = self.getImpl().run_virsorter(self.getContext(), params)
        print('RESULT run_virsorter:')
        pprint(result)
    
        testresult = [
            {'blah': 'blah', 'bleh': 'bleh'}]
    
        self.assertEqual(sorted(result), sorted(testresult))


    def create_random_string(self):
        N = 20
        return ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def upload_assembly(self):

        if not self.testobjref:
            print "upload_assembly start"
    
            indata = 'U00096.2.fa'
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
                     'name': 'ecolik12'})
        
                print "upload_assembly"
                print ref
                #self.testobjref = []
                self.testobjref.append(self.testwsname[0] + '/ecolik12')
                #self.testobjdata = []
                self.testobjdata.append(self.dfu.get_objects(
                    {'object_refs': [self.testobjref[0]]}))
        
                print "self.testobjdata[0]"
                print self.testobjdata[0]
    
            except Exception as e:
                print e
                pass
    
            print "self.testobjref[0]"
            print self.testobjref[0]