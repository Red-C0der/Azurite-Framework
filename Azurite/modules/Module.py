# coding: utf-8

import os,sys,inspect
from functools import wraps
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import main


def exec_hooks(func):
    @wraps(func)
    def wrapper(*args, **kw):
        #print 'MODULE HOOK: '+str(func.__name__)
        for metd in main._hooks['pre_all']:
            method(metd, *args, **kw)
        try:
            for metd in main._hooks['pre'][func.__name__]:
                method(metd, *args, **kw)
        except:
            #Do some logging stuff
            pass
        try:
            res = func(*args, **kw)
        finally:
            for metd in main._hooks['post_all']:
                method(metd, *args, **kw)
                
            try:
                for metd in main._hooks['post'][func.__name__]:
                    method(metd, *args, **kw)
            except:
                #Do some logging stuff
                pass
        return res
    return wrapper


class Module:
    # Sets basic information
    def __init__(self):
        self.name = 'MyModule' # Module name
        self.identifier = 'com.myname.mymodule' # Module identifier
        self.description = 'My awesome module!' # A short description
        self.version = '0.0.0' # The version of your module
        self.target_version = '0.0.0' # The version of Azurite your module is build for
        self.target_os = ['osx', 'linux', 'windows', 'ios', 'android'] # Supported operating systems (osx, linux, windows, ios, android)
        self.dependencies = {
            'hooks': [],
            'modules': [],
            'python_modules': []
            } # Insert the hook or module identifiers. For python modules use the pip installation name.
        self.__post_init__()
    
    def __post_init__(self):
        pass
    
    
    # Gets called when the module is loaded
    def load(self, azurite_instance):
        pass
    
    # Gets called when (before) the module is completely unloaded by the system
    def unload(self, azurite_instance):
        pass
    
    
    def test(self):
        print 'hello world'