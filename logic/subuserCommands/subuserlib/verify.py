#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is one of the most important modules in subuser.  This module has one function `verify` which is used to apply the changes for most commands that change the user's configuration:

 - Adding a new subuser
 - Removing an old subuser
 - Updating repositories
 - Adding repositories
 - Repairing the instalation
"""

#external imports
import shutil,os
#internal imports
import subuserlib.install

def verify(user):
   """
   Ensure that:
      - Registry is consistent; warns the user about subusers that point to non-existant source programs.
     - For each subuser there is an up-to-date image installed.
     - No-longer-needed temporary repositories are removed. All temporary repositories have at least one subuser who's image is built from one of the repository's program sources.
      - No-longer-needed installed images are removed.
   """
  user.getRegistry().log("Verifying subuser configuration.")
  verifyRegistryConsistency(user)
  user.getInstalledImages().unregisterNonExistantImages()
  ensureImagesAreInstalledAndUpToDate(user)
  trimUnneededTempRepos(user)
  rebuildBinDir(user)

def verifyRegistryConsistency(user):
  user.getRegistry().log("Verifying registry consistency...")
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    if not subuser.getProgramSource().getName() in subuser.getProgramSource().getRepository():
      user.getRegistry().log("WARNING: "+subuser.getName()+" is no longer present in it's source repository. Support for this progam may have been dropped.")

def ensureImagesAreInstalledAndUpToDate(user):
  user.getRegistry().log("Checking if images need to be updated or installed...")
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    subuserlib.install.ensureSubuserImageIsInstalledAndUpToDate(subuser)    

def trimUnneededTempRepos(user):
  user.getRegistry().log("Running garbage collector on temporary repositories...")
  for repoId,repo in user.getRegistry().getRepositories().iteritems():
    keep = False
    if not type(repoId) is str: #If this is a temp repo.
      for _,installedProgram in user.getInstalledPrograms().iteritems():
        if repoId == installedProgram.getSourceRepoId():
          keep = True
    if not keep:
      user.getRegistry().logChange("Removing uneeded temporary repository: "+repo.getName())
      repo.removeGitRepo()
      del user.getRegistry().getRepositories()[repoId]

def rebuildBinDir(user):
  shutil.rmtree(user.getConfig().getBinDir())
  os.mkdir(user.getConfig().getBinDir())
  for _,subuser in user.getRegistry().getSubusers().iteritems():
    if subuser.isExecutableShortcutInstalled():
      subuser.installExecutableShortcut()