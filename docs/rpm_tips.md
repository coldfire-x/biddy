# RPM Packaging

## Build Guide
* 创建一个专用的rpmbuild账户 请勿使用root做build
* 在builder的home目录添加.rpmmacros
  文件中加入:

    %_topdir %(echo $HOME)/rpmbuild
    %_buildrootdir %{_topdir}/BUILD

* 生成gpg的key 对每个自己打的包签名

## RPM Tips
* rpm --showrc will show all macros
* rpm --eval %{macroname} will evaluate macroname

## PHP 项目注意事项

在post小节中添加重载php-fpm脚本:

    fpmmasters=`ps -ef | egrep "php-fpm.*master" | grep -v grep | awk '{print $2}'`
    for master in $fpmmasters; do
        kill -USR2 $master
    done

* 自己build的rpm包放在~/path/to/ftp/pub/yumrepos/example/{OSVER}
  . 对应包的arch存放
  . 增加或者删除rpms后 更新repo信息 createrepo --update dir
