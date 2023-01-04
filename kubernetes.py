#!/usr/bin/python3
from common.envs import *
from common.module import *

os.system('clear')

class deploys:
    def vars():
        dict_Node = file_json.json_read('dict_Node.json')

        # dict_Node = {
        #     'masterNode': [{'k8s-master1': '192.168.13.218'}, {'k8s-master2': '192.168.13.219'}],
        #     'workerNode': [{'k8s-worker1': '192.168.13.220'}, {'k8s-worker2': '192.168.13.221'}, {'k8s-worker3': '192.168.13.222'}],
        #     'loadbalancerNode': [{'k8s-loadbalancer1': '192.168.13.223'}, {'k8s-loadbalancer2': '192.168.13.224'}]
        # }

        dict_tAuthen = {
            'username': 'root',
            'password': 'hoanghd'
        }

        dict_rootDir = {
            'src_rootDir': '/kubernetes',
            'dst_rootDir': '/kubernetes'
        }

        dict_Network = {
            'pod_network_cidr': '10.244.0.0/16',
            'vitualIP': '172.16.1.100',
            'nicPhysical': 'enp1s0',
            'sshPort': 22
        }

        return dict_Node, dict_tAuthen, dict_rootDir, dict_Network

    def prepareEnv():
        print('\n','-'*30,' Local update system and install packages ','-'*30)
        packagesInstall.updateSystem()
        packagesInstall.installPkgs({'apt': ['sshpass','tree'],'apt-get': ['cloud-image-utils']})
        packagesInstall.pythonModules(['jsonpath-ng==1.5.3', 'paramiko==2.12.0', 'requests==2.22.0'])

    def remotePkgsInstall():
        print('\n','-'*30,' Remote update system and install packages ','-'*30)
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        
        packages = {
            'apt': ['sshpass','tree'],
        }

        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                for package in packages['apt']:
                    print('- Install %s on server %s (%s)' %(package,hostName,sshIpaddr))
                    commands = 'command -v %s >/dev/null 2>&1 || (sudo apt-get install %s -y %s)' %(package,package,output)
                    remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,commands)

    def defineVars():
        listDict = list(deploys.vars()[0].items())
        listDict.pop()
        for nodeType,listNode in listDict:
            if 'masterNode' in nodeType:
                masterHostname = list(listNode[0].keys())[0]
                masterIpaddr = list(listNode[0].values())[0]
        return masterHostname, masterIpaddr

    def sshConfig():
        print('\n','-'*30,' Config sshkey ','-'*30)
        src_rootDir = deploys.vars()[2]['src_rootDir']
        dst_rootDir = deploys.vars()[2]['dst_rootDir']
        os.system('echo '' > ~/.ssh/known_hosts')
        id_rsa = '''-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAxwldSynNWYEj36iWSNvsLU821sIW5cpzOWySWlaR8KrREFjN\nfCYQJWFRfzk+s+wrKSYGifvYxFvGEEsUMA80WEZEKQ1xY6s/lAoD1+Y5cJ5cbohN\nRYYno1rEUDLqz2qeARUSDyKVRw3LVtU6/01NYcGJECwavNUkzP216OUP8HmYKZXF\nWWLT9C6M1ftkUYaeI8RSn+cQr0UPDkJ92ERtRvsqQTpewNHSHpC7sS8lLDPR2nhX\nddUV1Fk8kII6gQAyH3nZ0329IUU7JwoW9RTwiD6aPkmtFQWlJSP56oHLlxr+wkk2\npOoxZ5fzxpi7icbej4g9FNDBQ2KLeQWdGhNqpQIBIwKCAQEAu6m+XM+kW7RGZSns\nyFpTtbEWcrb/pXW9GOK14CW8zPjTvvSkfF5m/qw25asAmwM+oyPaR5WvH4m6vuez\n8syBz5K1S0cwZUmw+UtFc8pwrAMGsVvxFapf4ymxx/V+TokYoe9LipzzJbyMhRIw\nT8yKyeJcqNkghigMwUb7+Nf5Fe1S+Zu+X3opHYX6tE7rN1cH+9Kams6TAzYoviqh\nzTnYTCmtRpQxR+pa+6CWWijrhUxzUJUpy7k2/iAsrykaUoWMBy9cmlD0CdXQJnEU\nQnKQ/dn0M4GOwShks+D/kc7gbNrnGeuLukDyKbNAeddc/EbCSAFUqgIcSRWjdpJ9\nQFnRCwKBgQDtd9jSb89CKy3qROKzawL081Sk339okyT715E3vchyHqxcqzoaf+I3\nRBiIyLB8fB8gPAzLwwvasVxKI25vVGLlcx35205fb1d/0HWMv5LQc/Rs13n3oz5b\nzICRgjuopLYIcN6h3PIk8sGjTmixcv6LABa+Xfgz5TTB+3WazcYZIQKBgQDWkbqs\n4WdWqbCYqxKQpBAVFdYhDLNZw2LBNrKafuGKHVjnQ2MXvlvlBeUm1nJKC25G1JcK\nCULaBfIYXfe3A6MNffNW92zmgLWggyRdcumV0MAa4puh6rt5sSFhGzRrOR+zoogI\nV8KuhquXuObGf5SNQxL+IZB+4h6YPd1ebOZNBQKBgFgz1DDns2G4REESRZMZHlr7\nS1MucSbXkWTbCg1jv3rYMWQ/mT0K7Z9/sVdgfBD65v1YIgKKRjtJMOhWTZcQtwTE\nW5dRdOGeYlQLmWAp5hLpPYeDO+5D8pcgEn8wX01EfiBkb/L6S0+NXd2SJuLS8NSL\nASIi5yk34GVOxUggi2hrAoGAdHr+8CKXLwupAmt/G1G/lmrwlZkuKWoRCc08Yn9k\nfi0wQwdTDOOuOn+LBnRp7a5vEIII2Y//uC8dBenePsd1xX7jLzXcCBn8MpBVkdCq\nsGoB4rWHr6tP1FjXmx1lmUrlUuMz50WVkfFV1gVKE/wdcUGrOX/vWtKFoxpE+L7G\nKc8CgYEAsUB2iJ4m/i8GWMy/sgw1GzbWFahFGRTqxXv2FMlBP/8T2w9D7+yKHGy5\nBkvPI0JR00Nb3HkYNnuADr1QDNkX33jbTnWzi4J9RGFsmHvbcwcsrl1DZvThZpmM\na6MV5Isezjp7oc9a9dJkY+4GUEgZbLqlE/7I5y+HMiG1cdJi434=\n-----END RSA PRIVATE KEY-----\n\n-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAuY2ERXpfftdqv8UkgX+PWNmJGetjBc83C69Q/ULJ2fcOYyvu\nXtN7EAPaTysCZwp27hAxh9SdMWY0N3GdN0EKyyfd5RUpUdrwHFeZl0LbWkc2iihf\nEeppT128KEB8rAR/9N1u9rAWdlji1s5mDOCCIKGP8CUKHV5jU8Peo5J/F/vHB6Hc\neeZtSvNrVgYRnTHNzpIkvfKsiUeJ7GEavt5QG3f2lD/L+zeIUj+844a4E2jtozqZ\n2wyY12LivFsk/znp0LW8z7HSXKJjxGwzd77XfB5nvRmdH6ktka5oaUs8nUoWxgPs\nrVuYfNsK1wCkFiGookusy4obC3eJwBYyDWG8QQIDAQABAoIBAEH4q8+cC7noUz7t\nk+Yq+UdoyJMbmrBlFTglVBFHnsbNTSM7alvyqu1twT+mlgsWsGRCA6o8kMsQgH45\n+eC8Ul8axIz/chp1Uitxhd0+2wiFC0IhynNvOZQLSquxCeKLEwd3d01kHAhl3/jp\nl2T6qal6Z9fFA4yfk4cju9PCcUeQFQjIE0kN4zpeIwOU7nc4ZDHKPvCjtEMDgbix\nXVYyAMivp9G/hi/ltgjN67xplv1RPWiFcLxScyepy/UQGnq0On5EfWe2MrEs9uRB\n7ug5iY3zryBhrFQDdy/t4oB+BaeVkPu37pv2WK8mDNjpS43q3B9ob54TqRSwHF4M\n8gwe/CUCgYEA4W57jh84j1sskVv6L/3opCGGVM1AFfqs9MVBSg54iIwxoMXcjERC\nRARFYiS3TEKn4lPpILp+DBFdvG3n1FNxDufihfBQvVfIx+JAJT7/28/4URlDUmTm\nNzjtfVDkGtRWbVI0jT8mkTF8q1PjxxgTuuVP75uCTtrIVQ34AmCp/KsCgYEA0raz\n2Ky8kGEIvsbh1buk14QKA2+Y7KP8hUORWdccXe/5dL18h6aRLd07wIh0p+94YagU\nwhH26vjKO32BcCDAb+p+xkd1zGo/56fvC3v37elrMZFLNw5ObLZp/LmJ0LJh/qD3\nU9+qsw3mt64zaep17Ymah2FeU6baz67GR+vm0sMCgYEAzhU6ToqsIiGvdJMo/Iaa\nDrG3I/8e/vjS9FD/hrwD5JCFLfyzymb8TUG6TCZUixrEb1tWW90hLdcSYhf3P1uo\nl3/Uza0LooyFuHVVPreBH2nYEAuQR9qFuyYHtfAlF4HWIMpt0FJS55jd56IhMPkJ\n0Gmh0eHQFlZbnaXPfBzySVECgYBdvR+m/blpNXGxhUKEVdTQd5II00WhyJYXJubr\no7Gf7Jj6IS3cHvKpB6mETnAvIW5Za2/IojtJbuJwsrW5jyhs4VICnVm/VWkWgnPq\nlPzH3zZrt6pRVND4tfHSlyvDJwhHQY6lxnPm8gE4p4uBy+cohDW1klBnQGxJRgQ5\njK2EBwKBgHZnF7PgM8V7ax1csPvkGvZ3QvmVPxgho9Wd8dD2M8+Qz7bh7wcbDA/L\n2zGORXArJb+S9qykU+xDsOxkzTmJ29m2ijNMdB6yruueLbjpNI7hDEVs2EyIVzJc\n1pXIGd1UWFG+MgmU/e1wkJGlNXN25aiJPPjnXGb+46+YuOp1nqrs\n-----END RSA PRIVATE KEY-----'''
        authorized_keys = '''ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAxwldSynNWYEj36iWSNvsLU821sIW5cpzOWySWlaR8KrREFjNfCYQJWFRfzk+s+wrKSYGifvYxFvGEEsUMA80WEZEKQ1xY6s/lAoD1+Y5cJ5cbohNRYYno1rEUDLqz2qeARUSDyKVRw3LVtU6/01NYcGJECwavNUkzP216OUP8HmYKZXFWWLT9C6M1ftkUYaeI8RSn+cQr0UPDkJ92ERtRvsqQTpewNHSHpC7sS8lLDPR2nhXddUV1Fk8kII6gQAyH3nZ0329IUU7JwoW9RTwiD6aPkmtFQWlJSP56oHLlxr+wkk2pOoxZ5fzxpi7icbej4g9FNDBQ2KLeQWdGhNqpQ==\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC5jYRFel9+12q/xSSBf49Y2YkZ62MFzzcLr1D9QsnZ9w5jK+5e03sQA9pPKwJnCnbuEDGH1J0xZjQ3cZ03QQrLJ93lFSlR2vAcV5mXQttaRzaKKF8R6mlPXbwoQHysBH/03W72sBZ2WOLWzmYM4IIgoY/wJQodXmNTw96jkn8X+8cHodx55m1K82tWBhGdMc3OkiS98qyJR4nsYRq+3lAbd/aUP8v7N4hSP7zjhrgTaO2jOpnbDJjXYuK8WyT/OenQtbzPsdJcomPEbDN3vtd8Hme9GZ0fqS2RrmhpSzydShbGA+ytW5h82wrXAKQWIaiiS6zLihsLd4nAFjINYbxB'''
        folder_option.maker_folder(src_rootDir)
        file_option.file_write('%s/id_rsa' %(src_rootDir),id_rsa)
        file_option.file_write('%s/authorized_keys' %(src_rootDir),authorized_keys)
        os.system('chmod 600 %s/id_rsa' %(src_rootDir))
        os.system('chmod 600 %s/authorized_keys' %(src_rootDir))
        sourceIdrsa = '%s/id_rsa' %(src_rootDir)
        sourceAuthorizedkeys = '%s/authorized_keys' %(src_rootDir)
        sshUser = deploys.vars()[1]['username']
        sshPasswd= deploys.vars()[1]['password']
        sshPort = deploys.vars()[3]['sshPort']
        
        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                commands = 'sudo rm -rf ~/.ssh/* && sudo mkdir -p ~/.ssh'
                print('- Config sshkey on server %s (%s)' %(hostName,sshIpaddr))
                remoteAction.sshpassRemote(sshPasswd,sshPort,sshUser,sshIpaddr,commands)
                remoteAction.scp_sshpassRemote(sshPasswd,sshPort,sourceIdrsa,sshUser,sshIpaddr,'~/.ssh/id_rsa')
                remoteAction.scp_sshpassRemote(sshPasswd,sshPort,sourceAuthorizedkeys,sshUser,sshIpaddr,'~/.ssh/authorized_keys')
                remoteAction.sshpassRemote(sshPasswd,sshPort,sshUser,sshIpaddr,'mkdir -p %s' %(dst_rootDir))

    def hostnameConfig():
        print('\n','-'*30,' Config hostname ','-'*30)
        src_rootDir = deploys.vars()[2]['src_rootDir']
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']

        sourceConfig = '%s/hosts' %(src_rootDir)
        file_option.file_remove(sourceConfig)
        os.system('cp /etc/hosts %s/hosts' %(src_rootDir))
        
        count = 1
        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if count == 1:
                    lags = '\n'
                else:
                    lags = ''

                print('- Set hostname on server %s (%s)' %(hostName,sshIpaddr))
                hostFile = '%s%s %s\n' %(lags,sshIpaddr,hostName)
                file_option.val_add_to_file(sourceConfig,hostFile)
                remoteAction.scpRemote(sshPort,sourceConfig,sshUser,sshIpaddr,'/etc/hosts')
                commands = 'sudo hostnamectl set-hostname %s' %(hostName)
                remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,commands)
                count += 1

    def firewallConfig():
        print('\n','-'*30,' Firewall config ','-'*30)
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']

        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                print('- Firewall config on server %s (%s)' %(hostName,sshIpaddr))
                commands = 'sudo ufw disable && sudo systemctl stop ufw && sudo systemctl disable ufw'
                remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,commands)

    def keepaliveConfig():
        print('\n','-'*30,' Keepalive config ','-'*30)
        src_rootDir = deploys.vars()[2]['src_rootDir']
        nicPhysical = deploys.vars()[3]['nicPhysical']
        vitualIP = deploys.vars()[0]['vitualIP']
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']

        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'loadbalancer' in hostName:
                    print('- Keepalive config on server %s (%s)' %(hostName,sshIpaddr))
                    config = '''vrrp_instance VI_1 {\n        state MASTER\n        interface %s\n        virtual_router_id 101\n        priority 10\n        advert_int 1\n        authentication {\n            auth_type PASS\n            auth_pass %s\n        }\n        virtual_ipaddress {\n            %s\n        }\n    }''' %(nicPhysical,deploys.vars()[1]['password'],vitualIP)
                    sourceConfig = '%s/keepalived-%s.conf' %(src_rootDir,hostName)
                    file_option.file_write(sourceConfig,config)
                    remoteAction.scpRemote(sshPort,sourceConfig,sshUser,sshIpaddr,'/etc/keepalived/keepalived.conf')
                    commands = 'sudo systemctl restart keepalived && sudo systemctl status keepalived && sudo systemctl enable keepalived && sudo ip addr show %s' %(nicPhysical)
                    remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,commands)

    def haproxyConfig():
        print('\n','-'*30,' Haproxy config ','-'*30)
        src_rootDir = deploys.vars()[2]['src_rootDir']
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']

        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                sourceConfig = '%s/haproxy.cfg' %(src_rootDir)
                if 'loadbalancer' in hostName:
                    configAPI = '''frontend stats\n    bind *:8080\n    mode http\n    stats enable\n    stats uri /stats\n    stats refresh 10s\n    stats admin if LOCALHOST\n\nfrontend fe-apiserver\n    bind 0.0.0.0:6443\n    mode tcp\n    option tcplog\n    default_backend be-apiserver\n\nbackend be-apiserver\n    mode tcp\n    option tcplog\n    option tcp-check\n    balance roundrobin\n    default-server inter 10s downinter 5s rise 2 fall 2 slowstart 60s maxconn 250 maxqueue 256 weight 100\n'''
                    file_option.file_write(sourceConfig,configAPI)

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'master' in hostName:
                    masterAPI = '    server %s %s:6443 check\n' %(hostName,sshIpaddr)
                    file_option.val_add_to_file(sourceConfig,masterAPI)

        workerHTTP = '''\nfrontend http_frontend\n    bind *:80\n    mode tcp\n    option tcplog\n    default_backend http_backend\n\nbackend http_backend\n    mode tcp\n    balance roundrobin\n'''
        file_option.val_add_to_file(sourceConfig,workerHTTP)

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'worker' in hostName:
                    workerHTTP = '    server %s %s:30100 check\n' %(hostName,sshIpaddr)
                    file_option.val_add_to_file(sourceConfig,workerHTTP)

        workerHTTPS = '''\nfrontend https_frontend\n    bind *:443\n    mode tcp\n    option tcplog\n    default_backend https_backend\n\nbackend https_backend\n    mode tcp\n    balance roundrobin\n'''
        file_option.val_add_to_file(sourceConfig,workerHTTPS)

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'worker' in hostName:
                    workerHTTPS = '    server %s %s:30101 check\n' %(hostName,sshIpaddr)
                    file_option.val_add_to_file(sourceConfig,workerHTTPS)

        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'loadbalancer' in hostName:
                    print('- Haproxy config on server %s (%s)' %(hostName,sshIpaddr))
                    remoteAction.scpRemote(sshPort,sourceConfig,sshUser,sshIpaddr,'/etc/haproxy/haproxy.cfg')
                    commands = 'sudo systemctl enable haproxy && sudo systemctl restart haproxy && sudo systemctl status haproxy'
                    remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,commands)

    def clusterCreate():
        print('\n','-'*30,' Create kubernetes cluster ','-'*30)
        networkCidr = deploys.vars()[3]['pod_network_cidr']
        vitualIP = deploys.vars()[0]['vitualIP']
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']

        listDict = list(deploys.vars()[0].items())
        listDict.pop()

        for nodeType,listNode in listDict:
            if 'masterNode' in nodeType:
                hostName = list(listNode[0].keys())[0]
                sshIpaddr = list(listNode[0].values())[0]
                print('- Create Kubernetes cluster on server %s (%s)' %(hostName,sshIpaddr))
                commands = '''kubeadm init --control-plane-endpoint "%s:6443" --upload-certs --pod-network-cidr=%s && mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config && export KUBECONFIG=/etc/kubernetes/admin.conf''' %(vitualIP,networkCidr)
                remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,commands)

    def loadbalancerConfig():
        print('\n','-'*30,' Loadbalancer config ','-'*30)
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        masterIpaddr = deploys.defineVars()[1]
        listDict = list(deploys.vars()[0].items())
        listDict.pop()
        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'loadbalancer' in hostName:
                    print('- Loadbalancer config on server %s (%s)' %(hostName,sshIpaddr))
                    copyConfig = '''mkdir -p $HOME/.kube && scp -o StrictHostKeychecking=no root@%s:/etc/kubernetes/admin.conf $HOME/.kube/config && chown $(id -u):$(id -g) $HOME/.kube/config''' %(masterIpaddr)
                    remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,copyConfig)

    def joinMaster():
        print('\n','-'*30,' Join Master node ','-'*30,)
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        masterHostname = deploys.defineVars()[0]
        masterIpaddr = deploys.defineVars()[1]
        
        listDict = list(deploys.vars()[0].items())
        listDict.pop()
        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'master' in hostName and hostName != masterHostname:
                    print('- Kubernetes join master cluster on server %s (%s)' %(hostName,sshIpaddr))
                    joinCluster = """\$(ssh -p 22 -o StrictHostKeychecking=no root@%s 'kubeadm token create --print-join-command --certificate-key $(ssh -p 22 -o StrictHostKeychecking=no root@%s 'kubeadm init phase upload-certs --upload-certs | tail -1')') && mkdir -p $HOME/.kube\nsudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config\nsudo chown $(id -u):$(id -g) \$HOME/.kube/config\nexport KUBECONFIG=/etc/kubernetes/admin.conf""" %(masterIpaddr,masterIpaddr)
                    remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,joinCluster)

    def joinWorker():
        print('\n','-'*30,' Join Worker node ','-'*30)
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        masterIpaddr = deploys.defineVars()[1]
        listDict = list(deploys.vars()[0].items())
        listDict.pop()
        for nodeType,listNode in listDict:
            for node in listNode:
                hostName = list(node.keys())[0]
                sshIpaddr = list(node.values())[0]
                if 'worker' in hostName:
                    print('- Kubernetes join worker cluster on server %s (%s)' %(hostName,sshIpaddr))
                    joinCluster = """\$(ssh -p 22 -o StrictHostKeychecking=no root@%s 'kubeadm token create --print-join-command')""" %(masterIpaddr)
                    remoteAction.sshRemote(sshPort,sshUser,sshIpaddr,joinCluster)

    def calicoNetwork():
        print('\n','-'*30,' Deploy some additional services ','-'*30)
        print('- Install Calico network')
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        networkCidr = deploys.vars()[3]['pod_network_cidr']
        calicoConfig = """wget https://docs.projectcalico.org/v3.21/manifests/calico.yaml\nsudo sed -i 's/# - name: CALICO_IPV4POOL_CIDR/- name: CALICO_IPV4POOL_CIDR/' calico.yaml\nsudo sed -i 's|#   value: .*|  value: "%s"|g' calico.yaml\nkubectl apply -f calico.yaml""" %(networkCidr)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,calicoConfig)

    def helmInstall():
        print('- Install Helm')
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        commandInstall = 'curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 && chmod 700 get_helm.sh && ./get_helm.sh'
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandInstall)

    def metricServer():
        print('- Deploy metrics server')
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        currentDir = os.path.abspath(os.getcwd())
        sourceManifest = '%s/manifest/metrics_server.yaml' %(currentDir)
        dst_rootDir = deploys.vars()[2]['dst_rootDir']
        fileExist = os.path.exists(sourceManifest)
        if fileExist == True:
            remoteAction.scpRemote(sshPort,sourceManifest,sshUser,vitualIP,'%s/metrics_server.yaml' %(dst_rootDir))
            commandDeploy = 'kubectl apply -f %s/metrics_server.yaml' %(dst_rootDir)
            remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandDeploy)         
            commandVerify = 'kubectl top pod -A && kubectl top node'
            remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandVerify)       
        else:
            print('- %s does not exist' %(sourceManifest))

    def ingressNginx():
        print('- Deploy Ingress Nginx')
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        currentDir = os.path.abspath(os.getcwd())
        src_configMap = '%s/manifest/configMap.sh' %(currentDir)
        dst_rootDir = deploys.vars()[2]['dst_rootDir']
        dst_configmap = '%s/nginxConfigmap.yaml' %(dst_rootDir)

        commandDeploy = '''kubectl create namespace nginx-ingress && helm repo add nginx-stable https://helm.nginx.com/stable && helm install ingress nginx-stable/nginx-ingress --namespace nginx-ingress && git clone https://github.com/nginxinc/kubernetes-ingress.git && kubectl apply -f ./kubernetes-ingress/deployments/helm-chart/crds/ && sed -i 's|kind: deployment|kind: daemonset|g' ./kubernetes-ingress/deployments/helm-chart/values.yaml && helm upgrade ingress nginx-stable/nginx-ingress -f ./kubernetes-ingress/deployments/helm-chart/values.yaml -n nginx-ingress'''
        configMap = """cat > %s << OEF\nkind: ConfigMap\napiVersion: v1\nmetadata:\n  name: ingress-nginx-ingress\n  namespace: nginx-ingress\ndata:\n  use-proxy-protocol: '"true"'\n  proxy-connect-timeout: "10s"\n  proxy-read-timeout: "10s"\n  client-max-body-size: "2m"\n  external-status-address: "%s"\nOEF\n \
            kubectl -n nginx-ingress patch configmap ingress-nginx-ingress --patch-file %s""" %(dst_configmap,vitualIP,dst_configmap)
        patchNginx = """kubectl -n nginx-ingress patch svc ingress-nginx-ingress --patch '{"spec": { "type": "NodePort", "ports": [ { "port": 80, "nodePort": 30100 }, { "port": 443, "nodePort": 30101 } ] } }'"""
        commandVerify = 'kubectl get po -n nginx-ingress && kubectl get ds -n nginx-ingress'

        file_option.file_write(src_configMap,patchNginx)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandDeploy)  
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,configMap) 
        remoteAction.scpRemote(sshPort,src_configMap,sshUser,vitualIP,'%s/patchNginx.sh' %(dst_rootDir))
        file_option.file_remove(src_configMap)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,'. %s/patchNginx.sh' %(dst_rootDir))       
        commandVerify = 'kubectl top pod -A && kubectl top node'
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandVerify)   

    def metallb():
        print('- Deploy Metallb')
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        dst_rootDir = deploys.vars()[2]['dst_rootDir']
        dst_IPAddressPool = '%s/IPAddressPool.yaml' %(dst_rootDir)
        dst_L2Advertisement = '%s/L2Advertisement.yaml' %(dst_rootDir)

        commandDeploy = '''kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.4/config/manifests/metallb-native.yaml'''
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandDeploy)  

        print(' + Note: The service will be ready in a few minutes, please wait a moment\n')
        time.sleep(120)

        IPAddressPool = """cat > %s << OEF\napiVersion: metallb.io/v1beta1\nkind: IPAddressPool\nmetadata:\n  name: first-pool\n  namespace: metallb-system\nspec:\n  addresses:\n  - %s/28\nOEF\n \
            kubectl apply -f %s""" %(dst_IPAddressPool,vitualIP,dst_IPAddressPool)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,IPAddressPool)  

        L2Advertisement = """cat > %s << OEF\napiVersion: metallb.io/v1beta1\nkind: L2Advertisement\nmetadata:\n  name: example\n  namespace: metallb-system\nspec:\n  ipAddressPools:\n  - first-poo\nOEF\n \
            kubectl apply -f %s""" %(dst_L2Advertisement,dst_L2Advertisement)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,L2Advertisement) 

    def argocd():
        print('- Deploy ArgoCD')
        argocdDomain = "argocd.hoanghd.com"
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        dst_rootDir = deploys.vars()[2]['dst_rootDir']
        currentDir = os.path.abspath(os.getcwd())
        src_argocd_values = '%s/manifest/argocd_values.yaml' %(currentDir)
        src_argocd_ingress = '%s/manifest/argocd_ingress.yaml' %(currentDir)
        dst_argocd_values = '%s/argocd_values.yaml' %(dst_rootDir)
        dst_argocd_ingress = '%s/argocd_ingress.yaml' %(dst_rootDir)

        remoteAction.scpRemote(sshPort,src_argocd_values,sshUser,vitualIP,dst_argocd_values)
        remoteAction.scpRemote(sshPort,src_argocd_ingress,sshUser,vitualIP,dst_argocd_ingress)

        commandDeploy = '''kubectl create ns argocd && sed -i 's|    host:.*|    host: %s|g' %s && kubectl apply -f %s -n argocd && kubectl apply -f %s -n argocd''' %(argocdDomain,dst_argocd_ingress,dst_argocd_values,dst_argocd_ingress)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandDeploy)

        print(' + Default username is "admin" and use command "kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath=\'{.data.password}\' | base64 -d" to get password default\n')
        print('- The ArgoCD webinterface: http://%s' %(argocdDomain))
    
    def dashboard():
        print('- Deploy Kubernetes dashboard')
        sshUser = deploys.vars()[1]['username']
        sshPort = deploys.vars()[3]['sshPort']
        vitualIP = deploys.vars()[0]['vitualIP']
        dst_rootDir = deploys.vars()[2]['dst_rootDir']
        dst_kubernetesDir = '%s/dashboard_certs/' %(dst_rootDir)
        dashboardDomain = "dashboard.hoanghd.com"
        certsDir = 'mkdir -p %s' %(dst_kubernetesDir)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,certsDir)

        currentDir = os.path.abspath(os.getcwd())
        src_Dashboard = '%s/manifest/dashboard.yaml' %(currentDir)
        dst_Dashboard = '%s/dashboard.yaml' %(dst_rootDir)
        remoteAction.scpRemote(sshPort,src_Dashboard,sshUser,vitualIP,dst_Dashboard)

        commandDeploy = '''kubectl apply -f %s && chmod -R 777 %s''' %(dst_Dashboard,dst_kubernetesDir)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,commandDeploy)

        certsCreate = """openssl req -nodes -newkey rsa:2048 -keyout %s/tls.key -out %s/ca.csr -subj "/CN=\"%s\"" && openssl x509 -req -sha256 -days 365 -in %s/ca.csr -signkey %s/tls.key -out %s/tls.crt && kubectl create secret generic kubernetes-dashboard-certs --from-file=%s -n kubernetes-dashboard && kubectl describe secret/kubernetes-dashboard-certs --namespace kubernetes-dashboard && kubectl get secret -n kubernetes-dashboard""" %(dst_kubernetesDir,dst_kubernetesDir,dashboardDomain,dst_kubernetesDir,dst_kubernetesDir,dst_kubernetesDir,dst_kubernetesDir)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,certsCreate)

        src_dashboardAdminuse = '%s/dashboard-adminuser.yaml' %(dst_rootDir)
        dst_dashboardRbac = '%s/dashboard-rbac.yaml' %(dst_rootDir)
        dashboardAdminuser = '''cat > %s << OEF\napiVersion: v1\nkind: ServiceAccount\nmetadata:\n  name: admin-user\n  namespace: kubernetes-dashboard\nOEF''' %(src_dashboardAdminuse)
        dashboardRbac = '''cat > %s << OEF\napiVersion: rbac.authorization.k8s.io/v1\nkind: ClusterRoleBinding\nmetadata:\n  name: admin-user\nroleRef:\n  apiGroup: rbac.authorization.k8s.io\n  kind: ClusterRole\n  name: cluster-admin\nsubjects:\n- kind: ServiceAccount\n  name: admin-user\n  namespace: kubernetes-dashboard\nOEF''' %(dst_dashboardRbac)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,dashboardAdminuser)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,dashboardRbac)

        applyConfig = 'kubectl apply -f %s && kubectl apply -f %s' %(src_dashboardAdminuse,dst_dashboardRbac)
        remoteAction.sshRemote(sshPort,sshUser,vitualIP,applyConfig)
        print('\n','-'*30,' The Kubernetes cluster has been deployed ','-'*30,)
        print('- The virtual ip address: %s' %(vitualIP))
        print('- The Haproxy webmonitor: http://%s:8080/stats' %(deploys.vars()[0]['vitualIP']))

# deploys.prepareEnv()
# deploys.sshConfig()
# deploys.remotePkgsInstall()
# deploys.hostnameConfig()
# deploys.firewallConfig()
# deploys.keepaliveConfig()
# deploys.haproxyConfig()
# deploys.clusterCreate()
# deploys.loadbalancerConfig()
# deploys.joinMaster()
# deploys.joinWorker()
# deploys.calicoNetwork()
# deploys.helmInstall()
# deploys.metricServer()
# deploys.ingressNginx()
# deploys.metallb()
# deploys.argocd()
# deploys.dashboard()