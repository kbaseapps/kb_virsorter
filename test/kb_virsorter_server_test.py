# -*- coding: utf-8 -*-
import unittest
import os
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

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_filter_contigs_ok(self):
        obj_name = "contigset.1"
        contig1 = {'id': '1', 'length': 10, 'md5': 'md5', 'sequence': 'agcttttcat'}
        contig2 = {'id': '2', 'length': 5, 'md5': 'md5', 'sequence': 'agctt'}
        contig3 = {'id': '3', 'length': 12, 'md5': 'md5', 'sequence': 'agcttttcatgg'}
        obj1 = {'contigs': [contig1, contig2, contig3], 'id': 'id', 'md5': 'md5', 'name': 'name', 
                'source': 'source', 'source_id': 'source_id', 'type': 'type'}
        self.getWsClient().save_objects({'workspace': self.getWsName(), 'objects':
            [{'type': 'KBaseGenomes.ContigSet', 'name': obj_name, 'data': obj1}]})
        ret = self.getImpl().filter_contigs(self.getContext(), {'workspace': self.getWsName(), 
            'contigset_id': obj_name, 'min_length': '10'})
        obj2 = self.getWsClient().get_objects([{'ref': self.getWsName()+'/'+obj_name}])[0]['data']
        self.assertEqual(len(obj2['contigs']), 2)
        self.assertTrue(len(obj2['contigs'][0]['sequence']) >= 10)
        self.assertTrue(len(obj2['contigs'][1]['sequence']) >= 10)
        self.assertEqual(ret[0]['n_initial_contigs'], 3)
        self.assertEqual(ret[0]['n_contigs_removed'], 1)
        self.assertEqual(ret[0]['n_contigs_remaining'], 2)

    def test_filter_contigs_err1(self):
        with self.assertRaises(ValueError) as context:
            self.getImpl().filter_contigs(self.getContext(), {'workspace': self.getWsName(), 
                'contigset_id': 'fake', 'min_length': 10})
        self.assertTrue('Error loading original ContigSet object' in str(context.exception))

    def test_filter_contigs_err2(self):
        with self.assertRaises(ValueError) as context:
            self.getImpl().filter_contigs(self.getContext(), {'workspace': self.getWsName(), 
                'contigset_id': 'fake', 'min_length': '-10'})
        self.assertTrue('min_length parameter shouldn\'t be negative' in str(context.exception))

    def test_filter_contigs_err3(self):
        with self.assertRaises(ValueError) as context:
            self.getImpl().filter_contigs(self.getContext(), {'workspace': self.getWsName(), 
                'contigset_id': 'fake', 'min_length': 'ten'})
        self.assertTrue('Cannot parse integer from min_length parameter' in str(context.exception))
        
