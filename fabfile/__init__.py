# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.join(os.path.abspath(__file__), '..'))

from fabric.api import env, task, run, local, cd
from fabric.contrib import files

from settings import ProjectConfig, get_build_config, REPO_PREFIX
from .rpmbuildcmd import BuildRpm
from .tasks import *


@task
def help():
    help_str = '''
1. 列出所有项目: fab list

2. 给项目打包: fab build_rpm:[项目名],[tag号]
   例子: 给mop/gift项目打包，tag号为gift-0.0.1
       fab build_rpm:mop/gift,gift-0.0.1

3. 只打包 但不上传至线上yumrepo: fab build_only [othercommds]

4. 升级包 fab upgrade:project_name, [code|static], [prod|stage]
   例子: 升级生产环境 mop/gift项目的代码
       fab upgrade:mop/gift,code,prod

5, 降级为上一个版本 fab downgrade:project_name, [code|static], [prod|stage]

6, 查看当前包信息 fab info:project_name, [code|static], [prod|stage]


注: 目前可选的操作系统版本为: centos5 | centos6 再配置文件中设置
'''
    print help_str


upgrade = YumUpgradeTask()
install = YumIntallTask()
info = YumInfoTask()
downgrade = YumDowngradeTask()


# it will upload rpm packages to rpm repo by default
env.build_only = False
def build_only():
    ''' only build the rpm , it wont scp packages to yum repo '''
    env.build_only = True


@task
def list():
    ''' list all projects '''
    for proj in ProjectConfig().all_projects:
        print proj


@task
def build_rpm(proj, tag):
    project_conf = ProjectConfig().get_config(proj)
    cmd = BuildRpm(project_conf.package_cfg, tag)
    cmd.execute()


@task
def init_env(py=None):
    ''' init env, scp example.repo to target box

    Args:
        py: if py is not None, then init box as an python env, install python27
        rpm package, and pip
    '''
    env.user = 'root'

    curdir = os.path.dirname(os.path.abspath(__file__))
    repo_file = os.path.join(curdir, '..', 'docs', 'example.repo')

    if not files.exists('/etc/yum.repos.d/example.repo'):
        repo_url = 'ftp://yums.example.com/pub/yumrepos/example/example.repo'
        run('wget %s -O /etc/yum.repos.d/example.repo' % repo_url)

    # install python to /usr/local/python
    if not py:
        print '#' * 10, 'init yum env finished', '#' * 10
        return

    run('yum install python27 -y')

    # install pip to /usr/local/python/bin/pip
    pipurl = 'https://bootstrap.pypa.io/get-pip.py'
    with cd('/tmp'):
        run('wget %s --no-check-certificate' % pipurl)
        run('/usr/local/python/bin/python /tmp/get-pip.py')
        run('rm -rf /tmp/get-pip.py')
