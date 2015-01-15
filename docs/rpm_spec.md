RPM SPEC在实际打包过程中，需要了解的有一下几点

1. 常用宏的含义
2. RPM SPEC中小节的含义(%post, %pre之类)
3. 如何debug RPM包


## 常用宏

### %{installprefix}

应用安装后的父目录名，一般为/web,比如你的应用为mop/gift，settings中的location为
gift,那么安装后，应用路径就是：

    /web/gift


### ${RPM_BUILD_ROOT}

** The buildroot, on the other hand, acts as a staging area that looks like the final installation directory. The name buildroot refers to the fact that the final installation directory is usually the root directory, /. The install section of the spec file installs files into the buildroot directory in the proper subdirectories, as if the files were really under the system root directory, /. This allows the buildroot directory to hold all the final installed files for a package, so you can see what will really be installed by the package. **

You should always set the buildroot by defining a Buildroot: entry in your spec file. For example:

    Buildroot: %{_tmppath}/%{name}-%{version}-root

This example sets the buildroot under the temporary directory named in the %_tmppath macro. The subdirectory is named based on the name and version of the package. For example, for a package named ypbind and a version 1.12, with a %_tmppath value of /tmp, the final buildroot directory would be:

    /tmp/ypbind-1.12-root

Once you set a buildroot, your scripts run from the spec file and commands within the spec file can access the buildroot using the RPM_BUILD_ROOT environment variable. You normally need to access the RPM_BUILD_ROOT environment variable in the install section of the spec file.


## RPM SPEC小节

我们需要关注的小节主要是: `%install`, `%files`, `%post`


### install

这个小节里面的内容，可以是shell script，主要的用途是，讲我们的应用程序文件拷贝
到虚拟的安装目录中去(RPM_BUILD_ROOT), 如果有static包，那么需要把static文件单独
拷贝到安装目录。

    rm -rf ${RPM_BUILD_ROOT} # 清理虚拟安装目录
    mkdir -p ${RPM_BUILD_ROOT}%{installprefix} # 重新建一个虚拟目录
    cp -pr * ${RPM_BUILD_ROOT}%{installprefix}/{{ name }}  # 把应用文件拷贝到安装目录
    # 把静态文件拷贝到安装目录
    cp -pr %{packagename}/vno/static ${RPM_BUILD_ROOT}%{installprefix}/{{ name }}

注意，由于我们的静态文件包是安装在静态资源服务器上的，所以，`cp static`到安装目录，
不会和我们的程序(code)文件有冲突。


### files

files小节，主要是列出RPM包中的所有文件,如果列出的文件和实际RPM包中的文件不一致，
打包会报错。

    %defattr(-,www,www) # 设置目录的基本属性
    %dir %attr(-,www,www)%{installprefix}/{{ name }} # 单独对目录申明
    %{installprefix}/{{ name }} # 偷懒的做法，这个目录下的文件都是RPM包中的
    %exclude %{installprefix}/{{ static_name }}/static # 不包含安static目录


### post

post小节是在安装完RPM包后，我们需要执行的脚本,比如重启应用之类的


## 如何debug

在打包过程中，会有很多的打包日志，里面包含了打包的过程，仔细看这个日子，你会发现，
RPM打包系统具体做的事情，比如:解开tar包，移动程序文件到虚拟目录等

当然，打包完成后，如果不放心，可以检查一下包中的文件，可以登录到打包服务器，找到
你的RPM包(~/RPMS/{arch}), 然后执行 `rpm -qpl package`：

    [In] : rpm -qpl example_mop_webpass-2-3.0.noarch.rpm
    [Out]: /web/webpass
    [Out]: /web/webpass/protected
    [Out]: /web/webpass/protected/action
    [Out]: /web/webpass/protected/action/add_package.php
    [Out]: /web/webpass/protected/action/add_webpass_user.php
    [Out]: /web/webpass/protected/action/api
    [Out]: /web/webpass/protected/action/api/package_list.php
    [Out]: /web/webpass/protected/action/api/startup.php

这些输出的路径，就是安装后，文件的具体位置
