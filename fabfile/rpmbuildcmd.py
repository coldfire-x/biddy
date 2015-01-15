# -*- coding: utf-8 -*-

import time, os, re, codecs

from jinja2 import Template
from fabric.api import local, run, put, cd, lcd, env, hide
from fabric.context_managers import settings

from . import get_build_config
from .gitcmd import GitCmds


class BuildRpm(object):
    ''' build rpm package and scp to yum repo '''

    def __init__(self, project, tag):
        self.project = project
        self.tag = tag
        self._tmpdir = None
        self._gitcmd = None

    @property
    def gitcmd(self):
        ''' get git command wrapper '''
        if self._gitcmd:
            return self._gitcmd

        else:
            self._gitcmd = GitCmds(self.tmpdir) # tmpdir as git's working dir
            return self._gitcmd

    @property
    def tmpdir(self):
        ''' create a temporaty working directory '''
        if not self._tmpdir:
            random = str(time.time()).split('.')[0] + 'rpmbuildtmp'
            self._tmpdir = os.path.join('/tmp', random)

            if not os.path.exists(self._tmpdir):
                os.makedirs(self._tmpdir)
            else:
                local('cd %s && rm -rf ./*' % self._tmpdir)

        return self._tmpdir

    def run_build_script(self):
        ''' if project has a build script `build`, run it '''
        with lcd(self.tmpdir):
            local('if [ -e build ]; then /bin/bash ./build; fi')

    def create_tarball(self, tarballname):
        ''' create a tarball without `.git` `.gitignore` files '''
        dirname = tarballname
        if not tarballname.endswith('.tar.gz'):
            tarballname += '.tar.gz'
        else:
            dirname = tarballname.split('.')[0]

        self.tarballname = tarballname

        with lcd(os.path.dirname(self.tmpdir)):
            local('rm -rf %s' % dirname)
            local('mv %s %s' % (self.tmpdir, dirname))
            local('tar czf %s --exclude ".git" --exclude ".gitignore" %s'
                % (tarballname, dirname))
            local('rm -rf %s' % dirname)

        self.tarball_location = os.path.join('/tmp', tarballname)

    def _proces_tag(self, tag):
        ''' get rpm version from tag

        Note: the tag MUST contain at least three parts separated by period `.`
        '''
        pattern = re.compile(r'(\d{1,}\.){2}\d{1,}')
        sre = pattern.search(tag)
        return sre.group()

    def render_spec_file(self, project, tag):
        ''' render rpm spec file '''
        tmpl = project.tmpl
        with codecs.open(os.path.join('templates', tmpl), encoding='utf8') as f:
            tmpl_file = f.read()
            template = Template(tmpl_file)

        packagename = project.package_name

        # tag的名称应该是：版本.release.minor
        tag = self._proces_tag(tag)
        version, release, minor = tag.split('.')
        self.version = version
        self.release = release
        self.minor = minor

        source = self.tarballname
        name = project.location
        static_name = project.static_location
        arch = project.arch
        spec = template.render(locals())

        with lcd('/tmp'):
            spec_file = project.tmpl.rsplit('.', 1)[0]
            with codecs.open(os.path.join('/tmp', spec_file),
                encoding='utf8', mode='w') as f:
                f.write(spec)

        self.spec_name = spec_file
        self.spec_location = os.path.join('/tmp', spec_file)

    def _scp_to(self, dest, file):
        ''' scp file to dest '''
        local('scp %s %s' % (file, dest))

    def scp_spec_to(self, dest, spec_file):
        self._scp_to(dest, spec_file)

    def scp_source_to(self, dest, source):
        self._scp_to(dest, source)

    def do_build_rpm(self, dirname, spec):
        ''' run rpmbuild command in building box '''
        with settings(host_string=self.config.builder):
            with cd(dirname):
                run('rpmbuild -ba %s' % spec)

    def rpm_name(self, pkg_name, arch):
        return "%s-%s-%s.%s.%s.rpm" % (pkg_name, self.version,
            self.release, self.minor, arch)

    def scp_rpm_to_repo(self, arch, rpm):
        ''' scp rpm packages to yum repo '''
        with settings(host_string=self.config.builder):
            real_path = os.path.join(self.config.rpmdir, arch)
            with cd(real_path):
                rpm_dest = os.path.join(self.config.yumrepo, arch)
                run("scp %s %s" % (rpm, rpm_dest))

    def update_repos(self, arch):
        ''' after scp rpm packages to yum repo, update repo meta info '''
        with settings(
            # hide stderr and stdout log, only keep warnings and running log
            hide('stderr', 'stdout',),
            host_string=self.config.builder):
            rpm_path = os.path.join(self.config.os_repo_base_dir, arch)
            # 在builder机器上ssh到yumrepo服务器 并且更新repo元信息
            refresh_cmd = "ssh %s@%s createrepo --update %s" % (
                self.config.repo_user, self.config.repo_host, rpm_path)
            run(refresh_cmd)

    def prepare(self):
        # check tag from git
        gitrepo = self.project.gitrepo
        self.gitcmd.clone(gitrepo)
        self.gitcmd.checkout(self.tag)

        # 检查是否有./build脚本，有的话执行改脚本
        self.run_build_script()

        # 把项目文件打成tar.gz包
        self.create_tarball(self.project.package_name)

        # 生成spec文件
        self.render_spec_file(self.project, self.tag)

    def scp_tar_spec_to_building_machine(self):
        # scp spec and tarball to building machine's directory
        self.scp_spec_to(self.config.get_specdir(), self.spec_location)
        self.scp_source_to(self.config.source_dir, self.tarball_location)

    def build_rpm(self):
        self.do_build_rpm(self.config.specdir, self.spec_name)

    def scp_to_yumrepo(self):
        rpmname = self.rpm_name(self.project.package_name, self.project.arch)
        self.scp_rpm_to_repo(self.project.arch, rpmname)

        if self.project.static_location:
            rpmname = self.rpm_name("%s-static" % self.project.package_name,
                self.project.arch)
            self.scp_rpm_to_repo(self.project.arch, rpmname)

        self.update_repos(self.project.arch)

    def _cleanup(self):
        local('rm -rf %s' % self.tarball_location)
        local('rm -rf %s' % self.spec_location)

    def execute(self):
        # check out project, create tarball
        self.prepare()

        for osver in self.project.os:
            self.config = get_build_config(osver)
            # scp tarball and spec file to building machine
            self.scp_tar_spec_to_building_machine()
            self.build_rpm()
            if not env.build_only:
                self.scp_to_yumrepo()

        self._cleanup()
