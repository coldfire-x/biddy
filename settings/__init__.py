# -*- coding: utf-8 -*-

import os
import glob
import json

from .models import ProjectCfg


_current_dir = os.path.dirname(os.path.abspath(__file__))
REPO_PREFIX = 'example-'


class _BuilderBaseConfig(object):
    ''' base configuration '''

    __attrs__ = [
        'host', 'user', 'osver', 'specdir', 'sourcedir', 'rpmdir',
        'repo_user', 'repo_host', 'repo_base_dir', 'repo_name_prefix',
        'git_host', 'git_user',
    ]

    __attrs_dict__ = {x:1 for x in __attrs__}

    def __init__(self, config_file=None):
        ''' init an object

        Args:
            config_file: if given, it should be an json formatted confg file,
            if not given, then use `./config.json`.
        '''
        self._parsed = False
        if not config_file:
            config_file = os.path.join(_current_dir, 'config.json')

        if os.path.exists(config_file):
            self._config_file = config_file
            with open(self._config_file) as f:
                self.parse_config_json(f)

    def parse_config_json(self, f):
        ''' parse config file

        if attr defined in __attrs__ is found in json configuration file, then
        update it. otherwise use the default value.
        '''
        self._json_obj = json.load(f)
        for k in self._json_obj:
            if k not in self.__attrs_dict__: continue
            setattr(self, k, self._json_obj[k])

        self._parsed = True

    def special_config(self, k):
        ''' hook populate special configs

        Args:
            k, special key in json config file, override default settings
        '''
        d = self._json_obj.get(k)
        if not d : return

        for _k in d:
            if _k not in self.__attrs_dict__: continue
            setattr(self, _k, d[_k])

    def get_specdir(self):
        return self.builder + ':%s' % self.specdir

    @property
    def yumrepo(self):
        return "%s@%s:%s" % (self.repo_user, self.repo_host, self.os_repo_base_dir)

    @property
    def source_dir(self):
        return self.builder + ':%s' % self.sourcedir

    @property
    def builder(self):
        return '@'.join([self.user, self.host])

    @property
    def os_repo_base_dir(self):
        return os.path.join(self.repo_base_dir, self.osver)


def get_build_config(osversion):
    ''' get os related config object

    Args:
        osversion: only the centos5, centos6 is valid, these two should be key
                   in configuration file.
    '''
    assert osversion in ('centos5', 'centos6'), 'Invalid os version'

    obj = _BuilderBaseConfig()
    obj.special_config(osversion)
    return obj


def load_project_config_modules():
    ''' load all project configs from package configs

    all module in configs package should be containing a list var named projects
    '''
    path = os.path.join(_current_dir, 'configs', '*.py')
    all_modules = glob.glob(path)
    modules = [os.path.basename(m)[:-3] for m in all_modules]

    projects = []
    for m in modules:
        if m == '__init__': continue

        m = 'configs' + '.' + m
        module = __import__(m, globals(), locals(), ['projects'])
        projects.extend(module.projects)

    return projects


class ProjectConfig(object):
    ''' project packaging and deploy configurations '''

    def __init__(self):
        self.projects = load_project_config_modules()
        self.project_names = [x['packaging']['name'] for x in self.projects]

    @property
    def all_projects(self):
        return self.project_names

    def get_config(self, name, mode='prod'):
        ''' get project's configuration

        Args:
            name: project's name, such as 'mop/gift2'
            mode: prod or stage, default value is `prod`, the different between
                  these two values is the ip of hosts, default value is `prod`
        '''
        name = name.strip()
        conf = None
        for project in self.projects:
            if project['packaging']['name'].strip() == name:
                conf = project
                break

        assert conf is not None, 'Cannt find config for project %s' % name
        return ProjectCfg(conf, mode)
