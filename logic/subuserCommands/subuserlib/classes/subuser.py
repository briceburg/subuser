#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

#external imports
import subprocess,os
#internal imports
import subuserlib.classes.userOwnedObject,subuserlib.classes.programSource,subuserlib.classes.permissions,subuserlib.classes.describable

class Subuser(subuserlib.classes.userOwnedObject.UserOwnedObject,subuserlib.classes.describable.Describable):
  __name = None
  __programSource = None

  def __init__(self,user,name,programSource):
    subuserlib.classes.userOwnedObject.UserOwnedObject.__init__(self,user)
    self.__name = name
    self.__programSource = programSource

  def getName(self):
    return self.__name

  def getProgramSource(self):
    return self.__programSource

  def getPermissions(self):
    permissionsDotJsonPath = os.path.join(self.getUser().getConfig().getUserSetPermissionsDir(),self.getName(),"permissions.json")
    if not os.path.exists(permissionsDotJsonPath):
      permissionsDotJsonPath = os.path.join(self.getProgramSource().getSourceDir(),"permissions.json")
    if not os.path.exists(permissionsDotJsonPath):
      permissionsDotJsonPath = None
    return subuserlib.classes.permissions.Permissions(self.getUser(),permissionsDotJsonPath)

  def getHomeDirOnHost(self):
    """
    Returns the path to the subuser's home dir. Unless the subuser is configured to have a stateless home, in which case returns None.
    """
    if self.getPermissions()["stateful-home"]:
      return os.path.join(self.getUser().getConfig().getSubuserHomeDirsDir(),self.getName())
    else:
      return None
  
  def getDockersideHome(self):
    if self.getPermissions()["as-root"]:
      return "/root/"
    else:
      return self.getUser().homeDir
  
  def getSetupSymlinksScriptPathOnHost(self):
    """
    For each subuser we have a docker-side script which sets up various symlinks within the container.  This function returns a path to that script as cached on the host side.
    """
    return os.path.join(self.getUser().homeDir,".subuser","cache","by-subuser",self.getName(),"setup-symlinks")
  
  def describe(self):
    print("Subuser: "+self.getName())
    print("------------------")
    print("Progam:")
    self.getProgramSource().describe()