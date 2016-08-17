# coding: utf-8

#    Allows import of Hook file
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from Hook import Hook

class CustomHook(Hook):
    def __post_init__(self):
        self.name = 'Hello World Hook'
        self.identifier = 'tk.red_c0der.helloworld'
        self.description = 'My awesome hook!'
        self.version = '1.0.0'
        self.target_version = '1.0.0'
        self.target_os = ['osx', 'linux', 'windows', 'ios', 'android']
        self.dependencies = {
            'hooks': [],
            'modules': [],
            'python_modules': []
            }
            
    def hook_pre_tk_testing_test(self, *args, **kwargs):
        #print 'tk_testing_test prehook'
        pass
    
    def hook_pre_helloworld(self, *args, **kwargs):
        print ''
        print 'Runtest'
        print 'Args.: '+str(args)
        print 'kwargs: '+str(kwargs)
        print ''
    
    def hook_pre_writecon(self, *args, **kwargs):
        #print 'Writecon Pre hook'
        pass
    
    def hook_post_writecon(self, *args, **kwargs):
        #print 'Args.: '+str(args)
        #print 'kwargs: '+str(kwargs)
        pass
    
    
    def hook_pre_all(self, method, *args, **kwargs):
        # Gets called before every method
        #print 'PRE HOOOK'
        #print 'FC: '+method.__name__
        pass
    
    def hook_post_all(self, method, *args, **kwargs):
        # Gets called after all methods
        pass
    
    #def hook_post_writecon(self, **kwargs):
    #    pass

