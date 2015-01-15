# -*- coding: utf-8 -*-


class PackagingCfg(object):
    ''' cls for project packaging '''

    # all the attributes list here are building related
    __attrs__ = ['name', 'gitrepo', 'tmpl', 'arch', 'package_name',
        'os', 'description', 'location', 'static_location',
    ]

    def __init__(self, config_dict):
        ''' init a packagecfg object from config_dict '''
        for attr in self.__attrs__:
            if attr in config_dict:
                setattr(self, attr, config_dict[attr])


class DeployCfg(object):
    ''' cls for deploying configs '''

    class _BaseConfig(object):
        ''' base config include rpm package name and deploy targets '''

        def __init__(self, config_dict, mode):
            self.package_name = config_dict['package_name']
            self.hosts = config_dict[mode]['hosts']

    class Static(_BaseConfig):
        ''' static files configs '''
        pass

    class Code(_BaseConfig):
        ''' source code configs '''
        pass

    def __init__(self, config_dict, mode):
        ''' init a deploy config object, set up source code and static deploy
            config object

        Args:
            config_dict: deploy related config dict
            mode: only valid values are (stage, prod)
        '''
        self.code = self.Code(config_dict['code'], mode)

        if 'static' not in config_dict: return
        self.static = self.Static(config_dict['static'], mode)


class ProjectCfg(object):
    ''' configs for project '''

    def __init__(self, config_dict, mode='prod'):
        self.package_cfg = None
        self.deploy_cfg = None
        self.parse(config_dict, mode)

    def parse(self, config_dict, mode):
        ''' parse configs, init config objects '''
        config = config_dict['packaging']
        self.package_cfg = PackagingCfg(config)

        if 'deploy' not in config_dict: return
        config = config_dict['deploy']
        self.deploy_cfg = DeployCfg(config, mode)
