import time
import paramiko
import json

devices = json.load(open("devices.json"))

for device in devices:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=device["ip_management"], username=device["username"], look_for_keys=True)
    print("Connecting to {} ...".format(device["ip_management"]))
    with client.invoke_shell() as ssh:
        print("Connected to {}  ...".format(device["ip_management"]))

        ssh.send("terminal length 0\n")        
        time.sleep(1)
        # result = ssh.recv(1000).decode('ascii')
        # print(result)
              
        ssh.send("conf t\n")

        #Assign IP
        for interface in device["interfaces"]:
            ssh.send("int " + interface["name"] + "\n")
            ssh.send("ip add " + interface["ip_address"] + "\n")
        time.sleep(1)
        
        #OSPF
        ssh.send("router ospf 1 vrf control-Data\n")
        for network_ip in device["ospf_networks"]:
            ssh.send("network " + network_ip + " area 0\n")
            time.sleep(1)
        ssh.send("exit\n")
        time.sleep(1)

        #Advertise default route And Pat on R3
        if device["name"] == "R3":
            ssh.send("router ospf 1 vrf control-Data\n")
            ssh.send("default-information originate\n")
            ssh.send("exit\n")
            time.sleep(1)
            for ip_access_list in device["access-lists-1"]:
                ssh.send("access-list 1 " + ip_access_list + "\n")
            time.sleep(1)
            ssh.send("int g0/1\n")
            ssh.send("ip nat inside\n")
            ssh.send("int g0/2\n")
            ssh.send("ip nat outside\n")
            ssh.send("exit\n")
            ssh.send("ip nat inside source list 1 int g0/2 vrf control-Data overload\n")
            time.sleep(1)
        
        #Access-class for telnet/ssh from Management plane and VPN Network
        for ip_access_list in device["access-lists-2"]:
            ssh.send("access-list 2 " + ip_access_list + "\n")
        ssh.send("line vty 0 4\n")
        ssh.send("access-class 2 in\n")
        ssh.send("exit\n")
        time.sleep(1)
        
        ssh.send("wr\n")
        ssh.send("exit\n")
        print("Close connection !!!")

