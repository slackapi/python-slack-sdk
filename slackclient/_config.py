#! /usr/bin/env python

import sys
import os
import argparse

import yaml

PY3 = sys.version_info[0] == 3

CONF_FILENAMES = ['~/.slackclient.conf']

def get_input(message, prompt=None):
    if prompt is None:
        prompt = '>> '
    if PY3:
        print(message)
        return input(prompt)
    print message
    return raw_input(prompt)
    
class Config(object):
    conf_vars = {
        'TOKEN':{
            'required':True, 
            'prompt_message':'Please enter the API Token for your account', 
        }, 
        'DOMAIN':{'default':'slack.com'}, 
    }
    def __init__(self, **kwargs):
        self.data = {}
        self.filename = kwargs.get('conf_file', self.find_conf_file())
        self.config_mode = kwargs.get('configure')
        if self.filename is None:
            self.filename = os.path.expanduser(CONF_FILENAMES[0])
            self.build_defaults()
        else:
            self.filename = os.path.expanduser(self.filename)
            self.read_conf()
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, item):
        if key in self.data and self.data[key] == item:
            return
        self.data[key] = item
        self.write_conf()
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, item):
        self.set(key, item)
    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        return super(Config, self).__getattr__(attr)
    def build_defaults(self):
        for key, opts in self.conf_vars.items():
            if key in self.data:
                continue
            if opts.get('required') and self.config_mode:
                msg = opts.get('prompt_message', key)
                val = get_input(msg)
            else:
                val = opts.get('default')
            self.data[key] = val
        self.write_conf()
    def read_conf(self):
        with open(self.filename, 'r') as f:
            s = f.read()
        self.data.update(yaml.load(s))
    def write_conf(self):
        s = yaml.dump(self.data, default_flow_style=False)
        with open(self.filename, 'w') as f:
            f.write(s)
    def find_conf_file(self):
        for fn in CONF_FILENAMES:
            fn = os.path.expanduser(fn)
            if os.path.exists(fn):
                return fn

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--configure', dest='configure', action='store_true', 
                   help='Configure Slack Client')
    p.add_argument('-c', dest='conf_file', 
                   help='Config filename (default is ~/.slackclient.conf')
    args, remaining = p.parse_known_args()
    return vars(args)
    
if __name__ == '__main__':
    config = Config(**parse_args())
else:
    config = Config()
