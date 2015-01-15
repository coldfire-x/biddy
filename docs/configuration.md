# Configuration

每个需要打包的项目都需要在`settings/configs/`中添加配置文件，
配置文件按照在git上的不同组来划分，比如git上的项目`mop/Example-web`，
相应的配置文件在`settings/configs/mop.py`中。

## 配置文件说明

`mop/gift`这个项目为例子,具体的配置如下：

    {
        'packaging': { # 打包相关配置
            'name': 'mop/gift',
            'gitrepo': 'git@git.Example.com:mop/gift.git', # 项目git地址
            'tmpl': 'mop_gift.spec.tmpl', # rpm spec template name
            'arch': 'noarch', # could be noarch or x86_64
            'package_name': 'Example_mop_gift',
            'description': '欧朋送话费活动',
            'location': 'gift', # 安装目录的名字,eg: /web/gift
             # static_location 如果有定义则需要另外打包static
            'static_location': 'gift',
            'os': ['centos5', 'centos6'], # target host's os distribution
        },

        'deploy': { # 部署相关配置
            'code': { # 部署代码
                'package_name': 'Example_mop_gift', # 安装的RPM包名
                'production': { # 生产环境目标服务器
                    'hosts': ['root@192.168.1.1', 'root@192.168.1.2']
                }, # 预发布环境，或者测试环境的服务器地址
                'staging': { # staging host information
                    'hosts': ['root@192.168.1.3',],
                }
            },
            'static': { # 部署静态文件
                'package_name': 'Example_mop_gift-static',
                'production': {
                    'hosts': ['root@192.168.1.1', 'root@192.168.1.2',
                    ]
                },
                'staging': {
                    'hosts': ['root@192.168.1.3'],
                }
            },
        }
    }

这个配置是一个完整的Python 字典对象，`packaging`对应的把项目打成RPM包所需要的信息，
具体解释如下：

    'name': 'mop/gift', # 项目的名称，规则是git组加具体项目名
    'gitrepo': 'git@git.xxx.com:mop/gift.git', # 项目git地址
    'tmpl': 'mop_gift.spec.tmpl', # RPM SEPC的模板文件名，文件在templates目录下
    'arch': 'noarch', # 是否对操作系统是多少位有要求，脚本类一般为noarch, golang为x86_64
    'package_name': 'Example_mop_gift', # 打包后RPM的包名,规则为Example_git组名_项目名
    'description': '欧朋送话费活动', # RPM包的描述信息
    'location': 'gift', # 安装目录的名字,eg: /web/gift
    'static_location': 'gift', # static_location 如果有定义则需要另外打包static包
    'os': ['centos5', 'centos6'], # 安装RPM包的目标服务器操作系统版本,会在不同的打包服务器上进行打包


`deploy`是一个可选的配置项，主要用来自动化升级目标机器上的RPM包, 具体的含义看代码中的注释,
需要解释的为，代码和静态文件的RPM包是分开的，需要安装到不同的目标服务器上，我们的静态资源服务器
有4台，根据具体需要，把相应的服务器地址填入hosts中。
