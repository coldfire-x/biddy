## 基本命令

1. 安装包 `yum install package-name`
2. 升级包到最新版本 `yum upgrade package-name`
3. 降级包到之前的版本 `yum downgrade package-name`
4. 查看包的信息 `yum info package-name`
5. 清空缓存的meta信息 `yum clean metadata`
6. 安装特定版本 `yum install example_mop_gift-1-5.3`


## Yum Repo tips
*  在/etc/yum.conf中添加 metadata_expire = 60 [metadata过期时间设置为60秒]

## Yum运行的时候出现segmentfault
* 参考这篇文章: [centos yum Segmentation fault](http://hi.baidu.com/zys1234/item/f9282042038de4d2c0a5926b)

## 参考文档

1. [How To Download a RPM Package Using yum Command Without Installing On Linux](http://www.cyberciti.biz/faq/yum-downloadonly-plugin/)
