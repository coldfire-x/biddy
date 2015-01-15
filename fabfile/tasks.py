# -*- coding: utf-8 -*-

from fabric.tasks import Task
from fabric.api import local, run, put, cd, lcd, env, execute
from fabric.context_managers import settings

from . import ProjectConfig
from .gitcmd import GitCmds
from .yumcmd import Yum


__all__ = ['YumUpgradeTask', 'YumInfoTask', 'YumIntallTask', 'YumDowngradeTask']


class YumBaseTask(Task):
    ''' task class for yum operations '''

    name = 'yum'

    def __do_run_cmd(self, cmd):
        ''' running real yum command '''
        real_cmd = getattr(self.yum, cmd)
        if not callable(real_cmd):
            return

        with settings(parallel=True):
            execute(real_cmd, hosts=self.hosts)

    def run(self, proj, sub, mode):
        ''' run fabric task

        setup running env, and call the real * doer *
        '''
        cmd = self.name
        self.setup_runing_env(proj, sub, mode)
        self.__do_run_cmd(cmd)

    def setup_runing_env(self, proj, sub, mode):
        ''' setup running env

        setup operation running targets as hosts

        Args:
            proj: project name
            sub: only valid value is `code` or `static`, that is release source
                 code or static files such as js, css and img.
            mode: valid value is `stage`, `prod`.
        '''
        if sub not in ('code', 'static') or mode not in ('stage', 'prod'):
            print '\nWrong command usage, the right command is:'
            print 'fab upgrade:proj,[code|static],[prod|stage]\n'
            return

        self.conf = ProjectConfig().get_config(proj, mode)
        self.deploy_conf = (self.conf.deploy_cfg.code if sub == 'code'
            else self.conf.deploy_cfg.static
        )
        self.yum = Yum(self.deploy_conf.package_name)

        # setup hosts
        env.hosts = self.hosts = self.deploy_conf.hosts


class YumUpgradeTask(YumBaseTask): name = 'upgrade'
class YumIntallTask(YumBaseTask): name = 'install'
class YumDowngradeTask(YumBaseTask): name = 'downgrade'
class YumInfoTask(YumBaseTask): name = 'info'
