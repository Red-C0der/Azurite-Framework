# coding: utf-8
# Author: Red_C0der

import os
import sys
import inspect
import cmd
from functools import wraps
from xml.etree import ElementTree
import hashlib, uuid
import getpass
import pygithub3
from git import Repo
import imp
import shutil
import time


_hook_instances = {}
_hooks = {
    'pre': {},
    'post': {},
    'pre_all': [],
    'post_all': [],
    }
_module_instances = {}
#self.modules = {}


def exec_hooks(func):
    @wraps(func)
    def wrapper(*args, **kw):
        #print '    Pre Hook main.py: '+str(func.__name__)
        for method in _hooks['pre_all']:
            method(func, *args, **kw)
        try:
            for method in _hooks['pre'][func.__name__]:
                method(*args, **kw)
        except:
            #Do some logging stuff
            pass
        try:
            res = func(*args, **kw)
        finally:
            #print '    Post Hook main.py: '+str(func.__name__)
            for method in _hooks['post_all']:
                method(func, *args, **kw)
                
            try:
                for method in _hooks['post'][func.__name__]:
                    method(*args, **kw)
            except:
                #Do some logging stuff
                pass
        return res
    return wrapper    


class StartUp:
    def __init__(self, DEBUG=False):
        if DEBUG: self.writecon('debug', 'Created StartUp instance')
        
        self.writecon('', 'Setting up enviroment variables')
        
        #   Setting Debug value
        self.DEBUG = DEBUG
        
        #   Setting Azurite version
        self.version = '1.0.0'
        if DEBUG: self.writecon('debug', 'StartUp.version = '+str(self.version))
        
        #   Setting operating system
        self.os = 'linux' if sys.platform == 'linux2' else 'windows' if sys.platform == 'wind32' else 'windows' if sys.platform == 'cygwin' else 'osx' if sys.platform == 'darwin' else 'ios' if sys.platform == 'iphoneos' else None
        
        if DEBUG: self.writecon('debug', 'sys.platform = '+str(sys.platform))
        if DEBUG: self.writecon('debug', 'StartUp.os = '+str(self.os))
        
        #   Creating Hook and ModuleLoader Instances
        self.HookLoaderInstance = self.HookLoader(self, DEBUG=self.DEBUG)
        self.ModuleLoaderInstance = self.ModuleLoader(self, DEBUG=self.DEBUG)
        
        self.writecon('ok', 'Set up enviroment variables')


    class HookLoader:
        hooks = {}

        def __init__(self, StartupInstance, DEBUG=False):
            
            #   Setting StartUp instance
            self.StartupInstance = StartupInstance
            
            if DEBUG: self.StartupInstance.writecon('debug', 'HookLoader instance was created')
            if DEBUG: self.StartupInstance.writecon('debug', 'self.StartupInstance = '+str(self.StartupInstance))
            
            #   Setting Debug value
            self.DEBUG = DEBUG


        #    Loads hooks from hooks directory
        def loadhooks(self):
            self.StartupInstance.writecon('', 'Loading hooks')

            hookdirs = []
            hooks = {}

            self.StartupInstance.writecon('', 'Getting directories in hooks dir', 1)
            #    Getting directories in hooks dir
            for item in os.listdir("./hooks"):
                if not item.endswith('.py'):
                    hookdirs.append(item)
            
            self.StartupInstance.writecon('ok', 'Got directories in hooks dir', 1)
            if self.DEBUG: self.StartupInstance.writecon('debug', 'hookdirs = '+str(hookdirs))
  
            self.StartupInstance.writecon('', 'Importing hooks', 1)
            #    Importing hooks
            for dir in hookdirs:
                self.StartupInstance.writecon('', 'Working on hook: '+str(dir), 2)
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'dir = '+str(dir))
                
                #    Generate path to hook.py file
                hookpath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/hooks/'+dir+'/'
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'hookpath = '+str(hookpath))

                #    Inserting path to make import possible
                sys.path.insert(0,hookpath)

                #   Executing info data
                info_file = open(hookpath+'info.py', 'r')
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'info_file = '+str(info_file))
                
                info_data = info_file.read()
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'info_data = '+str(info_data))
                
                exec info_data
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'Executed info data!')
	            
	            
                #    Import module.py
                hook = __import__(hook_file)
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'hook = '+str(hook))
                
                #   Getting CustomHook class
                HookInstance = hook.CustomHook()
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'HookInstance = '+str(HookInstance))
                
                #   Deleting hook object
                del hook
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'Deleted hook object!')
                
                #    Saving hook class with identifier as key
                if HookInstance.identifier not in hooks.keys():
                    self.hooks[HookInstance.identifier] = HookInstance
                else:
                    self.StartupInstance.writecon('error', 'Dublicated identifier! ['+identifier+'] Ignoring hook!', 3)
	            
                #    Removing path
                sys.path.remove(hookpath)
                
                self.StartupInstance.writecon('ok', 'Finished hook: '+str(dir), 2)
	        
            if self.DEBUG: self.StartupInstance.writecon('debug', 'self.hooks = '+str(self.hooks))
	        
            self.StartupInstance.writecon('', 'Performing first compatability checks', 3)
            #    Checking hook compatability and unloading unsupported hooks
            for identifier in self.hooks.keys():
                self.StartupInstance.writecon('', 'Checking hook: '+str(identifier), 4)
                hook = self.hooks[identifier]
                if self.DEBUG: self.StartupInstance.writecon('debug', 'hook = '+str(hook))
	            
                #   This gets changed based on compatability
                compatible = True
	            
                #    Comapring versions
                if self.DEBUG: self.StartupInstance.writecon('debug', 'hook.target_version = '+str(hook.target_version))
                if self.StartupInstance.version > hook.target_version:
                    self.StartupInstance.writecon('warning', 'Hook is outdated and may not function correctly!', 5)
                elif self.StartupInstance.version < hook.target_version:
                    self.StartupInstance.writecon('warning', 'Hook is made for a future version of Azurite and may not function correctly!', 5)
                elif self.StartupInstance.version == hook.target_version:
                    self.StartupInstance.writecon('ok', 'Hook is fully compatible with current Azurite version ('+str(self.StartupInstance.version)+')', 5)
	            
	            
                #    Comparing os
                if self.DEBUG: self.StartupInstance.writecon('debug', 'hook.target_os = '+str(hook.target_os))
                if self.StartupInstance.os not in hook.target_os:
                    self.StartupInstance.writecon('error', 'Hook is not compatible with your operating system! ('+str(self.StartupInstance.os)+') Unloading it!', 5)
                    compatible = False
                else:
                    self.StartupInstance.writecon('ok', 'Hook is compatible with your operating system ('+str(self.StartupInstance.os)+')', 5)
                
	            
                self.StartupInstance.writecon('ok', 'Checked hook', 4)
	            
                #    Add to global hook dict if compatible
                if compatible:
                    self.StartupInstance.writecon('', 'Adding hook for furture checks', 4)
                    _hook_instances[identifier] = hook
            
                self.StartupInstance.writecon('ok', 'Finished first compatability check', 3)
                self.StartupInstance.writecon('ok', 'Finished work on hook: '+str(identifier), 2)
            
            if self.DEBUG: self.StartupInstance.writecon('debug', '_hook_instances = '+str(_hook_instances))
            
            self.StartupInstance.writecon('ok', 'Imported hooks', 1)
            self.StartupInstance.writecon('ok', 'Loaded hooks')
            
            
                

    class ModuleLoader:
        modules = {}
        
        def __init__(self, StartupInstance, DEBUG=False):
        
            #   Setting StartupInstance
            self.StartupInstance = StartupInstance
            
            if DEBUG: self.StartupInstance.writecon('debug', 'ModuleLoader Instance was created!')
            if DEBUG: self.StartupInstance.writecon('debug', 'self.StartupInstance = '+str(self.StartupInstance))
	        
            #   Setting Debug value
            self.DEBUG = DEBUG
        
        
        #    Loads modules from modules directory
        def loadmodules(self):
            self.StartupInstance.writecon('', 'Loading modules')
            
            moduledirs = []
            modules = {}
            warnings = {}
            
            self.StartupInstance.writecon('', 'Getting directories in modules dir', 1)
            #    Getting directories in modules dir
            for item in os.listdir("./modules"):
                if not item.endswith('.py'):
                    moduledirs.append(item)
                    
            self.StartupInstance.writecon('ok', 'Got directories in modules dir', 1)
            if self.DEBUG: self.StartupInstance.writecon('debug', 'moduledirs = '+str(moduledirs))
            
            
            self.StartupInstance.writecon('', 'Importing modules', 1)
            
            #    Importing modules
            for dir in moduledirs:
                self.StartupInstance.writecon('', 'Working on module: '+str(dir), 2)
                if self.DEBUG: self.StartupInstance.writecon('debug', 'dir = '+str(dir))
                
                #    Generate path to module.py file
                modulepath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/modules/'+dir+'/'
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'modulepath = '+str(modulepath))
                
                #    Inserting path to make import possible
                sys.path.append(modulepath)
                
                
                #   Executing info data
                info_file = open(modulepath+'info.py', 'r')
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'info_file = '+str(info_file))
                
                info_data = info_file.read()
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'info_data = '+str(info_data))
                
                exec info_data
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'Executed info_data!')
                
                
                #    Import module.py
                module = __import__(module_file)
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'module = '+str(module))
                
                ModuleInstance = module.CustomModule()
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'ModuleInstance = '+str(ModuleInstance))
                
                del module
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'Deleted module object')
                
                
                #    Removing path
                sys.path.remove(modulepath)
                
                
                #    Saving module class with identifier as key
                if ModuleInstance.identifier in modules.keys():
                    self.StartupInstance.writecon('error', 'Dublicated identifier! ['+ModuleInstance.identifier+'] Ignoring module!', 3)
                else:
                    modules[ModuleInstance.identifier] = ModuleInstance
                
                self.StartupInstance.writecon('ok', 'Finished work on module: '+str(dir), 2)
                
            if self.DEBUG: self.StartupInstance.writecon('debug', 'modules = '+str(modules))
            
            self.StartupInstance.writecon('', 'Performing first compatability checks', 3)
            
            #    Checking hook compatability and unloading unsipported hooks
            for identifier in modules.keys():
                self.StartupInstance.writecon('', 'Checking module: '+str(identifier), 4)
                module = modules[identifier]
                
                if self.DEBUG: self.StartupInstance.writecon('debug', 'module = '+str(module))
                
                compatible = True
                warnings[identifier] = []
                
                #    Comapring versions
                if self.DEBUG: self.StartupInstance.writecon('debug', 'module.target_version = '+str(module.target_version))
                if self.StartupInstance.version > module.target_version:
                    self.StartupInstance.writecon('warning', 'Module is outdated and may not function correctly!', 5)
                elif self.StartupInstance.version < module.target_version:
                    self.StartupInstance.writecon('warning', 'Module is made for a future version if Azurite and may not work correctly!', 5)
                elif self.StartupInstance.version == module.target_version:
                    self.StartupInstance.writecon('ok', 'Module is compatible with current Azurite version ('+str(self.StartupInstance.version)+')', 5)
                
            
                #    Comparing os
                if self.DEBUG: self.StartupInstance.writecon('debug', 'module.target_os = '+str(module.target_os))
                if self.StartupInstance.os not in module.target_os:
                    self.StartupInstance.writecon('error', 'Module is not compatible with your current os! ('+str(self.StartupInstance.os)+') Unloading it!', 5)
                else:
                    self.StartupInstance.writecon('ok', 'Module is compatible with your operating system ('+str(self.StartupInstance.os)+')', 5)
                
                
                #    Add to global module dict if compatible
                if compatible:
                    self.StartupInstance.writecon('', 'Adding module for furture checks', 5)
                    _module_instances[identifier] = module
                
                self.StartupInstance.writecon('ok', 'Checked module: '+str(identifier), 4)
            
            if self.DEBUG: self.StartupInstance.writecon('debug', '_module_instances = '+str(_module_instances))    
            
            self.StartupInstance.writecon('ok', 'Imported modules', 1)
            
            self.StartupInstance.writecon('ok', 'Loaded modules')
    
    def cross_dependencies_check(self):
        self.writecon('', 'Starting cross dependencies check')
        
        if self.DEBUG: self.writecon('debug', '_hook_instances = '+str(_hook_instances))
        if self.DEBUG: self.writecon('debug', '_module_instances = '+str(_module_instances))
        
        delhooks = []
        delmodules = []
        
        # Hooks
        if self.DEBUG: self.writecon('debug', 'Checking hooks')
        for identifier in _hook_instances:
            self.writecon('', 'Checking hook: '+str(identifier), 1)
            hook = _hook_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'hook = '+str(hook))
            
            compatible = True
            
            if self.DEBUG: self.writecon('debug', 'hook.dependencies = '+str(hook.dependencies))
            
            self.writecon('', 'Checking Python modules', 2)
            # Python Modules
            for module in hook.dependencies['python_modules']:
                try:
                    __import__(module)
                    self.writecon('ok', 'Python module installed: '+str(module), 3)
                except:
                    self.writecon('error', 'Python module missing: '+str(module), 3)
                    compatible = False
            self.writecon('ok', 'Checked Python modules', 2)
            
            
            self.writecon('', 'Checking hooks', 2)
            # Hooks
            for dep_hook in hook.dependencies['hooks']:
                if dep_hook not in _hook_instances.keys():
                    self.writecon('error', 'Hook is missing: '+str(dep_hook), 3)
                    compatible = False
                else:
                    self.writecon('ok', 'Hook is loaded: '+str(dep_hook), 3)
            self.writecon('ok', 'Checked hooks', 2)
            
            
            self.writecon('', 'Checking modules', 2)
            # Modules
            for dep_module in hook.dependencies['modules']:
                if dep_module not in _module_instances.keys():
                    self.writecon('error', 'Module is missing: '+str(dep_module), 3)
                    compatible = False
                else:
                    self.writecon('ok', 'Module is loaded: '+str(dep_module), 3)
            self.writecon('ok', 'Checked modules', 2)
            
            
            # Checking compatability
            if not compatible:
                delhooks.append(identifier)
                self.writecon('warning', 'Hook failed cross compatability check! Ths could affect other hooks and modules!', 1)
            else:
                self.writecon('ok', 'Hook succeeded the cross compatability check! Loading hook into system: '+str(identifier), 1)
        
        for identifier in delhooks:
            del _hook_instances[identifier]
            if self.DEBUG: self.writecon('debug', 'Deleted _hook_instances['+str(identifier)+'] !')
        
        if self.DEBUG: self.writecon('debug', '_hook_instances = '+str(_hook_instances))
        
        if self.DEBUG: self.writecon('debug', 'Checking modules')
        # Modules
        for identifier in _module_instances:
            self.writecon('', 'Checking module: '+str(identifier), 1)
            module = _module_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'module = '+str(module))
            
            compatible = True
            
            self.writecon('', 'Checking Python modules', 2)
            
            if self.DEBUG: self.writecon('debug', 'module.dependencies = '+str(module.dependencies))
            
            # Python Modules
            for py_module in module.dependencies['python_modules']:
                try:
                    __import__(py_module)
                    self.writecon('ok', 'Python module loaded: '+str(py_module), 3)
                except:
                    self.writecon('error', 'Python module not installed: '+str(py_module), 3)
                    compatible = False
            self.writecon('ok', 'Checked Python modules', 2)
            
            
            self.writecon('', 'Checking hooks', 2)
            # Hooks
            for dep_hook in module.dependencies['hooks']:
                if dep_hook not in _hook_instances.keys():
                    self.writecon('error', 'Hook is missing: '+str(dep_hook), 3)
                    compatible = False
                else:
                    self.writecon('ok', 'Hook is loaded: '+str(dep_hook), 3)
            self.writecon('ok', 'Checked hooks', 2)
            
            
            self.writecon('', 'Checking modules', 2)
            # Modules
            for dep_module in module.dependencies['modules']:
                if dep_module not in _module_instances.keys():
                    self.writecon('error', 'Module is missing: '+str(dep_module), 3)
                    compatible = False
                else:
                    self.writecon('ok', 'Module is loaded: '+str(dep_module), 3)
            self.writecon('ok', 'Checked modules', 2)
            
            
            # Checking compatability
            if not compatible:
                delmodules.append(identifier)
                self.writecon('warning', 'Module failed cross compatability check! Ths could affect other hooks and modules!', 1)
            else:
                self.writecon('ok', 'Module succeeded the cross compatability check! Loading Module into system: '+str(identifier), 1)
            
            if self.DEBUG: self.writecon('debug', '_module_instances = '+str(_module_instances))
        
        for identifier in delmodules:
            del _module_instances[identifier]
            if self.DEBUG: self.writecon('debug', 'Deleted _module_instances['+str(identifier)+'] !')
        
        self.writecon('ok', 'Cross dependencie check was finished successfully!')
	        
    def final_load_hooks(self):
        self.writecon('', 'Making final changes to fully load hooks')
        
        for identifier in _hook_instances:
            self.writecon('', 'Working on hook instance: '+str(identifier), 1)
            hook_instance = _hook_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'hook_instance = '+str(hook_instance))
            
            self.writecon('', 'Getting hook methods from current module', 2)
            #    Getting methods from class
            methods = inspect.getmembers(hook_instance, predicate=inspect.ismethod)
            self.writecon('ok', 'Got methods', 2)
            if self.DEBUG: self.writecon('debug', 'methods = '+str(methods))
            
            self.writecon('', 'Applying methods', 2)
            
            for name, method in methods:
                if self.DEBUG: self.writecon('debug', 'Checking azurite_method: '+str(name))
                if name == 'hook_pre_all':
                    self.writecon('', 'Applying pre_all hook', 3)
                    
                    _hooks['pre_all'].append(method)
                    
                    self.writecon('ok', 'Applied pre_all hook', 3)
                elif name == 'hook_post_all':
                    self.writecon('', 'Applying post_all hook', 3)
                    
                    _hooks['post_all'].append(method)
                    
                    self.writecon('ok', 'Applied post_all hook', 3)
                else:
                    if 'hook_pre_' in name:
                        method_name = name[9:]
                        self.writecon('', 'Applying method: '+method_name, 3)
                    
                        _hooks['pre'][method_name] = []
                    
                        _hooks['pre'][method_name].append(method)
                    
                        self.writecon('ok', 'Applied method: '+str(method_name), 3)
                    elif 'hook_post_' in name:
                        method_name = name[10:]
                        self.writecon('', 'Applying method: '+method_name, 3)
                    
                        _hooks['post'][method_name] = []
                    
                        _hooks['post'][method_name].append(method)
                    
                        self.writecon('ok', 'Applied method: '+str(method_name), 3)
                
            self.writecon('ok', 'Finished applying methods', 2)
            
            self.writecon('ok', 'Applied all methods from hook: '+str(identifier), 1)
            
        self.writecon('ok', 'Finished final changes! Hooks loaded successfully!')


	
    def patch_azurite(self):
        self.writecon('', 'Patching main Azurite class')
        for identifier in _module_instances:
            self.writecon('', 'Applying patches from: '+str(identifier), 1)
            module = _module_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'module = '+str(module))


            self.writecon('', 'Getting method and classes from current module', 2)
            
            #   Getting methods and classes
            methods = inspect.getmembers(module, predicate=inspect.ismethod)
            self.writecon('ok', 'Got methods', 2)
            
            classes = inspect.getmembers(module, predicate=inspect.isclass)
            self.writecon('ok', 'Got classes', 2)
            
            if self.DEBUG: self.writecon('debug', 'methods = '+str(methods))
            if self.DEBUG: self.writecon('debug', 'classes = '+str(classes))
            
            
            patchmethods = 0
            for name, method in methods:
                if name != '__init__' and name != '__post__init__' and name != 'load' and name != 'unload' and name[:12] != 'patch_shell_':
                    patchmethods = patchmethods+1
            if self.DEBUG: self.writecon('debug', 'patchmethods = '+str(patchmethods))
            
            patchclasses = 0
            for name, method in classes:
                if name[:11] == 'patch_main_':
                    patchclasses = patchclasses+1
            if self.DEBUG: self.writecon('debug', 'patchclasses = '+str(patchclasses))

            if patchmethods < 1:
                self.writecon('info', 'Module '+str(identifier)+' does not contain any main patch methods!', 2)
            else:
                self.writecon('', 'Patching methods', 2)
                for name, method in methods:
                    if self.DEBUG: self.writecon('debug', 'Current method: '+str(name))
                    if 'patch_main_' in name:
                        method_name = name[11:]
                        
                        if self.DEBUG: self.writecon('debug', 'method_name = '+str(method_name))
                        
                        self.writecon('', 'Patching method: '+method_name, 3)
                    
                        setattr(Azurite, method_name, classmethod(method))
                        
                        if self.DEBUG: self.writecon('debug', 'setattr returned 0 errors!')
                        
                        self.writecon('ok', 'Patched method: '+str(method_name), 3)
            
            
            if patchclasses < 1:
                self.writecon('info', 'Module '+str(identifier)+' does not contain any main patch classes!', 2)
            else:
                self.writecon('', 'Patching classes', 2)
                for name, cls in classes:
                    if self.DEBUG: self.writecon('debug', 'Current class: '+str(name))
                    if 'patch_main_' in name:
                        class_name = name[11:]
                        
                        if self.DEBUG: self.writecon('debug', 'class_name = '+str(class_name))
                        
                        self.writecon('', 'Patching class: '+class_name, 3)
                    
                        setattr(Azurite, class_name, cls)
                        
                        if self.DEBUG: self.writecon('debug', 'setattr returned 0 errors!')
                        
                        self.writecon('ok', 'Patched class: '+str(class_name), 3)


                self.writecon('ok', 'Finished patching', 2)
                
            self.writecon('ok', 'Applied all patches from module: '+str(identifier), 1)
	        
        self.writecon('ok', 'Patched main Azurite class')
        
        
    def patch_shell(self):
        self.writecon('', 'Patching Azurite shell class')
        for identifier in _module_instances:
            self.writecon('', 'Applying patches from: '+str(identifier), 1)
            module = _module_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'module = '+str(module))
            
            self.writecon('', 'Getting methods and classes from current module', 2)
            
            #   Getting methods and classes
            methods = inspect.getmembers(module, predicate=inspect.ismethod)
            self.writecon('ok', 'Got methods', 2)
            
            classes = inspect.getmembers(module, predicate=inspect.isclass)
            self.writecon('ok', 'Got classes', 2)
            
            if self.DEBUG: self.writecon('debug', 'methods = '+str(methods))
            if self.DEBUG: self.writecon('debug', 'classes = '+str(classes))
            
            
            patchmethods = 0
            for name, method in methods:
                if name != '__init__' and name != '__post__init__' and name != 'load' and name != 'unload' and name[:12] != 'patch_main_':
                    patchmethods = patchmethods+1
            if self.DEBUG: self.writecon('debug', 'patchmethods = '+str(patchmethods))
            
            patchclasses = 0
            for name, method in classes:
                if name[:12] == 'patch_shell_':
                    patchclasses = patchclasses+1
            if self.DEBUG: self.writecon('debug', 'patchclasses = '+str(patchclasses))

            if patchmethods < 1:
                self.writecon('info', 'Module '+str(identifier)+' does not contain any shell patch methods!', 2)
            else:
                self.writecon('', 'Patching methods', 2)
                for name, method in methods:
                    if self.DEBUG: self.writecon('debug', 'Current method: '+str(name))
                    if 'patch_shell_' in name:
                        method_name = name[12:]
                        
                        if self.DEBUG: self.writecon('debug', 'method_name = '+str(method_name))
                        
                        self.writecon('', 'Patching method: '+method_name, 3)
                    
                        setattr(AzuriteShell, 'do_'+str(method_name), classmethod(method))
                        
                        if self.DEBUG: self.writecon('debug', 'setattr returned 0 errors!')
                        
                        self.writecon('ok', 'Patched method: '+str(method_name), 3)
            
            
            if patchclasses < 1:
                self.writecon('info', 'Module '+str(identifier)+' does not contain any shell patch classes!', 2)
            else:
                self.writecon('', 'Patching classes', 2)
                for name, cls in classes:
                    if self.DEBUG: self.writecon('debug', 'Current class: '+str(name))
                    if 'patch_shell_' in name:
                        class_name = name[12:]
                        
                        if self.DEBUG: self.writecon('debug', 'class_name = '+str(class_name))
                        
                        self.writecon('', 'Patching class: '+class_name, 3)
                    
                        setattr(AzuriteShell, class_name, cls)
                        
                        if self.DEBUG: self.writecon('debug', 'setattr returned 0 errors!')
                        
                        self.writecon('ok', 'Patched class: '+str(class_name), 3)
            
                self.writecon('ok', 'Finished patching', 2)
                
            self.writecon('ok', 'Applied all patches from module: '+str(identifier), 1)
            
        self.writecon('ok', 'Patched Azurite shell class')
        
    def writecon(self, state, text, subthread=0):
        try:
            import termcolor
            from colored import fg, bg, attr, style
            compatability_mode = False
        except:
            compatability_mode = True
    
    
        if not compatability_mode:
            import time
            import termcolor
            from colored import fg, bg, attr, style
            
            if subthread == 0:
                subthread_spacing = ''
            elif subthread == 1:
                subthread_spacing = '    - '
            elif subthread == 2:
                subthread_spacing = '        - '
            elif subthread == 3:
                subthread_spacing = '            - '
            elif subthread == 4:
                subthread_spacing = '                - '
            elif subthread == 5:
                subthread_spacing = '                    - '
            
            if state == "":
                formatted_text = "[" + termcolor.colored("....", "cyan", attrs=["bold"]) + "]   " + text
            if state == "ok":
                formatted_text = "[ " + termcolor.colored("OK", "green", attrs=["bold"]) + " ]   " + text #termcolor.colored(text, "green", attrs=["bold"]))
            if state == "error":
                formatted_text = "[" + termcolor.colored("ERROR", "red", attrs=["blink", "bold"]) + "]  " + termcolor.colored(text, "red", attrs=["bold"])
            if state == "warning":
                formatted_text = "[" + fg(208) + attr("bold") + attr("blink") + "WARN" + style.RESET + "]   " + fg(208) + attr("bold") + text + style.RESET
            if state == "info":
                formatted_text = "[" + termcolor.colored("INFO", "cyan", attrs=["bold"]) + "]   " + termcolor.colored(text, "cyan", attrs=["bold"])
            if state == "debug":
                formatted_text = "[" + termcolor.colored("DEBUG", "magenta", attrs=["bold"]) + "]  " + termcolor.colored(text, "magenta", attrs=["bold"])
            if state == "sys":
                formatted_text = "[" + termcolor.colored("SYSTEM", "blue", attrs=["bold"]) + "] " + termcolor.colored(text, "blue", attrs=["bold"])
            
            sys.stdout.write(subthread_spacing)
            sys.stdout.flush()
            for char in formatted_text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.00001)
            sys.stdout.write('\n')
            return True
        else:
            import time
            
            #    Run in compatabiliy mode
            if subthread == 0:
                subthread_spacing = ''
            elif subthread == 1:
                subthread_spacing = '    - '
            elif subthread == 2:
                subthread_spacing = '        - '
            elif subthread == 3:
                subthread_spacing = '            - '
            elif subthread == 4:
                subthread_spacing = '                - '
            elif subthread == 5:
                subthread_spacing = '                    - '
            
            if state == "":
                formatted_text = "[....]   " + text
            if state == "ok":
                formatted_text = "[ OK ]   " + text
            if state == "error":
                formatted_text = "[ERROR]  " + text
            if state == "warning":
                formatted_text = "[WARN]   " + text
            if state == "info":
                formatted_text = "[INFO]   " + text
            if state == "debug":
                formatted_text = "[DEBUG]  " + text
            if state == "sys":
                formatted_text = "[SYSTEM] " + text
            
            sys.stdout.write(subthread_spacing)
            sys.stdout.flush()
            for char in formatted_text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.0001)
            sys.stdout.write('\n')
            return True


