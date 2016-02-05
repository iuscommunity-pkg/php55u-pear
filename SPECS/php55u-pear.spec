%global peardir %{_datadir}/pear
%global metadir %{_localstatedir}/lib/pear

%global getoptver 1.4.1
%global arctarver 1.4.0
%global structver 1.1.1
%global xmlutil   1.3.0
# all changes to man pages came from http://pkgs.fedoraproject.org/cgit/php-pear.git/commit/?id=ee18e3c185edb01c98517f5188fd802411170397
%global manpages  1.10.0

# Tests are only run with rpmbuild --with tests
# Can't be run in mock / koji because PEAR is the first package
%global with_tests       %{?_with_tests:1}%{!?_with_tests:0}

%if 0%{?rhel} >= 7
%global _macrosdir %{_rpmconfigdir}/macros.d
%else
%global _macrosdir %{_sysconfdir}/rpm
%endif

%define php_base php55u
%define real_name php-pear

Summary: PHP Extension and Application Repository framework
Name: %{php_base}-pear
Version: 1.10.1
Release: 2.ius%{?dist}
Epoch: 1
# PEAR, PEAR_Manpages, Archive_Tar, XML_Util, Console_Getopt are BSD
# Structures_Graph is LGPLv3+
License: BSD and LGPLv3+
Group: Development/Languages
URL: http://pear.php.net/package/PEAR
Source0: http://download.pear.php.net/package/PEAR-%{version}.tgz
Source1: https://raw.githubusercontent.com/pear/pear-core/v%{version}/install-pear.php
Source3: strip.php
Source10: pear.sh
Source11: pecl.sh
Source12: peardev.sh
Source13: macros.pear
Source21: http://pear.php.net/get/Archive_Tar-%{arctarver}.tgz
Source22: http://pear.php.net/get/Console_Getopt-%{getoptver}.tgz
Source23: http://pear.php.net/get/Structures_Graph-%{structver}.tgz
Source24: http://pear.php.net/get/XML_Util-%{xmlutil}.tgz
# Man pages
Source25: http://pear.php.net/get/PEAR_Manpages-%{manpages}.tgz

BuildArch: noarch
BuildRequires: %{php_base}-cli
BuildRequires: %{php_base}-xml
BuildRequires: gnupg
%if %{with_tests}
BuildRequires:  %{_bindir}/phpunit
%endif

Provides: php-pear(Console_Getopt) = %{getoptver}
Provides: php-pear(Archive_Tar) = %{arctarver}
Provides: php-pear(PEAR) = %{version}
Provides: php-pear(Structures_Graph) = %{structver}
Provides: php-pear(XML_Util) = %{xmlutil}
Provides: php-pear(PEAR_Manpages) = %{manpages}
Provides: %{php_base}-pear(Console_Getopt) = %{getoptver}
Provides: %{php_base}-pear(Archive_Tar) = %{arctarver}
Provides: %{php_base}-pear(PEAR) = %{version}
Provides: %{php_base}-pear(Structures_Graph) = %{structver}
Provides: %{php_base}-pear(XML_Util) = %{xmlutil}
Provides: %{php_base}-pear(PEAR_Manpages) = %{manpages}

Provides: php-composer(pear/console_getopt) = %{getoptver}
Provides: php-composer(pear/archive_tar) = %{arctarver}
Provides: php-composer(pear/pear-core-minimal) = %{version}
Provides: php-composer(pear/structures_graph) = %{structver}
Provides: php-composer(pear/xml_util) = %{xmlutil}
Provides: %{php_base}-composer(pear/console_getopt) = %{getoptver}
Provides: %{php_base}-composer(pear/archive_tar) = %{arctarver}
Provides: %{php_base}-composer(pear/pear-core-minimal) = %{version}
Provides: %{php_base}-composer(pear/structures_graph) = %{structver}
Provides: %{php_base}-composer(pear/xml_util) = %{xmlutil}

Requires:  %{php_base}-cli

# IUS Stuff
Provides: %{real_name} = %{version}
Conflicts: %{real_name} < %{version}

# phpci detected extension
# PEAR (date, spl always builtin):
Requires:  %{php_base}-ftp
Requires:  %{php_base}-pcre
Requires:  %{php_base}-posix
Requires:  %{php_base}-tokenizer
Requires:  %{php_base}-xml
Requires:  %{php_base}-zlib
# Console_Getopt: pcre
# Archive_Tar: pcre, posix, zlib
Requires:  %{php_base}-bz2
# Structures_Graph: none
# XML_Util: pcre
# optional: overload and xdebug


