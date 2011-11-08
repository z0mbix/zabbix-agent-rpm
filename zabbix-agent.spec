Name:           zabbix-agent
Version:        1.8.8
Release:        1%{?dist}
Summary:        Zabbix Agent - Open-source monitoring solution for your IT infrastructure
Group:          Applications/Internet
License:        GPL
URL:            http://www.zabbix.com/
Source0:        http://downloads.sourceforge.net/zabbix/zabbix-%{version}.tar.gz
Source1:        zabbix-agent.rc
Source2:        zabbix-agent.logrotate
Source3:		zabbix_agentd_userparams.conf
Source4:		zabbix_agentd.conf
Buildroot:      %{_tmppath}/zabbix-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  curl-devel net-snmp-devel
Requires:       logrotate, net-snmp-libs
Requires(pre):      /usr/sbin/useradd
Requires(post):     /sbin/chkconfig
Requires(preun):    /sbin/chkconfig
Requires(preun):    /sbin/service


%description
The zabbix client agent, to be installed on monitored systems.


%prep
%setup -q -n zabbix-%{version}

# fix up some lib64 issues
%{__perl} -pi.orig -e 's|_LIBDIR=/usr/lib|_LIBDIR=%{_libdir}|g' \
    configure


%build
%configure \
    --enable-agent \
    --with-net-snmp \
    --with-libcurl \

make %{?_smp_mflags}

echo $RPM_BUILD_ROOT

%install
rm -rf $RPM_BUILD_ROOT

# Setup required directories
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/zabbix
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/init.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_datadir}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/zabbix
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/zabbix

# Install init script
install -m 0755 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/init.d/%{name}

# Setup log rotation
install -m 0755 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

# Put config files in place
install -m 0640 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/zabbix
install -m 0640 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/zabbix
install -m 0640 misc/conf/zabbix_agent.conf $RPM_BUILD_ROOT%{_sysconfdir}/zabbix

# make install zabbix-agent
make DESTDIR=$RPM_BUILD_ROOT install

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "zabbix" user
/usr/sbin/useradd -c "Zabbix Monitoring System" \
        -s /sbin/nologin -r -d %{_localstatedir}/lib/zabbix zabbix 2> /dev/null || :

%post
# Add zabbix-agent to system start-up
/sbin/chkconfig --add %{name}

%preun
# Stop and disable service before removal
if [ "$1" = 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%dir %{_sysconfdir}/zabbix
%{_sbindir}/zabbix_agent
%{_sbindir}/zabbix_agentd
%{_bindir}/zabbix_sender
%{_bindir}/zabbix_get
%{_sysconfdir}/init.d/%{name}
%{_mandir}/man8/zabbix_agentd.8*
%{_mandir}/man1/zabbix_get.1*
%{_mandir}/man1/zabbix_sender.1*
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0640,zabbix,zabbix) %config(noreplace) %{_sysconfdir}/zabbix/zabbix_agent.conf
%attr(0640,zabbix,zabbix) %config(noreplace) %{_sysconfdir}/zabbix/zabbix_agentd.conf
%attr(0640,zabbix,zabbix) %config(noreplace) %{_sysconfdir}/zabbix/zabbix_agentd_userparams.conf
%attr(0755,zabbix,zabbix) %dir %{_localstatedir}/log/zabbix
%attr(0755,zabbix,zabbix) %dir %{_localstatedir}/run/zabbix

%changelog
* Tue Oct 20 2011 David Wooldridge <zombie@zombix.org> - 1.8.8-1
- Initial RPM build for 1.8.8
