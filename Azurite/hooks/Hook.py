# coding: utf-8

class Hook:
    # Sets basic information
    def __init__(self):
        self.name = 'MyHook' # Hook name
        self.identifier = 'com.myname.myhook' # Hook identifier
        self.description = 'My awesome hook!' # A short description
        self.version = '0.0.0' # The version of your hook
        self.target_version = '0.0.0' # The version of Azurite your hook is build for
        self.target_os = ['osx', 'linux', 'windows', 'ios', 'android'] # Supported operating systems (osx, linux, windows, ios, android)
        self.dependencies = {
            'hooks': [],
            'modules': [],
            'python_modules': []
            } # Insert the hook or module identifiers. For python modules use the pip installation name.
        self.__post_init__()
    
    def __post_init__(self):
        pass
    
    
    # Gets called when the hook is loaded
    def load(self, azurite_instance):
        pass
    
    # Gets called when (before) the hook is completely unloaded by the system
    def unload(self, azurite_instance):
        pass
    
    
    def test(self):
        print 'hello world'