%description
PEAR is a framework and distribution system for reusable PHP
components.  This package contains the basic PEAR components.


%prep
%setup -cT

# Create a usable PEAR directory (used by install-pear.php)
for archive in %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24} %{SOURCE25}
do
    tar xzf  $archive --strip-components 1 || tar xzf  $archive --strip-path 1
    file=${archive##*/}
    [ -f LICENSE ] && mv LICENSE LICENSE-${file%%-*}
    [ -f README ]  && mv README  README-${file%%-*}

    tar xzf $archive 'package*xml'
    [ -f package2.xml ] && mv package2.xml ${file%%-*}.xml \
                        || mv package.xml  ${file%%-*}.xml
done
cp %{SOURCE1} .


%build
# This is an empty build section.


%install
export PHP_PEAR_SYSCONF_DIR=%{_sysconfdir}
export PHP_PEAR_SIG_KEYDIR=%{_sysconfdir}/pearkeys
export PHP_PEAR_SIG_BIN=%{_bindir}/gpg
export PHP_PEAR_INSTALL_DIR=%{peardir}

# 1.4.11 tries to write to the cache directory during installation
# so it's not possible to set a sane default via the environment.
# The ${PWD} bit will be stripped via relocate.php later.
export PHP_PEAR_CACHE_DIR=${PWD}%{_localstatedir}/cache/php-pear
export PHP_PEAR_TEMP_DIR=/var/tmp

install -d $RPM_BUILD_ROOT%{peardir} \
           $RPM_BUILD_ROOT%{_localstatedir}/cache/php-pear \
           $RPM_BUILD_ROOT%{_localstatedir}/www/html \
           $RPM_BUILD_ROOT%{_localstatedir}/lib/pear/pkgxml \
           $RPM_BUILD_ROOT%{_docdir}/pecl \
           $RPM_BUILD_ROOT%{_datadir}/tests/pecl \
           $RPM_BUILD_ROOT%{_sysconfdir}/pear

export INSTALL_ROOT=$RPM_BUILD_ROOT

%{_bindir}/php -dmemory_limit=64M -dshort_open_tag=0 -dsafe_mode=0 \
         -d 'error_reporting=E_ALL&~E_DEPRECATED' -ddetect_unicode=0 \
         install-pear.php --force \
                 --dir      %{peardir} \
                 --cache    %{_localstatedir}/cache/php-pear \
                 --config   %{_sysconfdir}/pear \
                 --bin      %{_bindir} \
                 --www      %{_localstatedir}/www/html \
                 --doc      %{_docdir}/pear \
                 --test     %{_datadir}/tests/pear \
                 --data     %{_datadir}/pear-data \
                 --metadata %{metadir} \
                 --man      %{_mandir} \
                 %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24} %{SOURCE25}

# Replace /usr/bin/* with simple scripts:
install -m 755 %{SOURCE10} $RPM_BUILD_ROOT%{_bindir}/pear
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT%{_bindir}/pecl
install -m 755 %{SOURCE12} $RPM_BUILD_ROOT%{_bindir}/peardev

# Sanitize the pear.conf
%{_bindir}/php %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf ext_dir >new-pear.conf
%{_bindir}/php %{SOURCE3} new-pear.conf http_proxy > $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf

%{_bindir}/php -r "print_r(unserialize(substr(file_get_contents('$RPM_BUILD_ROOT%{_sysconfdir}/pear.conf'),17)));"


install -m 644 -D %{SOURCE13} \
           $RPM_BUILD_ROOT%{_macrosdir}/macros.pear

# Why this file here ?
rm -rf $RPM_BUILD_ROOT/.depdb* $RPM_BUILD_ROOT/.lock $RPM_BUILD_ROOT/.channels $RPM_BUILD_ROOT/.filemap

# Need for re-registrying XML_Util
install -m 644 *.xml $RPM_BUILD_ROOT%{_localstatedir}/lib/pear/pkgxml


%check
# Check that no bogus paths are left in the configuration, or in
# the generated registry files.
grep $RPM_BUILD_ROOT $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep %{_libdir} $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep '"/tmp"' $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep /usr/local $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep -rl $RPM_BUILD_ROOT $RPM_BUILD_ROOT && exit 1


%if %{with_tests}
cd $RPM_BUILD_ROOT%{pear_phpdir}/test/Structures_Graph/tests
phpunit \
   -d date.timezone=UTC \
   -d include_path=.:$RPM_BUILD_ROOT%{pear_phpdir}:%{pear_phpdir}: \
   AllTests || exit 1

