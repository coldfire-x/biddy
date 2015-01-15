## Deploys

此项目目的在于将脚本类文件自动打包成RPM，便于线上环境管理。打包过程如下：

0. 输入项目名称和tag号
1. clone gitlab上的项目代码到本地`/tmp/`下的一个临时目录
2. 如果项目中有`build`脚本，运行build脚本做预处理，比如css,js压缩等
3. 本地将项目打成tar包，scp到打包服务器上
4. 执行打包操作，生成RPM包，并将RPM包scp到线上YUM仓库


## 环境依赖

1. python2.7 (py依赖包见requirements.txt)
2. java
3. CentOS5
4. CentOS6
5. FTP


## Deploys 安装

1. 安装Python包管理工具[pip](https://pypi.python.org/pypi/pip)
2. git clone Deploys 代码
3. 运行`pip install -r requirements.txt`


## 打包环境

根据RPM包的安装目标机操作系统版本，分别在相应的打包环境打包

1. centos5 172.18.100.208
2. centos6 172.18.100.214

RPM Build的目录在`/home/buider/`。


## 约定

1. 打包时需要tag信息, tag名称可以时v1.2.3 或者 projectname-1.2.3 第一位数字为
版本号 其后为release, minor

2. RPM post小节里面涉及的脚本，不可以带有`yum`相关指令, 以及需要输入的指令，否则，会导致死锁


## 配置文件

参考settings.projects文件中的mop/gift项目配置


## 命令参考 [Fabric style]

1. fab help 更加详细的帮助信息
2. 列出所有的项目 `fab list`
3. 打成RPM包 `fab build_rpm:mop/gift,gift-1.4.1`
4. 升级RPM包 `fab upgrade:mop/gift,[code|static],[prod|stage]`
5. 初始化YUM环境 `fab -H 172.18.100.76,172.18.100.77 init_env`
   如果需要安装python: `fab -H 172.18.100.76,172.18.100.77 init_env:py`


## fabric tips

使用fab 命令的时候可以使用 `--hide stdout` 隐藏stdout输出



## fab TAB键自动补齐脚本(放置在~/.bashrc中)
    # Bash completion for fabric
    #
    function _fab_complete() {
        local cur
        if [[ -f "fabfile.py" || -d "fabfile" ]]; then
            cur="${COMP_WORDS[COMP_CWORD]}"
            COMPREPLY=( $(compgen -W "$(fab -F short -l)" -- ${cur}) )
            return 0
        else
            # no fabfile.py found. Don't do anything.
            return 1
        fi
    }

    complete -o nospace -F _fab_complete fab


## TODO

- store configs in db
- separate deploying from deploys
- 更新配置文件的配置方式，貌似现在的配置文件有点让人崩溃
- 更多的错误处理
- TBD: 把relay上的release_scripts下相关的脚本，整合进来


## 参考文档

- [fedora RPM 指南](http://docs.fedoraproject.org/en-US/Fedora_Draft_Documentation/0.1/html/RPM_Guide/)
- [Fabric API](http://docs.fabfile.org/en/1.7/index.html)
- [Using rpm to Install System Scripts in Linux](http://www.logiqwest.com/TechnicalPapers/rpmScriptInstall.html)
- [RPM 包的版本号比较](http://shuizhuyuanluo.blog.163.com/blog/static/778181201051972214868/)
