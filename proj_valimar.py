"""This module contains the CTF project class for Valimar scripts.

CTF test case classes inherit from this class giving the opportunity
to override default functionality on a project wide basis or to provide
common functionality.

Note:  This is a template and is meant to be starting point for a more
targeted script.
"""

import platform
PyMajorIs2 = platform.python_version_tuple()[0] == '2'

from ctf.project import Project

class Valimar(Project):
    """Valimar project class.  
    """

    def __init__(self, *args, **kwargs):
        self.projectDesc = "Valimar project common functionality"
        self.projectName = "Valimar"
        self.projectVersion = 1 
        
        super (Valimar, self).__init__(*args, **kwargs)

        # Add Project specific config information here

    def projectTclPackages (self):
        """Add project common Tcl packages here.
        """
        pass
    
    def projectOpts (self):
        """Add project common command line options here
        """
        pass

    def projectInit (self):
        """Called before the testInit() function is called to provide
        project common initializations.
        """
        pass 

    def projectConfigEmail (self):
        """Called before testConfigEmail() to configure email.
        """
        pass

    def projectCleanup (self):
        """Called before the testCleanup() function to provide project common
        test case cleanup functionality.
        """
        pass

    def projectEmail (self):
        """Called after testEmail to send project specific email.
        """
        pass
