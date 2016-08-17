# coding: utf-8

#    Allows import of Hook file
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from Hook import Hook

class CustomHook(Hook):
    def __post_init__(self):
        self.name = 'Testing Hook'
        self.identifier = 'tk.testing'
        self.description = 'My awesome hook!'
        self.version = '1.0.0'
        self.target_version = '1.0.0'
        self.target_os = ['osx', 'linux', 'windows', 'ios', 'android']
        self.dependencies = {
            'hooks': [],
            'modules': [],
            'python_modules': []
            }
    
    def hook_pre_helloworld(self, *args, **kwargs):
        print ''
        print '             TESTHOOK is running!'
        print ''
    