cd $RPM_BUILD_ROOT%{pear_phpdir}/test/XML_Util/tests
phpunit \
   -d date.timezone=UTC \
   -d include_path=.:$RPM_BUILD_ROOT%{pear_phpdir}:%{pear_phpdir}: \
   AllTests || exit 1
%else
echo 'Test suite disabled (missing "--with tests" option)'
%endif


%pre
# Manage relocation of metadata, before update to pear
if [ -d %{peardir}/.registry -a ! -d %{metadir}/.registry ]; then
  mkdir -p %{metadir}
  mv -f %{peardir}/.??* %{metadir}
fi


%post
# force new value as pear.conf is (noreplace)
current=$(%{_bindir}/pear config-get test_dir system)
if [ "$current" != "%{_datadir}/tests/pear" ]; then
%{_bindir}/pear config-set \
    test_dir %{_datadir}/tests/pear \
    system >/dev/null || :
fi

current=$(%{_bindir}/pear config-get data_dir system)
if [ "$current" != "%{_datadir}/pear-data" ]; then
%{_bindir}/pear config-set \
    data_dir %{_datadir}/pear-data \
    system >/dev/null || :
fi

current=$(%{_bindir}/pear config-get metadata_dir system)
if [ "$current" != "%{metadir}" ]; then
%{_bindir}/pear config-set \
    metadata_dir %{metadir} \
    system >/dev/null || :
fi

current=$(%{_bindir}/pear config-get -c pecl doc_dir system)
if [ "$current" != "%{_docdir}/pecl" ]; then
%{_bindir}/pear config-set \
    -c pecl \
    doc_dir %{_docdir}/pecl \
    system >/dev/null || :
fi

current=$(%{_bindir}/pear config-get -c pecl test_dir system)
if [ "$current" != "%{_datadir}/tests/pecl" ]; then
%{_bindir}/pear config-set \
    -c pecl \
    test_dir %{_datadir}/tests/pecl \
    system >/dev/null || :
fi


%postun
if [ $1 -eq 0 -a -d %{metadir}/.registry ] ; then
  rm -rf %{metadir}/.registry
fi


