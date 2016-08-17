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
        self.name = 'Logger Module'
        self.identifier = 'tk.red_c0der.logger'
        self.description = 'Provides basic logging functionality'
        self.version = '1.0.0'
        self.target_version = '1.0.0'
        self.target_os = ['osx', 'linux', 'windows', 'ios', 'android']
        self.dependencies = {
            'hooks': [],
            'modules': [],
            'python_modules': []
            }
    
    def load(self, azurite_instance):
        azurite_instance.writecon('ok', 'Logger module was loaded successfully!')
    
    
    @Module.exec_hooks
    def patch_main_helloworld(self, azurite, azurite_instance=None):
        azurite.writecon(azurite_instance, 'info', 'Hello World! (tk.red_c0der.logger)')
    
    def patch_main_runtest(self, azurite, azurite_instance=None):
        azurite.helloworld(azurite_instance=azurite_instance)
    
    
    def patch_main_installer(self, azurite, azurite_instance=None):
        print 'starting installation'
    
    def patch_shell_install(self, shell_instance, args):
        print '!!installer!!'
        print shell_instance.AzuriteInstance
        shell_instance.AzuriteInstance.installer()
    
    #def hook_pre_writecon(self, **kwargs):
    #    pass
    
    #def hook_post_writecon(self, **kwargs):
    #    pass
