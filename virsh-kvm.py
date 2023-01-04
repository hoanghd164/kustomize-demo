#!/usr/bin/python3
from common.envs import *
from common.module import *
from infra.kubernetes import *

os.system('clear')

class kvm:
    def vars():
        dict_Vps = {'kubernetes': [
                {'k8s-master': {'cpu': 2, 'memory': 4, 'diskSize': 30,'sl': 2}},
                {'k8s-worker': {'cpu': 8, 'memory': 16, 'diskSize': 100,'sl': 3}},
                {'k8s-loadbalancer': {'cpu': 2, 'memory': 4, 'diskSize': 30,'sl': 2}}],
                'startIP': '192.168.13.218'
        }

        # dict_Vps = {'kubernetes': [
        #         {'kvm-node': {'cpu': 4, 'memory': 16, 'diskSize': 200,'sl': 1}},
        #     ], 'startIP': '172.16.1.101'
        # }

        dict_Authen = {
            'username': 'hoanghd',
            'passwd': 'hoanghd'
        }

        dict_rootDir = {
            'rootDir': '/volumes-hdd',
            # 'image_rootDir': '/var/lib/libvirt/images',
            'image_rootDir': '/volumes-hdd/images',
            'os_rootHDD': '/volumes-hdd/os',
            'os_rootSSD': '/volumes-ssd/os',
            'os_rootNVME': '/volumes-nvme/os'
        }

        dict_network = {
            'bridged-network': {'subnet' : '192.168.13.0', 'gateway' : '192.168.12.5', 'prefix' : 23},
            'nat-network-sub172': {'subnet' : '172.16.1.0','gateway' : '172.16.1.254','prefix' : 24}
        }

        image_Info = {
            'ubuntu22.04': {
                'image_url': 'https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img',
                'image_checksum': '',
                'image_checksum_type': 'sha256',
                'type_os' : 'Linux',
                'variant' : 'ubuntu18.04',
                'interface_name': 'enp1s0',
                'local_image': '%s/jammy-server-ubuntu2204-cloudimg-amd64.img' %(dict_rootDir['image_rootDir'])
            },
            'ubuntu20.04': {
                'image_url': 'https://cloud-images.ubuntu.com/minimal/releases/focal/release/ubuntu-20.04-minimal-cloudimg-amd64.img',
                'image_checksum': '49b7325603f92b9160d373ed1433f636622f9fa5cd4cb96567c64e35ab6eec6d',
                'image_checksum_type': 'sha256',
                'type_os' : 'Linux',
                'variant' : 'ubuntu18.04',
                'interface_name': 'enp1s0',
                'local_image': '%s/focal-server-ubuntu2004-cloudimg-amd64.img' %(dict_rootDir['image_rootDir'])
            },
            'ubuntu18.04': { 
                'minimal':{
                    'image_url': 'https://cloud-images.ubuntu.com/minimal/releases/bionic/release/ubuntu-18.04-minimal-cloudimg-amd64.img',
                    'image_checksum': '2f8c35d32e9c0e09efe75759e1c1b9c3dbd8f41392051e6c4220d2b689dc85b4',
                    'image_checksum_type': 'sha256',
                    'type_os' : 'Linux',
                    'variant' : 'ubuntu18.04',
                    'interface_name': 'enp1s0',
                    'local_image': '%s/bionic-server-ubuntu1804-cloudimg-amd64.img' %(dict_rootDir['image_rootDir'])
                    },
                'bionic':{
                    'image_url': 'https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img',
                    'image_checksum': 'a90ab7fa64b554bc8381397c4807d610d4b96d992fbfbac188687cba29168f1a',
                    'image_checksum_type': 'sha256',
                    'type_os' : 'Linux',
                    'variant' : 'ubuntu18.04',
                    'interface_name': 'enp1s0',
                    'local_image': '%s/bionic-server-ubuntu1804-cloudimg-amd64.img' %(dict_rootDir['image_rootDir'])
                    },
                },
            'centos7.0': {
                'image_url': 'https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2c',
                'image_checksum': '',
                'image_checksum_type': 'sha256',
                'type_os' : 'Linux',
                'variant' : 'centos7.0',
                'interface_name': 'eth0',
                'local_image': '%s/CentOS-7-x86_64-GenericCloud.qcow2c' %(dict_rootDir['image_rootDir'])
            },
            'win2k12r2': {
                'image_url': '',
                'image_checksum': '',
                'image_checksum_type': 'sha256',
                'type_os' : 'Windows',
                'variant' : 'win2k12r2',
                'interface_name': 'interface0',
                'local_image': '%s/windows_server_2012r2.iso' %(dict_rootDir['image_rootDir'])
            },
            'win2k16': {
                'image_url': '',
                'image_checksum': '',
                'image_checksum_type': 'sha256',
                'type_os' : 'Windows',
                'variant' : 'win2k16',
                'interface_name': 'interface0',
                'local_image': '%s/win2016en-standard-minimal.qcow2' %(dict_rootDir['image_rootDir'])
            },
            'win2k19': {
                'image_url': '',
                'image_checksum': '',
                'image_checksum_type': 'sha256',
                'type_os' : 'Windows',
                'variant' : 'win2k19',
                'interface_name': 'interface0',
                'local_image': '%s/win2019en-standard-minimal.qcow2' %(dict_rootDir['image_rootDir'])
            },
            'kubernetes-packer-image-ubuntu1804': {
                'image_url': '',
                'image_checksum': '',
                'image_checksum_type': 'sha256',
                'type_os' : 'Linux',
                'variant' : 'ubuntu18.04',
                'interface_name': 'enp1s0',
                'local_image': '%s/kubernetes-packer-image.qcow2' %(dict_rootDir['image_rootDir'])
            }
        }
        return dict_Vps, dict_Authen, dict_rootDir, dict_network, image_Info

    def define_Vps():
        temp_vpsName = 1
        temp_ipaddr = 1 
        list_Vps = []
        startIP = int(kvm.vars()[0]['startIP'].split('.')[-1])
        subnet = ".".join(kvm.vars()[0]['startIP'].split('.')[0:3])
        
        for src_Dictvps in kvm.vars()[0]['kubernetes']:
            vm_name = list(src_Dictvps.keys())[0]
            sl = int(list(src_Dictvps.values())[0]['sl'])
            diskSize = list(src_Dictvps.values())[0]['diskSize']
            diskSize = list(src_Dictvps.values())[0]['diskSize']
            cpu = list(src_Dictvps.values())[0]['cpu']
            memory = list(src_Dictvps.values())[0]['memory']
            old_vm_name = vm_name
            if old_vm_name == vm_name:
                temp_vpsName = 1
            while temp_vpsName <= sl:
                if sl == 1:
                    vps_name = vm_name
                else:
                    vps_name='%s%s'%(vm_name,temp_vpsName)
                ipaddr = '%s.%s' %(subnet,startIP + temp_ipaddr-1)
                vitualIP = '%s.%s' %(subnet,startIP + temp_ipaddr)
                list_Vps.append({'vps_name': vps_name, 'cpu': cpu,'memory': memory,'diskSize': diskSize,'ipaddr': ipaddr})
                temp_vpsName += 1
                temp_ipaddr += 1
        list_Vps.append({'vitualIP': vitualIP})
        return list_Vps

    def convert_kubernetes_vars():
        list_vars = kvm.define_Vps()
        vitualIP = list_vars[-1]['vitualIP']
        list_dict_master = []
        list_dict_worker = []
        list_dict_loadbalancer = []
        list_vars.pop()

        for x in list_vars:
            if 'master' in x['vps_name']:
                dict_vars_master = {x['vps_name']: x['ipaddr']}
                list_dict_master.append(dict_vars_master)

            elif 'worker' in x['vps_name']:
                dict_vars_worker = {x['vps_name']: x['ipaddr']}
                list_dict_worker.append(dict_vars_worker)

            elif 'loadbalancer' in x['vps_name']:
                dict_vars_loadbalancer = {x['vps_name']: x['ipaddr']}
                list_dict_loadbalancer.append(dict_vars_loadbalancer)

        dict_master = '\'masterNode\': %s' %(list_dict_master)
        dict_worker = '\'workerNode\': %s' %(list_dict_worker)
        dict_loadbalancer = '\'loadbalancerNode\': %s' %(list_dict_loadbalancer)
        dict_vitualIP = '\'vitualIP\': \'%s\'' %(vitualIP)
        developer_str = ('{%s, %s, %s, %s}' %(dict_master,dict_worker,dict_loadbalancer,dict_vitualIP)).replace("'",'"')
        finally_list_vars = json.loads(developer_str)
        file_json.json_write('dict_Node.json',finally_list_vars)
        return developer_str

    def create_diskOS(image_path,os_path,disk_size):
        os.system('qemu-img create -b %s -f qcow2 %s %sG %s' %(image_path,os_path,disk_size,output))
        if output == True:
            os.system('qemu-img info %s' %(os_path))
        
    def create_diskSeed(network_path,cloudinit_path,os_seed):
        os.system('cloud-localds -v --network-config=%s %s %s %s' %(network_path,os_seed,cloudinit_path,output))
        if output == True:
            os.system('qemu-img info %s' %(os_seed))

    def define_cloudinit(vps_type):
        currentDir = os.path.abspath(os.getcwd())
        cloudinit_config_path = '%s/kvm-config/cloudinit' %(currentDir)
        network_config_path = '%s/kvm-config/network' %(currentDir)
        if 'centos' in vps_type:
            cloudinit_config_path = '%s/cloud-init-centos7.cfg' %(cloudinit_config_path)
            network_config_path = '%s/network_static_centos.cfg' %(network_config_path)
        elif 'ubuntu' in vps_type:
            cloudinit_config_path = '%s/cloud-init-ubuntu.cfg' %(cloudinit_config_path)
            network_config_path = '%s/network_static_ubuntu.cfg' %(network_config_path)
        elif 'win' in vps_type:
            cloudinit_config_path = '%s/cloud-init-windows.cfg' %(cloudinit_config_path)
            network_config_path = '%s/network_static_windows.cfg' %(network_config_path)
        return cloudinit_config_path, network_config_path

    def config_cloudinit(cloudinit_path_default,network_path_default,cloudinit_path,network_path,hostname,interface_name,ipaddr,prefix,gateway,username,passwd):
        dict_cloudinit = {
            'cloud-config-fqdn': hostname,
            'cloud-config-hostname': hostname,
            'cloud-config-vps_interface_name': interface_name,
            'cloud-config-vps_ipaddr': ipaddr,
            'cloud-config-vps_prefix': str(prefix),
            'cloud-config-vps_gateway': gateway,
            'cloud-config-username': username,
            'cloud-config-password': passwd
        }
        os.system('cp %s %s.bak' %(cloudinit_path_default,cloudinit_path_default))
        for key,value in dict_cloudinit.items():
            read_cloudinit = file_option.file_read('%s.bak' %(cloudinit_path_default))
            replaced_text = read_cloudinit.replace(key,value)
            file_option.file_write('%s.bak' %(cloudinit_path_default),replaced_text)
        ssh_path = cloudinit_path.split('/')
        ssh_path.pop()
        ssh_path = "/".join(ssh_path)
        read_cloudinit_add_sshkey = file_option.file_read('%s.bak' %(cloudinit_path_default))
        read_sshkey = file_option.file_read('%s/sshkey/id_rsa.pub' %(ssh_path))
        replaced_sshkey = read_cloudinit_add_sshkey.replace('cloud-config-keygen',read_sshkey)
        file_option.file_write('%s.bak' %(cloudinit_path_default),replaced_sshkey)
        # sshKey = 'ssh -i %s/sshkey/id_rsa -o StrictHostKeychecking=no ubuntu@%s' %(ssh_path,dict_cloudinit['cloud-config-vps_ipaddr'])
        sshKey = 'ssh -o StrictHostKeychecking=no root@%s' %(ipaddr)
        file_option.file_write('%s/sshkey/sshkey.info' %(ssh_path),sshKey)
        os.system('rm -rf %s && mv %s.bak %s' %(cloudinit_path,cloudinit_path_default,cloudinit_path))

        os.system('cp %s %s.bak' %(network_path_default,network_path_default))
        for key,value in dict_cloudinit.items():
            read_cloudinit = file_option.file_read('%s.bak' %(network_path_default))
            replaced_text = read_cloudinit.replace(key,value)
            file_option.file_write('%s.bak' %(network_path_default),replaced_text)
        os.system('rm -rf %s && mv %s.bak %s' %(network_path,network_path_default,network_path))

    def vps_choiseOS():
        listOS = [{'ubuntu18.04': 'Ubuntu-18.04'}, {'ubuntu20.04': 'Ubuntu-20.04'}, {'ubuntu22.04': 'Ubuntu-22.04'}, {'centos7.0': 'CentOS7.0'}, {'kubernetes-packer-image-ubuntu1804': 'Kubernetes Ubuntu-18.04'}, {'win2k12r2': 'Windows server 2012 R2'}, {'win2k16': 'Windows server 2016'}, {'win2k19': 'Windows server 2019'}]
        loops.listMenu(listOS)
        vps_choiseOS = loops.choiseMenu(listOS)
        return vps_choiseOS

    def define_path(vps_name,vps_type,disk_type):
        path_info = []
        os_rootHDD = kvm.vars()[2]['os_rootHDD']
        os_rootSSD = kvm.vars()[2]['os_rootSSD']
        os_rootNVME = kvm.vars()[2]['os_rootNVME']
        folder_option.maker_folder(os_rootHDD)
        folder_option.maker_folder(os_rootSSD)
        folder_option.maker_folder(os_rootNVME)
        kvm.define_cloudinit(vps_type)

        if vps_type == 'ubuntu18.04':
            interface_name = kvm.vars()[4][vps_type]['bionic']['interface_name']
            image_path = kvm.vars()[4][vps_type]['bionic']['local_image']
        else:
            interface_name = kvm.vars()[4][vps_type]['interface_name']
            image_path = kvm.vars()[4][vps_type]['local_image']

        if disk_type == 'hdd':
            path_sshkey = '%s/%s/%s/sshkey/id_rsa' %(os_rootHDD,vps_type,vps_name)
            if os.path.exists(path_sshkey) == False:
                folder_option.maker_folder('%s/%s/%s/sshkey' %(os_rootHDD,vps_type,vps_name))
                os.system('chmod 600 %s/%s/%s/sshkey' %(os_rootHDD,vps_type,vps_name))
                os.system('cd %s/%s/%s/sshkey && ssh-keygen -t rsa -b 4096 -f id_rsa -C hoanghd -N "" -q && cd - %s' %(os_rootHDD,vps_type,vps_name,output))
            os_path = '%s/%s/%s/os-%s.qcow2' %(os_rootHDD,vps_type,vps_name,vps_name)
            seed_path = '%s/%s/%s/seed-%s.qcow2' %(os_rootHDD,vps_type,vps_name,vps_name)
            cloudinit_path = '%s/%s/%s/cloudinit.cfg' %(os_rootHDD,vps_type,vps_name)
            network_path = '%s/%s/%s/network.cfg' %(os_rootHDD,vps_type,vps_name)
            path_info.append({'vps_name': vps_name, 'os_path': os_path, 'seed_path': seed_path, 'cloudinit_path': cloudinit_path, 'network_path': network_path, 'image_path': image_path, 'interface_name': interface_name})
        elif disk_type == 'ssd':
            path_sshkey = '%s/%s/%s/sshkey/id_rsa' %(os_rootSSD,vps_type,vps_name)
            if os.path.exists(path_sshkey) == False:
                folder_option.maker_folder('%s/%s/%s/sshkey' %(os_rootSSD,vps_type,vps_name))
                os.system('chmod 600 %s/%s/%s/sshkey' %(os_rootSSD,vps_type,vps_name))
                os.system('cd %s/%s/%s/sshkey && ssh-keygen -t rsa -b 4096 -f id_rsa -C hoanghd -N "" -q && cd - %s' %(os_rootSSD,vps_type,vps_name,output))
            os_path = '%s/%s/%s/os-%s.qcow2' %(os_rootSSD,vps_type,vps_name,vps_name)
            seed_path = '%s/%s/%s/seed-%s.qcow2' %(os_rootSSD,vps_type,vps_name,vps_name)
            cloudinit_path = '%s/%s/%s/cloudinit.cfg' %(os_rootSSD,vps_type,vps_name)
            network_path = '%s/%s/%s/network.cfg' %(os_rootSSD,vps_type,vps_name)
            path_info.append({'vps_name': vps_name, 'os_path': os_path, 'seed_path': seed_path, 'cloudinit_path': cloudinit_path, 'network_path': network_path, 'image_path': image_path, 'interface_name': interface_name})
        elif disk_type == 'nvme':
            path_sshkey = '%s/%s/%s/sshkey/id_rsa' %(os_rootSSD,vps_type,vps_name)
            if os.path.exists(path_sshkey) == False:
                folder_option.maker_folder('%s/%s/%s/sshkey' %(os_rootNVME,vps_type,vps_name))
                os.system('chmod 600 %s/%s/%s/sshkey' %(os_rootNVME,vps_type,vps_name))
                os.system('cd %s/%s/%s/sshkey && ssh-keygen -t rsa -b 4096 -f id_rsa -C hoanghd -N "" -q && cd - %s' %(os_rootNVME,vps_type,vps_name,output))
            os_path = '%s/%s/%s/os-%s.qcow2' %(os_rootNVME,vps_type,vps_name,vps_name)
            seed_path = '%s/%s/%s/seed-%s.qcow2' %(os_rootNVME,vps_type,vps_name,vps_name)
            cloudinit_path = '%s/%s/%s/cloudinit.cfg' %(os_rootNVME,vps_type,vps_name)
            network_path = '%s/%s/%s/network.cfg' %(os_rootNVME,vps_type,vps_name)
            path_info.append({'vps_name': vps_name, 'os_path': os_path, 'seed_path': seed_path, 'cloudinit_path': cloudinit_path, 'network_path': network_path, 'image_path': image_path, 'interface_name': interface_name})
        return path_info

    def vps_diskType():
        listdiskType = [{'ssd': 'Solid State Drive'}, {'hdd': 'Hard Disk Drive'}, {'nvme': 'Non-Volatile Memory Express'}]
        loops.listMenu(listdiskType)
        vps_diskType = loops.choiseMenu(listdiskType)
        print('\n','-'*30,' In progress of creating a virtual KVM machine automatically ','-'*30)
        if vps_diskType == 'ssd':
            return vps_diskType
        elif vps_diskType == 'hdd':
            return vps_diskType
        elif vps_diskType == 'nvme':
            return vps_diskType

    def vps_Run(vps_type,vps_name,memory,cpu,seed_path,os_path,network):
        if vps_type == 'ubuntu18.04':
            variant = kvm.vars()[4][vps_type]['bionic']['variant']
            type_os = kvm.vars()[4][vps_type]['bionic']['type_os']
        else:
            variant = kvm.vars()[4][vps_type]['variant']
            type_os = kvm.vars()[4][vps_type]['type_os']

        os.system('sudo virt-install --name %s \
            --virt-type kvm --memory %s --vcpus %s \
            --boot hd,menu=on \
            --disk path=%s,device=cdrom \
            --disk path=%s,device=disk \
            --graphics vnc \
            --os-type %s --os-variant %s \
            --network network:%s \
            --console pty,target_type=serial \
            --noautoconsole %s' %(vps_name,memory,cpu,seed_path,os_path,type_os,variant,network,output))
        print('- Successfully created VPS %s' %(vps_name))

    def vps_Deploy(subnet):
        list_vps = []
        list_vars = kvm.vars()[3]
        define_Vps = kvm.define_Vps()
        define_Vps.pop()
        for network,value in list_vars.items():
            split_subnet = value['subnet'].split('.')
            split_subnet.pop()
            subnet_in_vars = '.'.join(split_subnet)
            if subnet == subnet_in_vars:
                gateway = value['gateway']
                prefix = value['prefix']
                vps_type = kvm.vps_choiseOS()
                disk_type = kvm.vps_diskType()
                username = kvm.vars()[1]['username']
                passwd = kvm.vars()[1]['passwd']
                kvm.convert_kubernetes_vars()
                for vps_name in define_Vps:
                    cpu = vps_name['cpu']
                    memory = int(vps_name['memory'])*1024
                    ipaddr = vps_name['ipaddr']
                    disk_size = vps_name['diskSize']
                    vps_name = vps_name['vps_name']
                    hostname = '%s.com' %(vps_name)
                    path_info = kvm.define_path(vps_name,vps_type,disk_type)
                    cloudinit_path_default = kvm.define_cloudinit(vps_type)[0]
                    network_path_default = kvm.define_cloudinit(vps_type)[1]
                    for i in path_info:
                        if i['vps_name'] == vps_name:
                            seed_path = path_info[0]['seed_path']
                            os_path = path_info[0]['os_path']
                            image_path = path_info[0]['image_path']
                            interface_name = path_info[0]['interface_name']
                            cloudinit_path = path_info[0]['cloudinit_path']
                            network_path = path_info[0]['network_path']
                            kvm.config_cloudinit(cloudinit_path_default,network_path_default,cloudinit_path,network_path,hostname,interface_name,ipaddr,prefix,gateway,username,passwd)
                            kvm.create_diskOS(image_path,os_path,disk_size)
                            kvm.create_diskSeed(network_path,cloudinit_path,seed_path)
                            kvm.vps_Run(vps_type,vps_name,memory,cpu,seed_path,os_path,network)
                            list_vps.append('{\'%s\': \'%s\'}' %(vps_name,ipaddr))
            return list_vps, vps_type

    def vps_Destroy():
        values = subprocess.check_output("virsh list --all | awk 'FNR>='3'{print;}' | head -n -1 | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        values.remove(vps_name)
        vps_path = '/%s' %(subprocess.check_output("""virsh domblklist %s | grep -v 'Target' | grep 'seed\|snapshot\|os' | awk '{print $2}' | cut -d'/' -f2,3,4,5 | head -1""" %(vps_name), shell=True).decode("utf-8").strip('\n'))
        try:
            vps_Status = subprocess.check_output("""virsh list --all | grep -w %s | grep -c 'running'""" %(vps_name), shell=True).decode("utf-8").strip('\n')
        except:
            vps_Status = 0
        if int(vps_Status) == 1:
            os.system('virsh destroy %s' %(vps_name))
        os.system('virsh undefine %s' %(vps_name))
        os.system('''rm -rf %s''' %(vps_path))
        print('- Removing %s successful\n' %(vps_name))
        kvm.vps_Destroy()

    def vps_HA_Destroy():
        values = subprocess.check_output("pcs resource status | grep 'Resource Group' | cut -d':' -f2 | sed 's: ::g'", shell=True).decode("utf-8").strip('\n').split('\n')
        if values != ['']:
            loops.listmenu_noDict(values)
            haGroup = loops.choiseMenu_noDict(values)
            vps_name = haGroup.split('haGroup-')[1]
            vps_path = '/%s' %(subprocess.check_output("""virsh domblklist %s | grep -v 'Target' | grep 'seed\|snapshot\|os' | awk '{print $2}' | cut -d'/' -f2,3,4,5 | head -1""" %(vps_name), shell=True).decode("utf-8").strip('\n'))
            os.system('pcs resource delete %s --force' %(haGroup))
            os.system("""lsof +D %s | awk '{print $2}' | tail -n +2 | xargs -r kill -9""" %(vps_path))
            os.system("""rm -rf %s""" %(vps_path))
            print("- Removing %s successful\n" %(haGroup))
        else:
            print('\nNo haGroup exists to delete\n')

    def vps_List():
        os.system('clear')
        print('Total Vps\n')
        os.system("virsh list --all")

    def vps_ssh():
        values = subprocess.check_output("virsh list --all | grep 'running' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        vps_path = '/%s/sshkey/sshkey.info' %(subprocess.check_output("""virsh domblklist %s | grep -v 'Target' | grep 'seed\|snapshot\|os' | awk '{print $2}' | cut -d'/' -f2,3,4,5 | head -1""" %(vps_name), shell=True).decode("utf-8").strip('\n'))
        read_sshkey = file_option.file_read(vps_path)
        print('\n%s\n' %(read_sshkey))
        os.system(read_sshkey)

    def vps_Console():
        values = subprocess.check_output("virsh list --all | grep 'running' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        os.system('virsh console %s' %(vps_name))

    def vps_Start():
        values = subprocess.check_output("virsh list --all | grep 'shut off' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        os.system('virsh start %s' %(vps_name))

    def vps_Shutdown():
        values = subprocess.check_output("virsh list --all | grep 'running' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        os.system('virsh shutdown %s' %(vps_name))

    def vps_Reboot():
        values = subprocess.check_output("virsh list --all | grep 'running' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        os.system('virsh reboot %s' %(vps_name))

    def attach_Disk():
        values = subprocess.check_output("virsh list --all | grep 'running' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(values)
        vps_name = loops.choiseMenu_noDict(values)
        disk_size = int(input("\nDisk size attach: "))
        print("Don't choose these target names, because they already exist\n")
        os.system("""virsh domblklist %s | awk 'NF==2'' {print $1,$2}' | grep -v 'Target'""" %(vps_name))
        target = input("Disk target name (example: vda, vdb,vdc,...): ")
        try:
            subprocess.check_output('''virsh domblklist %s | awk 'NF==2'' {print $1,$2}' | grep -v 'Target' | grep -Eo "%s"''' %(vps_name,target))
            print("Target name already exists")
        except:
            disk_name = '''attach-disk-%s-%sG.qcow2''' %(target,disk_size)
            disk_path = subprocess.check_output("""virsh domblklist %s | grep -v 'Target' | grep 'seed\|snapshot\|os' | awk '{print $2}' | cut -d'/' -f2,3,4,5 | head -1""" %(vps_name), shell=True).decode("utf-8").strip('\n')
            disk_path = '%s%s/%s' %('/',disk_path,disk_name)
            os.system('''qemu-img create -f raw %s %sG''' %(disk_path,disk_size))
            os.system('''virsh attach-disk %s %s %s --cache none''' %(vps_name,disk_path,target))

    def deattach_Disk():
        list_Vps = subprocess.check_output("virsh list --all | grep 'running' | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(list_Vps)
        vps_name = loops.choiseMenu_noDict(list_Vps)
        list_disk_deattach = subprocess.check_output("""virsh domblklist %s | grep -v 'Target' | grep 'attach-disk' | awk 'NF==2'' {print $2}'""" %(vps_name), shell=True).decode("utf-8").strip('\n').split('\n')
        if list_disk_deattach != ['']:
            loops.listmenu_noDict(list_disk_deattach)
            disk_deattach = '%s' %(loops.choiseMenu_noDict(list_disk_deattach))
            os.system('''virsh detach-disk --domain %s %s && rm -rf %s''' %(vps_name,disk_deattach,disk_deattach))
        else:
            print('\n- There is no extra disk in the server %s.\n' %(vps_name))

    def create_Snapshot():
        list_Vps = subprocess.check_output("virsh list --all | awk 'FNR>='3'{print;}' | head -n -1 | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(list_Vps)
        vps_name = loops.choiseMenu_noDict(list_Vps)
        snapshot_name = input("\n- Snapshot name: ")
        snapshot_description = input("- Snapshot description: ")
        try:
            vps_Status = subprocess.check_output("""virsh list --all | grep -w %s | grep -c 'running'""" %(vps_name), shell=True).decode("utf-8").strip('\n')
        except:
            vps_Status = 0
        if int(vps_Status) == 1:
            os.system('virsh shutdown %s' %(vps_name))
        os.system('virsh snapshot-create-as --domain %s --name "%s" --description "%s" && sleep 5' %(vps_name,snapshot_name,snapshot_description))
        os.system('virsh start %s' %(vps_name))
        os.system('virsh snapshot-list --domain %s' %(vps_name))

    def restore_Snapshot():
        list_Vps = subprocess.check_output("virsh list --all | awk 'FNR>='3'{print;}' | head -n -1 | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(list_Vps)
        vps_name = loops.choiseMenu_noDict(list_Vps)
        list_Snapshot = subprocess.check_output("virsh snapshot-list --domain %s| awk 'NR>2'' {print $1}'" %(vps_name), shell=True).decode("utf-8").strip('\n').split('\n')
        if list_Snapshot != ['']:
            loops.listmenu_noDict(list_Snapshot)
            snapshot_Name = loops.choiseMenu_noDict(list_Snapshot)
            try:
                vps_Status = subprocess.check_output("""virsh list --all | grep -w %s | grep -c 'running'""" %(vps_name), shell=True).decode("utf-8").strip('\n')
            except:
                vps_Status = 0
            if int(vps_Status) == 1:
                os.system('virsh shutdown %s' %(vps_name))
            os.system('sleep 2 && virsh snapshot-revert --domain %s --snapshotname %s --running' %(vps_name,snapshot_Name))
            os.system('sleep 2 && virsh start %s' %(vps_name))
        else:
            print('\n- There is no snapshot in the server %s.\n' %(vps_name))
            
    def delete_Snapshot():
        list_Vps = subprocess.check_output("virsh list --all | awk 'FNR>='3'{print;}' | head -n -1 | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(list_Vps)
        vps_name = loops.choiseMenu_noDict(list_Vps)
        list_Snapshot = subprocess.check_output("virsh snapshot-list --domain %s| awk 'NR>2'' {print $1}'" %(vps_name), shell=True).decode("utf-8").strip('\n').split('\n')
        if list_Snapshot != ['']:
            loops.listmenu_noDict(list_Snapshot)
            snapshot_Name = loops.choiseMenu_noDict(list_Snapshot)
            os.system('virsh snapshot-delete --domain %s --snapshotname %s' %(vps_name,snapshot_Name,))
            os.system('virsh snapshot-list --domain %s' %(vps_name))
        else:
            print('\n- There is no snapshot in the server %s.\n' %(vps_name))

    def vps_ha_Enable():
        list_Vps = subprocess.check_output("virsh list --all | awk 'FNR>='3'{print;}' | head -n -1 | awk '{print $2}'", shell=True).decode("utf-8").strip('\n').split('\n')
        loops.listmenu_noDict(list_Vps)
        vps_name = loops.choiseMenu_noDict(list_Vps)
        vps_path = '/%s' %(subprocess.check_output("""virsh domblklist %s | grep -v 'Target' | grep 'seed\|snapshot\|os' | awk '{print $2}' | cut -d'/' -f2,3,4,5 | head -1""" %(vps_name), shell=True).decode("utf-8").strip('\n'))
        os.system('cp /etc/libvirt/qemu/%s.xml %s/%s.xml' %(vps_name,vps_path,vps_name))
        try:
            vps_Status = subprocess.check_output("""virsh list --all | grep -w %s | grep -c 'running'""" %(vps_name), shell=True).decode("utf-8").strip('\n')
        except:
            vps_Status = 0

        if int(vps_Status) == 1:
            os.system('virsh shutdown %s' %(vps_name))

        os.system('virsh undefine %s' %(vps_name))
        os.system('cp %s/%s.xml %s/%s.xml.bak' %(vps_path,vps_name,vps_path,vps_name))
        os.system('''sudo sed -i "s|cpu mode='host-model' check='partial'|cpu mode='host-passthrough' check='none'|" %s/%s.xml''' %(vps_path,vps_name))
        os.system('''sudo sed -i "s|driver name='qemu' type='qcow2'|driver name='qemu' type='qcow2' cache='none'|" %s/%s.xml''' %(vps_path,vps_name))
        os.system('''pcs resource create %s VirtualDomain \
            hypervisor="qemu:///system" \
            config="%s/%s.xml" \
            migration_transport=ssh \
            op start timeout="120s" \
            op stop timeout="120s" \
            op monitor  timeout="30" interval="10"  \
            meta allow-migrate="true" priority="100" \
            op migrate_from interval="0" timeout="120s" \
            op migrate_to interval="0" timeout="120" \
            --group haGroup-%s''' %(vps_name,vps_path,vps_name,vps_name))

    def vps_Action():
        os.system('clear')
        print('\nPlease select an active you want to use\n')
        listMenu = [{'vps_ssh': 'VPS ssh'}, {'vps_Console': 'VPS console'}, {'vps_Start': 'VPS start'}, {'vps_Reboot': 'VPS reboot'}, {'vps_Shutdown': 'VPS shutdown'}, {'vps_ha_Enable': 'VPS HA Enable'}, {'attach_Disk': 'VPS Attach disk'}, {'deattach_Disk': 'VPS Deattach disk'}, {'create_Snapshot': 'VPS Create snapshot'}, {'restore_Snapshot': 'VPS Restore snapshot'}, {'delete_Snapshot': 'VPS Delete snapshot'}, {'runMenu': 'Back menu'}]
        loops.listMenu(listMenu)
        action = loops.choiseMenu(listMenu)
        if action == 'vps_ssh':
            kvm.vps_ssh()
        elif action == 'vps_Console':
            kvm.vps_Console()
        elif action == 'vps_Start':
            kvm.vps_Start()
        elif action == 'vps_Shutdown':
            kvm.vps_Shutdown()
        elif action == 'vps_Reboot':
            kvm.vps_Reboot()
        elif action == 'attach_Disk':
            kvm.attach_Disk()
        elif action == 'deattach_Disk':
            kvm.deattach_Disk()
        elif action == 'create_Snapshot':
            kvm.create_Snapshot()
        elif action == 'restore_Snapshot':
            kvm.restore_Snapshot()
        elif action == 'delete_Snapshot':
            kvm.delete_Snapshot()
        elif action == 'vps_ha_Enable':
            kvm.vps_ha_Enable()

    def main_Menu():
        print('\nPlease select an active you want to use\n')
        listMenu = [{'vps_Deploy': 'VPS deploy'}, {'vps_Listvm': 'VPS list'}, {'vps_Actions': 'VPS actions'}, {'vps_Destroy': 'VPS destroy'}, {'vps_HA_Destroy': 'VPS HA destroy'}]
        loops.listMenu(listMenu)
        action = loops.choiseMenu(listMenu)

        if action == 'vps_Deploy':
            vps_check_icmp = []
            detailt_vps_check_icmp = []
            split_ipaddr = kvm.vars()[0]['startIP'].split('.')
            split_ipaddr.pop()
            subnet = '.'.join(split_ipaddr)
            define_vps_Deploy = kvm.vps_Deploy(subnet)
            list_vps = define_vps_Deploy[0]
            vps_type = define_vps_Deploy[1]
            count_vps = len(list_vps)
            print('\n','-'*30,' Kubernetes cluster will deploy in about 30 second ','-'*30)
            time.sleep(30)

            for i in list_vps:
                finally_list_vars = json.loads(i.replace("'",'"'))
                ipaddr = list(finally_list_vars.values())[0]
                hostname = list(finally_list_vars.keys())[0]
                icmp = script_check.icmp(ipaddr) 
                vps_check_icmp.append(icmp)
                if icmp == 0:
                    detailt_vps_check_icmp.append({hostname: ipaddr})

            if sum(vps_check_icmp) == count_vps:
                if vps_type == 'kubernetes-packer-image-ubuntu1804':
                    print('''- Kubernetes, often abbreviated as “K8s”, orchestrates containerized applications to run on a cluster of hosts.\n- The K8s system automates the deployment and management of cloud native applications using on-premises infrastructure or public cloud platforms.\n- It distributes application workloads across a Kubernetes cluster and automates dynamic container networking needs.\n- Kubernetes also allocates storage and persistent volumes to running containers, provides automatic scaling, and works continuously to maintain the desired state of applications, providing resiliency.\n''')
                    deploys.prepareEnv()
                    deploys.sshConfig()
                    deploys.remotePkgsInstall()
                    deploys.hostnameConfig()
                    deploys.firewallConfig()
                    deploys.keepaliveConfig()
                    deploys.haproxyConfig()
                    deploys.clusterCreate()
                    deploys.loadbalancerConfig()
                    deploys.joinMaster()
                    deploys.joinWorker()
                    deploys.calicoNetwork()
                    deploys.helmInstall()
                    deploys.metricServer()
                    deploys.ingressNginx()
                    deploys.metallb()
                    deploys.argocd()
                    deploys.dashboard()
            else:
                for x in detailt_vps_check_icmp:
                    for hostname,ipaddr in x.items():
                        print('- Server %s (%s) is not ready' %(hostname,ipaddr))

            file_option.file_remove('dict_Node.json')

        elif action == 'vps_Destroy':
            kvm.vps_Destroy()
        elif action == 'vps_HA_Destroy':
            kvm.vps_HA_Destroy()
        elif action == 'vps_Listvm':
            kvm.vps_List()
        elif action == 'vps_Actions':
            kvm.vps_Action()

kvm.main_Menu()