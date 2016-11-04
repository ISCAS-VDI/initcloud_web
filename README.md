# initcloud_web
Web interface for VDI administrator.

## Prepare
兼容的Openstack版本为L版

首先启动虚拟环境：
如果你的虚拟环境安装的地址是  /var/www/initcloud_web/.venv/ ， 那么请先运行 
```shell
source /var/www/initcloud_web/.venv/bin/activate
```
来激活虚拟环境。

安装相应的软件依赖
```shell
sudo yum install libyaml-devel.x86_64
pip install xmltodict  "pywinrm>=0.1.1"
```

下载ansible代码并安装
```shell
git clone https://github.com/ISCAS-VDI/ansible
cd ansible 
git submodule update --init --recursive
python setup.py install
```
在initcloud_web/cloud/api/software_manager/ansible_hosts.py下有config.yml的样例

## Configuration
1. settings: MGR_HTTP_ADDR, MGR_WS_ADDR, COMPUTE_HOST