%files
%{peardir}
%dir %{metadir}
%{metadir}/.channels
%verify(not mtime size md5) %{metadir}/.depdb
%verify(not mtime)          %{metadir}/.depdblock
%verify(not mtime size md5) %{metadir}/.filemap
%verify(not mtime)          %{metadir}/.lock
%{metadir}/.registry
%{metadir}/pkgxml
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/pear.conf
%{_macrosdir}/macros.pear
%dir %{_localstatedir}/cache/php-pear
%dir %{_localstatedir}/www/html
%dir %{_sysconfdir}/pear
%{!?_licensedir:%global license %%doc}
%license LICENSE*
%doc README*
%dir %{_docdir}/pear
%doc %{_docdir}/pear/*
%dir %{_docdir}/pecl
%dir %{_datadir}/tests
%dir %{_datadir}/tests/pecl
%{_datadir}/tests/pear
%{_datadir}/pear-data
%{_mandir}/man1/pear.1*
%{_mandir}/man1/pecl.1*
%{_mandir}/man1/peardev.1*
%{_mandir}/man5/pear.conf.5*


%changelog
* Thu Feb 04 2016 Carl George <carl.george@rackspace.com> - 1:1.10.1-2.ius
- Use correct macros directory on EL7
- Use correct licenses directory on EL7
- Include Source25 (PEAR_Manpages) in tarball strip for loop
- Provide php*-pear(PEAR_Manpages)
- Change Source1 to a direct url (credit: Steven Barre), fetch current version
- Console_Getopt is BSD license, Structures_Graph is LGPLv3+ license
- Set pecl doc_dir to /usr/share/doc/pecl (Fedora)
- Set pecl test_dir to /usr/share/tests/pecl (Fedora)
- Add composer provides (Fedora)
- Cleanup registry after removal (Fedora)
- Drop old php-pear-XML-Util scriptlets (Fedora)

* Tue Oct 27 2015 Ben Harper <ben.harper@rackspace.com> - 1:1.10.1-1.ius
- Latest upstream

* Fri Oct 09 2015 Ben Harper <ben.harper@rackspace.com> - 1:1.10.0-1.ius
- Latest upstream
- Update Archive_Tar to 1.4.0
- Update XML_Util to 1.3.0
- Update Structures_Graph to 1.1.1
- Update Console_Getopt to 1.4.1
- Update install-pear.php
- Remove patches, fixed upstream
- use PEAR_Manpages for man pages, taken from http://pkgs.fedoraproject.org/cgit/php-pear.git/commit/?id=ee18e3c185edb01c98517f5188fd802411170397 Thanks Remi

* Wed Oct 15 2014 Carl George <carl.george@rackspace.com> - 1:1.9.5-2.ius
- Conflict with less than %%{version}, not %%{basever}

* Fri Sep 12 2014 Carl George <carl.george@rackspace.com> - 1:1.9.5-1.ius
- Latest upstream
- Update Archive_Tar to 1.3.13
- Update XML_Util to 1.2.3
- Clean up requirements and provides
- Add pear.conf man page

* Thu Jul 11 2013 Ben Harper <ben.harper@rackspace.com> -  1:1.9.4-20.ius
- porting from php-pear-1.9.4-20.fc20.src.rpm

* Tue Jun 18 2013 Remi Collet <rcollet@redhat.com> 1:1.9.4-19
- add man pages for pear, peardev and pecl commands

* Fri May  3 2013 Remi Collet <rcollet@redhat.com> 1:1.9.4-18
- don't verify metadata file content

* Thu Apr 25 2013 Remi Collet <rcollet@redhat.com> 1:1.9.4-17
- improve post scriptlet to avoid updating pear.conf
  when not needed

* Tue Mar 12 2013 Ralf Corsépius <corsepiu@fedoraproject.org> - 1:1.9.4-16
- Remove %%config from %%{_sysconfdir}/rpm/macros.*
  (https://fedorahosted.org/fpc/ticket/259).

* Sat Feb  9 2013 Remi Collet <remi@fedoraproject.org> 1:1.9.4-15
- update Archive_Tar to 1.3.11
- drop php 5.5 patch merged upstream

* Tue Dec 11 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-14
- add explicit requires on all needed extensions (phpci)
- fix pecl launcher (need ini to be parsed for some
  extenstions going to be build as shared, mainly simplexml)
- add fix for new unpack format (php 5.5)

* Wed Sep 26 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-13
- move metadata to /var/lib/pear

* Wed Sep 26 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-12
- drop relocate stuff, no more needed

* Sun Aug 19 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-11
- move data to /usr/share/pear-data
- provides all package.xml

* Wed Aug 15 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-10
- enforce test_dir on update

* Mon Aug 13 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-9
- move tests to /usr/share/tests/pear
- move pkgxml to /var/lib/pear
- remove XML_RPC
- refresh installer

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.9.4-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr 11 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-7
- Update Archive_Tar to 1.3.10

* Wed Apr 04 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-6
- fix Obsoletes version for XML_Util (#226295)
- add link to upstream bug - please Provides LICENSE file
  https://pear.php.net/bugs/bug.php?id=19368
- add link to upstream bug - Incorrect FSF address
  https://pear.php.net/bugs/bug.php?id=19367

* Mon Feb 27 2012 Remi Collet <remi@fedoraproject.org> 1:1.9.4-5
- Update Archive_Tar to 1.3.9
- add patch from RHEL (Joe Orton)
- fix install-pear.php URL (with our patch for doc_dir applied)

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.9.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Oct 15 2011 Remi Collet <remi@fedoraproject.org> 1:1.9.4-3
- update Archive_Tar to 1.3.8
- allow to build with "tests" option

* Sat Aug 27 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.4-2
- update to XML_RPC-1.5.5

* Thu Jul 07 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.4-1
- update to 1.9.4

* Fri Jun 10 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.3-2
- fix pecl launcher

* Fri Jun 10 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.3-1
- update to 1.9.3
- sync options in launcher (pecl, pear, peardev) with upstream

* Wed Mar 16 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.2-3
- move %%{pear_docdir} to %%{_docdir}/pear
  https://fedorahosted.org/fpc/ticket/69

* Tue Mar  8 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.2-2
- update Console_Getopt to 1.3.1 (no change)

* Mon Feb 28 2011 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.2-1
- update to 1.9.2 (bug + security fix)
  http://pear.php.net/advisory-20110228.txt

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.9.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 12 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-6
- update Console_Getopt to 1.3.0
- don't require php-devel (#657812)
- update install-pear.php

* Tue Oct 26 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-5
- update Structures_Graph to 1.0.4

* Fri Sep 10 2010 Joe Orton <jorton@redhat.com> - 1:1.9.1-4
- ship LICENSE file for XML_RPC

* Fri Sep 10 2010 Joe Orton <jorton@redhat.com> - 1:1.9.1-3
- require php-devel (without which pecl doesn't work)

* Mon Jul 05 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-2
- update to XML_RPC-1.5.4

* Thu May 27 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.1-1
- update to 1.9.1

* Thu Apr 29 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-5
- update to Archive_Tar-1.3.7 (only metadata fix)

* Tue Mar 09 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-4
- update to Archive_Tar-1.3.6

* Sat Jan 16 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-3
- update to XML_RPC-1.5.3
- fix licenses (multiple)
- provide bundled LICENSE files

* Fri Jan 01 2010 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-2
- update to Archive_Tar-1.3.5, Structures_Graph-1.0.3

* Sat Sep 05 2009 Remi Collet <Fedora@FamilleCollet.com> 1:1.9.0-1
- update to PEAR 1.9.0, XML_RPC 1.5.2

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 30 2009 Remi Collet <Fedora@FamilleCollet.com> 1:1.8.1-1
- update to 1.8.1
- Update install-pear.php script (1.39)
- add XML_Util

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.7.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun May 18 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.2-2
- revert to install-pear.php script 1.31 (for cfg_dir)

* Sun May 18 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.2-1
- update to 1.7.2
- Update install-pear.php script (1.32)

* Tue Mar 11 2008 Tim Jackson <rpm@timj.co.uk> 1:1.7.1-2
- Set cfg_dir to be %%{_sysconfdir}/pear (and own it)
- Update install-pear.php script
- Add %%pear_cfgdir and %%pear_wwwdir macros

* Sun Feb  3 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.1-1
- update to 1.7.1

* Fri Feb  1 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.0-1
- update to 1.7.0

* Thu Oct  4 2007 Joe Orton <jorton@redhat.com> 1:1.6.2-2
- require php-cli not php

* Sun Sep  9 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.6.2-1
- update to 1.6.2
- remove patches merged upstream
- Fix : "pear install" hangs on non default channel (#283401)

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 1:1.6.1-2
- fix License

* Thu Jul 19 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.6.1-1
- update to PEAR-1.6.1 and Console_Getopt-1.2.3

* Thu Jul 19 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.5.4-5
- new SPEC using install-pear.php instead of install-pear-nozlib-1.5.4.phar

* Mon Jul 16 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.5.4-4
- update macros.pear (without define)

* Mon Jul 16 2007 Joe Orton <jorton@redhat.com> 1:1.5.4-3
- add pecl_{un,}install macros to macros.pear (from Remi)

* Fri May 11 2007 Joe Orton <jorton@redhat.com> 1:1.5.4-2
- update to 1.5.4

* Tue Mar  6 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-3
- add redundant build section (#226295)
- BR php-cli not php (#226295)

* Mon Feb 19 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-2
- update builtin module provides (Remi Collet, #226295)
- drop patch 0

* Thu Feb 15 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-1
- update to 1.5.0

* Mon Feb  5 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-4
- fix Group, mark pear.conf noreplace (#226295)

* Mon Feb  5 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-3
- use BuildArch not BuildArchitectures (#226925)
- fix to use preferred BuildRoot (#226925)
- strip more buildroot-relative paths from *.reg
- force correct gpg path in default pear.conf

* Thu Jan  4 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-2
- update to 1.4.11

* Fri Jul 14 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-4
- update to XML_RPC-1.5.0
- really package macros.pear

* Thu Jul 13 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-3
- require php-cli
- add /etc/rpm/macros.pear (Christopher Stone)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1:1.4.9-2.1
- rebuild

* Mon May  8 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-2
- update to 1.4.9 (thanks to Remi Collet, #183359)
- package /usr/share/pear/.pkgxml (#190252)
- update to XML_RPC-1.4.8
- bundle the v3.0 LICENSE file

* Tue Feb 28 2006 Joe Orton <jorton@redhat.com> 1:1.4.6-2
- set cache_dir directory, own /var/cache/php-pear

* Mon Jan 30 2006 Joe Orton <jorton@redhat.com> 1:1.4.6-1
- update to 1.4.6
- require php >= 5.1.0 (#178821)

* Fri Dec 30 2005 Tim Jackson <tim@timj.co.uk> 1:1.4.5-6
- Patches to fix "pear makerpm"

* Wed Dec 14 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-5
- set default sig_keydir to /etc/pearkeys
- remove ext_dir setting from /etc/pear.conf (#175673)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Dec  6 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-4
- fix virtual provide for PEAR package (#175074)

* Sun Dec  4 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-3
- fix /usr/bin/{pecl,peardev} (#174882)

* Thu Dec  1 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-2
- add virtual provides (#173806) 

* Wed Nov 23 2005 Joe Orton <jorton@redhat.com> 1.4.5-1
- initial build (Epoch: 1 to allow upgrade from php-pear-5.x)
