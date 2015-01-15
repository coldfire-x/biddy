# -*- coding: utf-8 -*-


projects = [
    {
        'packaging': { # 打包相关配置
            'name': 'tingsongx/xts',
            'gitrepo': 'git@git.example.com:tingsongx/xts.git', # 项目git地址
            'tmpl': 'tingsongx_xts.spec.tmpl', # rpm spec template name
            'arch': 'noarch', # could be noarch or x86_64
            'package_name': 'example_tingsongx_xts',
            'description': '欧朋送话费活动',
            'location': 'xts', # 安装目录的名字,eg: /web/xts
             # static_location 如果有定义则需要另外打包static
            'static_location': None,
            'os': ['centos5', 'centos6'], # target host's os distribution
        },

        'deploy': { # 部署相关配置
            'code': { # 部署代码
                'package_name': 'example_tingsongx_xts', # package to be installed or upgraded
                'prod': { # prod hosts information
                    'hosts': [
                        'root@192.168.1.1', 'root@192.168.1.1',
                     ]
                },
                'stage': { # stage host information
                    'hosts': ['root@192.168.1.3',],
                }
            },
        }
    },
]
