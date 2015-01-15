# -*- coding: utf-8 -*-

from fabric.api import run, hide
from fabric.context_managers import settings

from . import REPO_PREFIX


class Yum(object):
    ''' yum command wrapper

    Note: hosts info should be setup before this
    '''

    def __init__(self, package):
        ''' init yum object

        Args:
            package: rpm package name
        '''
        self.package = package
        # to accelerate yum operations, only check updates against our repo
        self._repo = (' --disablerepo=* --enablerepo=%s*' % REPO_PREFIX)

    def upgrade(self):
        ''' upgrade a rpm package to the latest version '''
        with settings(hide('stdout', 'stderr')):
            run('yum upgrade -y %s %s' % (self.package, self._repo))

    def info(self):
        ''' get rpm package information, this will check if update available '''
        run('yum info %s %s' % (self.package, self._repo))

    def install(self):
        ''' install a brand new rpm package '''
        with settings(hide('stdout', 'stderr')):
            run('yum install -y %s %s' % (self.package, self._repo))

    def downgrade(self):
        ''' downgrade to version which is less then 1

        Note: this yum operation may got unexpected result, because the version
        managemanet of yum, check yum's official doc for `version management`.
        '''
        with settings(hide('stdout', 'stderr')):
            run('yum downgrade -y %s %s' % (self.package, self._repo))

    def downloadonly(self, master):
        ''' download the rpm package only '''
        valid_main_cmds = ('upgrade', 'install', 'downgrade')
        assert master in valid_main_cmds, 'valid main cmds are %s' % valid_main_cmds
        with settings(hide('stdout', 'stderr')):
            run('yum %s -y %s --downloadonly %s' % (master, self.package, self._repo))
