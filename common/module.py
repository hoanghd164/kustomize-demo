#!/usr/bin/env python3
from common.envs import *

if output == True:
    output = ''
else:
    output = '>/dev/null 2>&1'

class file_json:
    def json_read(file_name):
        f = open(file_name, encoding='utf-8')
        value = json.load(f)
        f.close()
        return value

    def json_write(file_name, value):
        f = open(file_name, 'w', encoding='utf-8')
        json.dump(value, f, indent=4, ensure_ascii=False)
        f.close()
        return True

    def json_read_url(url):
        url_response = urlopen(url)
        value = json.loads(url_response.read().decode())
        return value

class file_option:
    def file_read(file_name):
        with open(file_name) as rf:
            value = rf.read()
            return value

    def file_write(file_name,value):
       with open(file_name, 'w+') as wf:
            value = wf.writelines(value)

    def val_add_to_file(file_name,value):
       with open(file_name, 'a') as wf:
            value = wf.writelines(value)

    def file_remove(file_name):
        if os.path.exists(file_name):
          os.remove(file_name)

class folder_option:
    def maker_folder(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def remove_folder(dir_name):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

class loops:
    def listMenu(values,count = 1):
        for item in values:
            print(str(count) + ') '+ list(item.values())[0])
            count += 1

    def listmenu_noDict(values,count = 1):
        for item in values:
            print(str(count) + ') '+ item)
            count += 1

    def choiseMenu(values):
        choise = int(input("\n- Your choice is: "))
        if choise <= len(values):
            return list(values[choise-1].keys())[0]
        else:
            try:
                choise = int(input("\n- Your selection does not exist, please choose from menu 1 to %s: " %(str(len(values)))))
                return list(values[choise-1].keys())[0]
            except:
                print('- Your selection does not exist, exited the selection menu.\n')

    def choiseMenu_noDict(values):
        choise = int(input("\n- Your choice is: "))
        if choise <= len(values):
            return values[choise-1]
        else:
            try:
                choise = int(input("\n- Your selection does not exist, please choose from menu 1 to %s: " %(str(len(values)))))
                return values[choise-1]
            except:
                print('- Your selection does not exist, exited the selection menu.\n')

class remoteAction:
    def sshRemote(sshPort,sshUser,ipaddr,commands):
        os.system('ssh -p %s -o StrictHostKeychecking=no %s@%s "%s" %s' %(sshPort,sshUser,ipaddr,commands,output))

    def sshpassRemote(sshPasswd,sshPort,sshUser,sshIpaddr,commands):
        os.system('sshpass -p %s ssh -p %s -o StrictHostKeychecking=no %s@%s "%s" %s' %(sshPasswd,sshPort,sshUser,sshIpaddr,commands,output))

    def scpRemote(sshPort,source,sshUser,sshIpaddr,destination):
        os.system('scp -r -p -P %s -o StrictHostKeychecking=no %s %s@%s:%s %s' %(sshPort,source,sshUser,sshIpaddr,destination,output))

    def scp_sshpassRemote(sshPasswd,sshPort,source,sshUser,sshIpaddr,destination):
        os.system('sshpass -p %s scp -r -p -P %s -o StrictHostKeychecking=no %s %s@%s:%s %s' %(sshPasswd,sshPort,source,sshUser,sshIpaddr,destination,output))
        
    def scp_remoteToLocal(sshPort,sshUser,sshIpaddr,srcRemote,desLocal):
        os.system('scp -r -p -P %s -o StrictHostKeychecking=no %s@%s:%s %s %s' %(sshPort,sshUser,sshIpaddr,srcRemote,desLocal,output))

class packagesInstall:
    def updateSystem():
        print('- Updating os and system')
        os.system('sudo apt update %s && sudo apt-get upgrade -y %s' %(output,output))

    def installPkgs(packages):
        if 'apt' in packages.keys():
            for packageApt in packages['apt']:
                print('- Installing %s package' %(packageApt))
                subprocess.check_output('command -v %s >/dev/null 2>&1 || (sudo apt install %s -y %s)' %(packageApt,packageApt,output), shell=True).decode("utf-8").strip('\n')

        if 'apt-get' in packages.keys():
            for packageGet in packages['apt-get']:
                print('- Installing %s package' %(packageGet))
                subprocess.check_output('command -v %s >/dev/null 2>&1 || (sudo apt-get install %s -y %s)' %(packageGet,packageGet,output), shell=True).decode("utf-8").strip('\n')

    def pythonModules(list_Module):
        for module in list_Module:
            try:
                subprocess.check_output('pip3 freeze | grep %s' %(module), shell=True).decode("utf-8").strip('\n')
                print('- Module %s already exists.' %(module))
            except subprocess.CalledProcessError:
                print('- Python install modules %s' %(module))
                file_option.file_write('requirements.txt',module)
                os.system('sudo pip3 install -r requirements.txt %s' %(output))
                os.system('sudo rm -rf requirements.txt' %(output))