class AzuriteShell(cmd.Cmd):
    intro = '''


 /=============\\
| Azurite Shell |
 \=============/
 root passwd: 123
 
 
    '''
    prompt = '> '
    
        
    def precmd(self, line):
        if self.AzuriteInstance.current_user == None and 'login' not in line:
            print("Please login first using the login command!")
            return 'pass'
        else:
            return cmd.Cmd.precmd(self, line)
    
    def do_pass(self, *args):
        pass
    def do_EOF(self, line):
        return True
    
    
    def do_login(self, *args):
        args = args[0].split(' ')

        print('')
        username = raw_input('Username: ')
        password = getpass.getpass(prompt='Password: ')
        
        if self.AzuriteInstance.authenticate(username, password):
            self.AzuriteInstance.writecon('ok', 'Authentication was successfull!')
            self.AzuriteInstance.current_user = username
            self.prompt = username+'@localhost$ '
            print('')
        else:
            self.AzuriteInstance.writecon('error', 'Username or password is not correct!')
            return
    def help_login(self):
        print("usage: login")
        print("       Requests username and password to log you in")
    
    
    def do_passwd(self, *args):
        args = args[0].split(' ')

        try:
            username = args[0]
            if username == '':
                self.AzuriteInstance.writecon('error', 'Please provide a username after passwd!')
                self.help_passwd()
                return
        except:
            self.AzuriteInstance.writecon('error', 'Please provide a username after passwd!')
            self.help_passwd()
            return
        
        print('')
        #print('Enter old password for user '+str(username)+':')
        oldpassword = getpass.getpass(prompt='Old Password: ')
        
        print('')
        #print('Enter new password for user '+str(username)+':')
        newpassword = getpass.getpass(prompt='New Password: ')
        
        print('')
        #print('Enter new password again to confirm:')
        confirmpassword = getpass.getpass(prompt='Confirm new Password:')
        
        if newpassword != confirmpassword:
            self.AzuriteInstance.writecon('error', 'Password are not the same!')
            self.help_passwd()
        else:
            ret = self.AzuriteInstance.changepassword(username, oldpassword, newpassword)
            if ret is True:
                self.AzuriteInstance.writecon('ok', 'Password changes successfuly!')
            else:
                self.AzuriteInstance.writecon('error', ret)
    def help_passwd(self, *args):
        print("usage: passwd <username>")
        print("       Changes password for user <username>")
    
    
    def do_shutdown(self, *args):
        args = args[0].split(' ')
        
        if '-now' in args:
            self.AzuriteInstance.writecon('info', 'Initiating shutdown sequence!')
            self.AzuriteInstance.shutdown()
            return
        elif '-t' in args:
            try:
                pos = args.index('-t')
                waittime = args[pos+1]
            except:
                self.AzuriteInstance.writecon('error', 'No time specified after -t argument!')
                self.help_shutdown()
                return
            
            if not waittime.isdigit():
                self.AzuriteInstance.writecon('error', 'Waittime argument is no integer! ('+str(waittime)+')')
                return
            else:
                self.AzuriteInstance.writecon('', 'Waiting '+str(waittime)+' seconds...')
                import time
                waittime = int(waittime)
                i = 0
                for i in range(waittime+1):
                    if i >= waittime-9:
                        print waittime-i
                        if waittime-i == 0:
                            self.AzuriteInstance.writecon('info', 'Initiating shutdown sequence!')
                            self.AzuriteInstance.shutdown()
                    time.sleep(1)
        else:
            self.help_shutdown()
            return
    def help_shutdown(self):
        print('usage: shutdown [ <args> ]')
        print('       Safely shuts down the framework and all loaded hooks and modules')
        print('')
        print('Args:')
        print('       -now              -   Immediately starts the shutdown sequence')
        print('       -t (time in sec)  -   Initiates the shutdown sequence after the specified')
        print('                               ammount of time')
      
    def do_apek(self, *args):
        args = args[0].split(' ')

        if '-install' in args:
            try:
                pos = args.index('-install')
                identifier = args[pos+1]
            except:
                self.AzuriteInstance.writecon('error', 'Please provide an identifier after -install')
                self.help_apek()
                return
            
            self.AzuriteInstance.writecon('', 'Searching AzuriteFramework Github repository')
            
            gh = pygithub3.Github()
            repositories = gh.repos.list_by_org(org='AzuriteFramework').all()
            for repo in repositories:
                if repo.name[:8] == 'package_':
                    repo_identifier = repo.name[8:]
                    if repo_identifier == identifier:
                        self.AzuriteInstance.writecon('ok', 'Finished searching')
                        self.AzuriteInstance.writecon('ok', 'Found repo: '+str(repo.git_url))
                        self.AzuriteInstance.writecon('', 'Starting installation')
                        self.AzuriteInstance.writecon('', 'Formatting git url', 1)
                        
                        giturl = repo.git_url[:-4]
                        
                        self.AzuriteInstance.writecon('ok', 'Formatted url', 1)
                        self.AzuriteInstance.writecon('', 'Removing old package data', 1)
                        
                        os.system('rm -rf ./tmp/package_'+str(identifier))
                        
                        self.AzuriteInstance.writecon('ok', 'Removed old data', 1)
                        self.AzuriteInstance.writecon('', 'Cloning github repo into tmp dir', 1)
                        
                        Repo.clone_from(giturl, './tmp/package_'+str(identifier))
                        
                        self.AzuriteInstance.writecon('ok', 'Cloned github repo', 1)
                        self.AzuriteInstance.writecon('', 'Checking compatability', 1)
                        
                        compatible = True
                        
                        self.AzuriteInstance.writecon('', 'Loading info data', 2)
                        
                        info = imp.load_source('info', './tmp/package_'+str(identifier)+'/info.py')
                        
                        self.AzuriteInstance.writecon('ok', 'Loaded info data', 2)
                        self.AzuriteInstance.writecon('', 'Checking version', 2)
                        
                        version = info.target_version
                        
                        if self.AzuriteInstance.version < version:
                            self.AzuriteInstance.writecon('warning', 'This package is made for a later version of Azurite and might not function properly! ('+str(version)+') Consider updating', 2)
                        elif self.AzuriteInstance.version > version:
                            self.AzuriteInstance.writecon('warning', 'The package is outdated and might not function properly!', 2)
                        else:
                            self.AzuriteInstance.writecon('ok', 'Package is compatible with your current Azurite version ('+str(self.AzuriteInstance.version)+')', 2)
                        
                        self.AzuriteInstance.writecon('', 'Checking operating system', 2)
                        
                        if self.AzuriteInstance.os not in info.target_os:
                            self.AzuriteInstance.writecon('error', 'Package is not compatible with your operating system ('+str(self.AzuriteInstance.os)+')', 2)
                            compatible = False
                        else:
                            self.AzuriteInstance.writecon('ok', 'Package is compatible with your operating system ('+str(self.AzuriteInstance.os)+')', 2)
                        
                        if compatible:
                            self.AzuriteInstance.writecon('', 'Checking dependencies', 2)
                            self.AzuriteInstance.writecon('', 'Checking Python modules', 3)
                            
                            for pymodule in info.dependencies['python_modules']:
                                try:
                                    __import__(pymodule)
                                except:
                                    self.AzuriteInstance.writecon('error', 'Python module is not installed: '+str(pymodule)+'! Package is not compatible!', 3)
                                    compatible = False
                                    continue
                            
                            if compatible:
                                self.AzuriteInstance.writecon('ok', 'Checked Python modules', 3)
                                self.AzuriteInstance.writecon('', 'Checking dependencie packages', 3)
                                
                                for package in info.dependencies['packages']:
                                    if package not in self.AzuriteInstance.loaded_packages:
                                        self.AzuriteInstance.writecon('error', 'Package '+str(package)+' is not installed or loaded!', 3)
                                        compatible = False
                                        continue
                                
                                if compatible:
                                    self.AzuriteInstance.writecon('ok', 'Checked dependencie packages', 3)
                                    self.AzuriteInstance.writecon('ok', 'Checked dependencies', 2)
                                    self.AzuriteInstance.writecon('ok', 'Checked compatability', 1)
                                    self.AzuriteInstance.writecon('info', 'Package is compatible! Installing it', 1)
                                    self.AzuriteInstance.writecon('', 'Deleting old files from package', 1)
                        
                                    os.system('rm -rf ./packages/'+str(identifier))
                        
                                    self.AzuriteInstance.writecon('ok', 'Deleted old files', 1)
                                    self.AzuriteInstance.writecon('', 'Moving package from tmp dict to packages dir', 1)
                        
                                    os.system('mv ./tmp/package_'+str(identifier)+' ./packages/'+str(identifier))
                        
                                    self.AzuriteInstance.writecon('ok', 'Moved package', 1)
                                    self.AzuriteInstance.writecon('', 'Executing uninstall.py file in package', 1)
                
                                    exists = False
                                    for item in os.listdir('./packages/'+str(identifier)):
                                        if item == 'install.py':
                                            exists = True
                
                                    if exists:
                                        os.system('python ./packages/'+str(identifier)+'/install.py')
                    
                                        self.AzuriteInstance.writecon('ok', 'Executed install.py', 1)
                                    else:
                                        self.AzuriteInstance.writecon('ok', 'install.py does not exist! Continuing!', 1)
                                    
                                    self.AzuriteInstance.writecon('ok', 'Installation package: '+str(identifier))
                                    
                                    self.AzuriteInstance.reboot()                                    
                                    return
                                    
                                else:
                                    self.AzuriteInstance.writecon('info', 'Package is not compatible! Removing it!', 2)
                                
                                    os.system('rm -rf ./tmp/package_'+str(identifier))
                            
                                    self.AzuriteInstance.writecon('ok', 'Removed package', 2)
                                    self.AzuriteInstance.writecon('error', 'Canceled installation!')
                                    return
                                
                                self.AzuriteInstance.writecon('', '')
                            else:
                                self.AzuriteInstance.writecon('info', 'Package is not compatible! Removing it!', 2)
                                
                                os.system('rm -rf ./tmp/package_'+str(identifier))
                            
                                self.AzuriteInstance.writecon('ok', 'Removed package', 2)
                                self.AzuriteInstance.writecon('error', 'Canceled installation!')
                                return
                            
                            self.AzuriteInstance.writecon('ok', 'Checked dependencies', 2)
                        else:
                            self.AzuriteInstance.writecon('info', 'Package is not compatible! Removing it!', 2)
                            
                            os.system('rm -rf ./tmp/package_'+str(identifier))
                            
                            self.AzuriteInstance.writecon('ok', 'Removed package', 2)
                            self.AzuriteInstance.writecon('error', 'Canceled installation!')
                            return

            self.AzuriteInstance.writecon('error', 'Could not find package with identifier: '+str(identifier))
            
            
        if '-remove' in args:
            try:
                pos = args.index('-remove')
                identifier = args[pos+1]
            except:
                self.AzuriteInstance.writecon('error', 'Please provide an identifier after -remove')
                self.help_apek()
                return
            
            self.AzuriteInstance.writecon('', 'Starting removal of package '+str(identifier))
            self.AzuriteInstance.writecon('', 'Checking if package is installed', 1)
            
            installed = False
            for item in os.listdir('./packages'):
                if item == identifier:
                    installed = True
            
            if not installed:
                self.AzuriteInstance.writecon('error', 'Package '+str(identifier)+' is not installed!', 1)
                self.AzuriteInstance.writecon('error', 'Could not remove package '+str(identifier))
                return
            else:
                self.AzuriteInstance.writecon('ok', 'Package is installed!', 1)
                self.AzuriteInstance.writecon('', 'Executing uninstall.py file in package', 1)
                
                exists = False
                for item in os.listdir('./packages/'+str(identifier)):
                    if item == 'uninstall.py':
                        exists = True
                
                if exists:
                    os.system('python ./packages/'+str(identifier)+'/uninstall.py')
                    
                    self.AzuriteInstance.writecon('ok', 'Executed uninstall.py', 1)
                else:
                    self.AzuriteInstance.writecon('ok', 'uninstall.py does not exist! Continuing!', 1)
                    
                
                self.AzuriteInstance.writecon('', 'Importing package info file', 1)
                
                info = imp.load_source('info', './packages/'+str(identifier)+'/info.py')
                
                self.AzuriteInstance.writecon('ok', 'Imported info file', 1)
                self.AzuriteInstance.writecon('', 'Checking files by the package', 1)
                
                files = info.package_files
                
                if len(files) != 0:
                    self.AzuriteInstance.writecon('ok', 'Got files!', 1)
                    self.AzuriteInstance.writecon('', 'Deleting files', 1)
                    
                    for filepath in files:
                        self.AzuriteInstance.writecon('', 'Checking file: '+str(filepath), 2)
                        
                        if not os.path.exists(filepath):
                            self.AzuriteInstance.writecon('warning', 'File does not exist! (This might create conflicts in other packages)', 2)
                        else:
                            self.AzuriteInstance.writecon('ok', 'Checked file: '+str(filepath), 2)
                            self.AzuriteInstance.writecon('', 'Deleting file: '+str(filepath), 2)
                            
                            #   TODO: ADD SAFETY (DONT DELETE SYSTEM FILES!)
                            
                            os.remove(filepath)
                            
                            self.AzuriteInstance.writecon('ok', 'Deleted file: '+str(filepath), 2)
                    
                    self.AzuriteInstance.writecon('ok', 'Deleted all files by the package', 1)
                else:
                    self.AzuriteInstance.writecon('ok', 'There are no files by the package!', 1)
                
                self.AzuriteInstance.writecon('', 'Checking directories by the package', 1)
                
                dirs = info.package_dirs
                
                if len(dirs) != 0:
                    self.AzuriteInstance.writecon('ok', 'Got directories!', 1)
                    self.AzuriteInstance.writecon('', 'Deleting directories', 1)
                    
                    for path in dirs:
                        self.AzuriteInstance.writecon('', 'Checking directory: '+str(path), 2)
                        
                        if not os.path.exists(path):
                            self.AzuriteInstance.writecon('warning', 'Directory does not exist! (This might create conflicts in other packages)', 2)
                        else:
                            self.AzuriteInstance.writecon('ok', 'Checked directory: '+str(path), 2)                        
                            self.AzuriteInstance.writecon('', 'Deleting directory: '+str(path), 2)
                            
                            #   TODO: ADD SAFETY (DONT DELETE SYSTEM FILES!)
                            
                            shutil.rmtree(path, ignore_errors=True)
                            
                            self.AzuriteInstance.writecon('ok', 'Deleted directory: '+str(path), 2)
                    
                    self.AzuriteInstance.writecon('ok', 'Deleted all directories by the package', 1)
                else:
                    self.AzuriteInstance.writecon('ok', 'There are no directories by the package!', 1)
                
                self.AzuriteInstance.writecon('ok', 'Package '+str(identifier)+' was fully removed!')
                
                
                
                
                
                
                #self.AzuriteInstance.writecon('', '')
            
            
        
    def help_apek(self, *args):
        print('usage: apek [ <args> ]')
        print('       Azurite Package manager')
        print('')
        print('Args:')
        print('       -install <identifier>         -   Installes package <identifier>')
        print('       -remove <identifier>          -   Uninstalles package <identifier>')



