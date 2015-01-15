# -*- coding: utf-8 -*-

import sys
from fabric.api import local, lcd, settings


class GitCmds(object):
    # 封装git相关命令

    def __init__(self, working_dir='.'):
        self.working_dir = working_dir

    def clone(self, gitrepo):
        local('git clone %s %s' % (gitrepo, self.working_dir))

        # pull submodule
        with lcd(self.working_dir):
            local('git submodule init')
            local('git submodule update')

    def _check_tag_on_master(self, treeish):
        with lcd(self.working_dir), settings(warn_only=True):
            result = local('git branch --contains %s | grep master' % treeish)
            if not result.failed:
                return True

    def checkout(self, treeish):
        with lcd(self.working_dir):
            local('git checkout %s' % treeish)
