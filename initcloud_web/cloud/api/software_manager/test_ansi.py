import api

# host = "192.168.1.202"
host = "192.168.150.101"

def test_install():
    print api.get_installed_software(host)
    api.install_software([api.Config.package_list[1]["Product_Id"]], [host])
    print api.get_installed_software(host)
    api.uninstall_software([api.Config.package_list[1]["Product_Id"]], [host])
    print api.get_installed_software(host)


def test_reg():
    # api.set_reg([host], key="HKU:\.DEFAULT\Software\MyCompany", value="Young", data="good")
    code = api.set_reg([host], key=r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="Wallpaper", data=r"C:\pic1.jpg")
    print "return code:", code
    code = api.set_reg([host], key=r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="NoDispScrSavPage", data=1, datatype="dword")
    print "return code:", code

def test_global_reg():
    code = api.set_reg([host], key=r"HKU:\.DEFAULT\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="Wallpaper", data=r"C:\pic1.jpg")
    code = api.set_reg([host], key=r"HKU:\.DEFAULT\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="NoDispScrSavPage", data=1, datatype="dword")


def test_global_reg2():
    code = api.set_reg([host], key=r"HKU:\*\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="Wallpaper", data=r"C:\pic1.jpg")
    code = api.set_reg([host], key=r"HKU:\*\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="NoDispScrSavPage", data=1, datatype="dword")


def change_defualt_user_reg():
    code = api.set_reg([host], key=r"HKU:\default_profile\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="Wallpaper", data=r"C:\pic.jpg")
    code = api.set_reg([host], key=r"HKU:\default_profile\Software\Microsoft\Windows\CurrentVersion\Policies\System", value="NoDispScrSavPage", data=1, datatype="dword")


def hide_user():
    code = api.set_reg([host], key=r"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList", value="iscas", data=0, datatype="dword")



def set_wallpaper():
    # code = api.set_wallpaper([host], "secret")
    code = api.set_wallpaper([host], "normal")

def test_install_new_program():
    print api.get_installed_software(host)
    api.install_software([api.Config.package_list[3]["Product_Id"]], [host])
    print api.get_installed_software(host)
    api.uninstall_software([api.Config.package_list[3]["Product_Id"]], [host])
    print api.get_installed_software(host)

# test_reg()
# test_install()
# test_global_reg()
# test_global_reg2()

# change_defualt_user_reg()
# hide_user()

# set_wallpaper()

test_install_new_program()
