# coding:utf8

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager

runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=1) 
import os


def execute_a_task(play_name, tasks, hosts, host_list='/etc/ansible/hosts'):
    # initialize needed objects
    variable_manager = VariableManager()
    loader = DataLoader()

    # create inventory and pass to var manager
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=host_list)
    variable_manager.set_inventory(inventory)

    # create play with tasks
    play_source =  dict(
            name = play_name,
            hosts = hosts,
            # gather_facts = 'no',
            gather_facts = 'yes',
            tasks = tasks,
        )

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)


    Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
    options = Options(connection=None, module_path=None, forks=10, become=None, become_method=None, become_user=None, check=False)
    passwords = dict()

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
                  inventory=inventory,
                  variable_manager=variable_manager,
                  loader=loader,
                  options=options,
                  passwords=passwords,
                  stdout_callback='default',
                  # stdout_callback=f,
              )
        return tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()
        pass


class Config(object):
    dest_dir = r'C:\\ansible\\'
    package_dir = "/root/tmp/"
    pakage_list = [
        {
            "name": "Microsoft Visual C thingy",
            "filename": r'vcredist_x64.exe',
            "Product_Id": "{CF2BEA3C-26EA-32F8-AA9B-331F7E34BA97}",
            "InstallArguments": "/install /passive /norestart",
            "UninstallArguments": "/uninstall /passive /norestart",
        }
    ]
    

# 1. 获取可安装软件的列表
def get_available_software():
    return Config.package_list


# 2. 获取某个虚拟机已安装软件的列表
def get_installed_software(host):
    # TODO: how to get the installed softwares?
    return []


# 3. 给指定虚拟机(列表)安装指定的软件(列表)
def install_software(software_list, hosts_list):
    for hosts in hosts_list:
        for software in software_list:
            execute_a_task(play_name="Installing software", tasks = [
                    dict(action=dict(module="win_file", args=dict(
                        path=Config.dest_dir,
                        state='directory',
                    ))),
                    dict(action=dict(module="win_copy", args=dict(
                        src=os.path.join(Config.package_dir, software['filename']),
                        dest=Config.dest_dir,
                    ))),
                    dict(action=dict(module='win_package', args=dict(
                        name=software["name"],
                        path=Config.dest_dir + software['filename'],
                        Product_Id=software["Product_Id"],
                        Arguments=software["InstallArguments"],
                    )), name="Installing" + software["name"]),
                 ], hosts=hosts)


# 4. 卸载指定虚拟机的指定软件(列表)
def uninstall_software(software_list, hosts_list):
    for hosts in hosts_list:
        for software in software_list:
            execute_a_task(play_name="Uninstalling software", tasks = [
                    dict(action=dict(module="win_file", args=dict(
                        path=Config.dest_dir,
                        state='directory',
                    ))),
                    dict(action=dict(module="win_copy", args=dict(
                        src=os.path.join(Config.package_dir, software['filename']),
                        dest=Config.dest_dir,
                    ))),
                    dict(action=dict(module='win_package', args=dict(
                        name=software["name"],
                        path=Config.dest_dir + software['filename'],
                        Product_Id=software["Product_Id"],
                        Arguments=software["UninstallArguments"],
                        state="absent",
                    )), name="Uninstalling" + software["name"]),
                 ], hosts="test-win1")


# install_software(Config.pakage_list, ["test-win1"])
# uninstall_software(Config.pakage_list, ["test-win1"])
# uninstall_software(None, None)

# t, p = execute_a_task(play_name="setup software", tasks = [
#         dict(action=dict(module="setup")),
#      ], hosts=["test-win1"])


# execute_a_task(play_name="setup software", tasks = [
#         dict(action=dict(module="setup")),
#      ], hosts=["test-win1"])
