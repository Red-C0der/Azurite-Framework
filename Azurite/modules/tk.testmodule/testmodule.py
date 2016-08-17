# coding: utf-8

#    Allows import of Module file
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
maindir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)
sys.path.insert(0, maindir)


import Module

class CustomModule(Module.Module):
    def __post_init__(self):
        self.name = 'Testing Module'
        self.identifier = 'tk.testing'
        self.description = 'Only used for testing!'
        self.version = '1.0.0'
        self.target_version = '1.0.0'
        self.target_os = ['osx', 'linux', 'windows', 'ios', 'android']
        self.dependencies = {
            'hooks': [],
            'modules': [],
            'python_modules': []
            }
    
    def load(self, azurite_instance):
        azurite_instance.writecon('ok', 'Loaded tk.testing module')
    
    
    @Module.exec_hooks
    def patch_main_tk_testing_test(self, azurite, azurite_instance=None):
        azurite.writecon(azurite_instance, 'info', 'This is a test! (tk.testing)')
    
    class patch_main_Test:
        def __init__(self, azurite_instance=None):
            self.azurite_instance = azurite_instance
            azurite_instance.writecon('info', 'Test class was patched successful!')
        
        @Module.exec_hooks
        def tk_testing_test(self, azurite_instance=None):
            print ('tk_testing_test method got called')