class Azurite:
    def __init__(self, version='1.0.0', os='ios', DEBUG='True'):
        
        self.version = version
        self.os = os
        
        self.DEBUG = DEBUG
    	    
        self.hooks = {}
        self.modules = {}
        
        #   Holds a copy of the default settings file for quick access
        self.settings = None
        
        #   Current user
        self.current_user = None
        
        #   Loaded packages
        self.loaded_packages = []
    
    
    @exec_hooks
    def getnode(self, path, subthread=-1):
        #   path example: "./system/ip"
        subthread=subthread+1
        if self.DEBUG: self.writecon('debug', 'Running getnode(self, '+str(path)+', subthread='+str(subthread)+')')
        try:
            node = self.settings.find(path)
            return node
        except:
            return None
            if self.DEBUG: self.writecon('debug', 'Could not find node at path: '+str(path))
    
    @exec_hooks
    def getnodes(self, path, subthread=-1):
        #   path example: "./system/users/user"
        subthread=subthread+1
        if self.DEBUG: self.writecon('debug', 'Running getnodes(self, '+str(path)+', subthread='+str(subthread)+')')
        try:
            nodes = self.settings.findall(path)
            return nodes
        except:
            return None
            if self.DEBUG: self.writecon('debug', 'Could not find any node at path: '+str(path))
        
        
    @exec_hooks
    def gettext(self, node, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running gettext(self, '+str(node)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        return node.text
    
    @exec_hooks
    def getattrib(self, node, attrib, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running getattrib(self, '+str(node)+', '+str(attrib)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        return node.attrib[attrib]
    
    @exec_hooks
    def settag(self, node, value, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running settag(self, '+str(node)+', '+str(value)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        node.tag = value
        return True
    
    @exec_hooks
    def setattrib(self, node, attrib, value, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running setattrib(self, '+str(node)+', '+str(attrib)+', '+str(value)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        node.set(attrib, value)
        return True
    
    @exec_hooks
    def settext(self, node, value, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running settext(self, '+str(node)+', '+str(value)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        node.text = value
        return True
    
    @exec_hooks
    def clearnode(self, node, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running clearnode(self, '+str(node)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        node.clear()
        return True
    
    @exec_hooks
    def appendnode(self, node, newnode, subthread=-1):
        if self.DEBUG: self.writecon('debug', 'Running appendnode(self, '+str(node)+', '+str(newnode)+', subthread='+str(subthread)+')')
        subthread=subthread+1
        node.append(newnode)
        return True
    
    @exec_hooks
    def savesettings(self, file='settings/default.xml', subthread=-1):    
        subthread=subthread+1
        self.writecon('', 'Saving setting file: '+str(file), subthread)
        self.writecon('', 'Opening file: '+str(file), subthread+1)
        
        try:
            fileobject = open(file, 'w')
        except:
            self.writecon('error', 'Could not open file: '+str(file), subthread+1)
            return False
        
        self.writecon('ok', 'Opened file', subthread+1)
        if self.DEBUG: self.writecon('debug', 'fileobject = '+str(fileobject))
        self.writecon('', 'Getting tree from self.settings', subthread+1)
        
        try:
            tree = self.settings
        except:
            self.writecon('error', 'Could not get tree!', subthread+1)
            return False
        
        self.writecon('ok', 'Got tree!', subthread+1)
        if self.DEBUG: self.writecon('debug', 'tree = '+str(tree))
        self.writecon('', 'Writing tree to file', subthread+1)
        
        try:
            tree.write(file)
        except:
            self.writecon('error', 'Could not write tree to file!', subthread+1)
            return False
        
        self.writecon('ok', 'Written tree to file!', subthread+1)
        
        self.writecon('ok', 'Saved settings file', subthread)
        return True
    
    @exec_hooks
    def loadsettings(self, file='settings/default.xml', subthread=-1):
        subthread=subthread+1
        self.writecon('', 'Loading setting file: '+str(file), subthread)
        self.writecon('', 'Opening file: '+str(file), subthread+1)
        
        try:
            fileobject = open(file, 'r')
        except:
            self.writecon('error', 'Could not open file: '+str(file), subthread+1)
            return False
        
        self.writecon('ok', 'Opened file', subthread+1)
        if self.DEBUG: self.writecon('debug', 'fileobject = '+str(fileobject))
        
        self.writecon('', 'Creating tree from file content', subthread+1)
        
        tree = ElementTree.parse(file)
        
        self.writecon('ok', 'Created tree', subthread+1)
        if self.DEBUG: self.writecon('debug', 'tree = '+str(tree))
        self.writecon('', 'Saving dictionary for later accesss', subthread+1)
        
        if self.settings is not None:
            self.writecon('warning', "Dictionary already exists! Won't override it!", subthread+1)
            return False
        else:
            self.settings = tree
            self.writecon('ok', 'Saved dictionary!', subthread+1)
        
        self.writecon('ok', 'Loaded settings file', subthread)
        return True



    @exec_hooks
    def exec_load_methods(self):
        if self.DEBUG: self.writecon('debug', 'Executing load methods')
        #    Hooks
        for identifier in _hook_instances.keys():
            if self.DEBUG: self.writecon('debug', 'Executing hook: '+str(identifier))
            
            hook = _hook_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'hook = '+str(hook))
                
            hook.load(azurite_instance=self)
            
            if self.DEBUG: self.writecon('debug', 'Finished executing hook.load')
    	    
        #    Modules
        for identifier in _module_instances.keys():
            if self.DEBUG: self.writecon('debug', 'Executing module: '+str(identifier))
            
            module = _module_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'module = '+str(module))
            
            module.load(azurite_instance=self)
            
            if self.DEBUG: self.writecon('debug', 'Finished executing module.load')
    	
    @exec_hooks
    def exec_unload_methods(self):
        if self.DEBUG: self.writecon('debug', 'Executing unload methods')
        #    Hooks
        for identifier in _hook_instances.keys():
            if self.DEBUG: self.writecon('debug', 'Executing hook: '+str(identifier))
            
            hook = _hook_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'hook = '+str(hook))
        
            hook.unload(azurite_instance=self)
            
            if self.DEBUG: self.writecon('debug', 'Finished executing hook.unload')
            	    
        #    Modules
        for identifier in _module_instances.keys():
            if self.DEBUG: self.writecon('debug', 'Executing module: '+str(identifier))
            
            module = _module_instances[identifier]
            
            if self.DEBUG: self.writecon('debug', 'module = '+str(module))
            	        
            module.unload(azurite_instance=self)
            
            if self.DEBUG: self.writecon('debug', 'Finished executing module.unload')



    @exec_hooks
    def shutdown(self):
        if self.DEBUG: self.writecon('debug', 'Initiating shutdown sequence!')
        
        self.exec_unload_methods()
        
        if self.DEBUG: self.writecon('debug', 'Executed unload methods')
        
        sys.exit()
    
    @exec_hooks
    def reboot(self):
        if self.DEBUG: self.writecon('debug', 'Initiating reboot sequence!')
        
        self.exec_unload_methods()
        
        if self.DEBUG: self.writecon('debug', 'Executed unload methods')
        
        if self.os == 'linux' or 'osx' or 'windows' or 'ios' or 'android':
            self.writecon('info', 'The system will restart in 8 seconds!')
            time.sleep(3)
            i = 5
            for y in range(6):
                self.writecon('info', str(i))
                i = i-1
                time.sleep(1)
            
            self.writecon('info', 'Restarting...')
            time.sleep(2)
            
            os.system('./start.sh '+str(sys.argv))
            
        else:
            self.writecon('info', 'Please restart the system manually to finish the installation using the "shutdown -now && shell ./start.sh" command!')
    
    @exec_hooks
    def authenticate(self, username, password):
        if self.DEBUG: self.writecon('debug', 'Starting authentication')
        
        usernodes = self.getnodes('./system/users/user')
        
        if self.DEBUG: self.writecon('debug', 'usernodes = '+str(usernodes))
        
        for node in usernodes:
            if self.getattrib(node, 'username') == username:
                salt = self.getattrib(node, 'salt')
                
                if self.DEBUG: self.writecon('debug', 'salt = '+str(salt))
                
                hashed_password = hashlib.sha512(password + salt).hexdigest()
                
                if self.DEBUG: self.writecon('debug', 'hashed_password = '+str(hashed_password))
                if hashed_password == self.getattrib(node, 'hashed_password'):
                    #if self.DEBUG: self.writecon('debug', 'Authentication was successfull! username: '+str(username)+' password: '+str(password))
                    if self.DEBUG: self.writecon('debug', 'Authentication was successfull! username: '+str(username)+' password: hidden')
                    return True
                else:
                    #if self.DEBUG: self.writecon('debug', 'Authentication failed! username: '+str(username)+' password: '+str(password))
                    if self.DEBUG: self.writecon('debug', 'Authentication failed! username: '+str(username)+' password: hidden')
                    return False
    
    @exec_hooks
    def changepassword(self, username, oldpassword, newpassword):
        if self.DEBUG: self.writecon('debug', 'Changing password of user: '+str(username))
        
        usernodes = self.getnodes('./system/users/user')
    
        if self.DEBUG: self.writecon('debug', 'usernodes = '+str(usernodes))
    
        for node in usernodes:
            if self.getattrib(node, 'username') == username:
                if hashlib.sha512(oldpassword + self.getattrib(node, 'salt')).hexdigest() == self.getattrib(node, 'hashed_password'):
                    salt = uuid.uuid4().hex
            
                    if self.DEBUG: self.writecon('debug', 'salt = '+str(salt))
            
                    hashed_password = hashlib.sha512(newpassword + salt).hexdigest()
            
                    if self.DEBUG: self.writecon('debug', 'hashed_password = '+str(hashed_password))
            
                    self.setattrib(node, 'salt', salt)
                    self.setattrib(node, 'hashed_password', hashed_password)
            
                    return True
                else:
                    return 'Old password is not correct!'
    	    
            
    @exec_hooks
    def writecon(self, state, text, subthread=0):
        try:
            import termcolor
            from colored import fg, bg, attr, style
            compatability_mode = False
        except:
            compatability_mode = True
    
    
        if not compatability_mode:
            import time
            import termcolor
            from colored import fg, bg, attr, style
            
            if subthread == 0:
                subthread_spacing = ''
            elif subthread == 1:
                subthread_spacing = '    - '
            elif subthread == 2:
                subthread_spacing = '        - '
            elif subthread == 3:
                subthread_spacing = '            - '
            elif subthread == 4:
                subthread_spacing = '                - '
            elif subthread == 5:
                subthread_spacing = '                    - '
            
            if state == "":
                formatted_text = "[" + termcolor.colored("....", "cyan", attrs=["bold"]) + "]   " + text
            if state == "ok":
                formatted_text = "[ " + termcolor.colored("OK", "green", attrs=["bold"]) + " ]   " + text #termcolor.colored(text, "green", attrs=["bold"]))
            if state == "error":
                formatted_text = "[" + termcolor.colored("ERROR", "red", attrs=["blink", "bold"]) + "]  " + termcolor.colored(text, "red", attrs=["bold"])
            if state == "warning":
                formatted_text = "[" + fg(208) + attr("bold") + attr("blink") + "WARN" + style.RESET + "]   " + fg(208) + attr("bold") + text + style.RESET
            if state == "info":
                formatted_text = "[" + termcolor.colored("INFO", "cyan", attrs=["bold"]) + "]   " + termcolor.colored(text, "cyan", attrs=["bold"])
            if state == "debug":
                formatted_text = "[" + termcolor.colored("DEBUG", "magenta", attrs=["bold"]) + "]  " + termcolor.colored(text, "magenta", attrs=["bold"])
            if state == "sys":
                formatted_text = "[" + termcolor.colored("SYSTEM", "blue", attrs=["bold"]) + "] " + termcolor.colored(text, "blue", attrs=["bold"])
            
            sys.stdout.write(subthread_spacing)
            sys.stdout.flush()
            for char in formatted_text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.00001)
            sys.stdout.write('\n')
            return True
        else:
            import time
            
            #    Run in compatabiliy mode
            if subthread == 0:
                subthread_spacing = ''
            elif subthread == 1:
                subthread_spacing = '    - '
            elif subthread == 2:
                subthread_spacing = '        - '
            elif subthread == 3:
                subthread_spacing = '            - '
            elif subthread == 4:
                subthread_spacing = '                - '
            elif subthread == 5:
                subthread_spacing = '                    - '
            
            if state == "":
                formatted_text = "[....]   " + text
            if state == "ok":
                formatted_text = "[ OK ]   " + text
            if state == "error":
                formatted_text = "[ERROR]  " + text
            if state == "warning":
                # 208
                formatted_text = "[WARN]   " + text
            if state == "info":
                formatted_text = "[INFO]   " + text
            if state == "debug":
                formatted_text = "[DEBUG]  " + text
            if state == "sys":
                formatted_text = "[SYSTEM] " + text
            
            sys.stdout.write(subthread_spacing)
            sys.stdout.flush()
            for char in formatted_text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.0001)
            sys.stdout.write('\n')
            return True

if __name__ == '__main__':
    
    #   Getting command line arguments and setting variables
    args = sys.argv
    
    debug = True if '-d' in args else False
    
    
    #   Setting Debug mode
    #while True:
    #    debug = raw_input('Debug (y/n):')
    #    debug = True if debug == 'y' else False if debug == 'n' else None
    #    if debug is not None:
    #        break
    
    startup = StartUp(DEBUG=debug)
    
    startup.HookLoaderInstance.loadhooks()
    startup.ModuleLoaderInstance.loadmodules()
    
    startup.cross_dependencies_check()
    
    startup.patch_azurite()
    startup.patch_shell()
    startup.final_load_hooks()
    
    
    az = Azurite(version=startup.version, os=startup.os, DEBUG=startup.DEBUG)
    
    az.exec_load_methods()
    
    az.runtest(azurite_instance=az)
    
    az.test = az.Test(azurite_instance=az)
    
    az.test.tk_testing_test(azurite_instance=az)
    
    az.loadsettings()
    
    setattr(AzuriteShell, 'AzuriteInstance', az)
    shll = AzuriteShell()
    shll.cmdloop()