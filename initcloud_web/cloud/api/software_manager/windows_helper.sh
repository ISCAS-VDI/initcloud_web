#!/bin/sh

DIR="/root/tmp/"

# .Net4
wget -P $DIR 'https://download.microsoft.com/download/9/5/A/95A9616B-7A37-4AF6-BC36-D6EA96C8DAAE/dotNetFx40_Full_x86_x64.exe'

# Powershell 3.0
wget -P $DIR 'https://download.microsoft.com/download/E/7/6/E76850B8-DA6E-4FF5-8CCE-A24FC513FD16/Windows6.1-KB2506143-x86.msu'
# If you are using x64 system, please use the following command to download the right version
wget -P $DIR 'https://download.microsoft.com/download/E/7/6/E76850B8-DA6E-4FF5-8CCE-A24FC513FD16/Windows6.1-KB2506143-x64.msu'

wget -P $DIR 'https://raw.githubusercontent.com/litterbear/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1'

# wget -P $DIR 'https://notepad-plus-plus.org/repository/7.x/7.3/npp.7.3.Installer.exe'
# wget -P $DIR 'https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi'

for url in `python -c "import api; api.Config.print_package_urls()"` ; do
    wget -P $DIR "$url"
done

cat <<EOF > $DIR/enable-http-5985
winrm set winrm/config/service/auth @{Basic="true"}
winrm set winrm/config/service @{AllowUnencrypted="true"}
winrm set winrm/config/client/auth @{Basic="true"}
winrm set winrm/config/client @{AllowUnencrypted="true"}
EOF


cd $DIR

python -m SimpleHTTPServer
