import time
import paramiko
import json
from jinja2 import Template

devices = json.load(open("devices.json"))

for device in devices:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=device["ip_management"], username=device["username"], look_for_keys=True)
    print("Connecting to {} ...".format(device["ip_management"]))
    with client.invoke_shell() as ssh:
        print("Connected to {}  ...".format(device["ip_management"]))
        
        template = """

        terminal length 0
        conf t

        {% for interface in interfaces -%}
            int {{ interface.name }}
            ip add {{ interface.ip_address }}
        {% endfor %}

        router ospf 1 vrf control-Data
        {% for network_ip in ospf_networks -%}
            network {{ network_ip }} area 0
        {% endfor %}
        exit

        {% if name == "R3" -%}
            router ospf 1 vrf control-Data
            default-information originate
            exit
            {% for ip_access_list in access_lists_1 -%}
                access-list 1 {{ ip_access_list }}
            {% endfor %}
            int g0/1
                ip nat inside
                exit
            int g0/2
                ip nat outside
                exit
            ip nat inside source list 1 int g0/2 vrf control-Data overload
        {%- endif %}

        {% for ip_access_list in access_lists_2 -%}
            access-list 2 {{ ip_access_list }}
        {% endfor %}

        line vty 0 4
            access-class 2 in
            exit
        exit
        wr
        exit
        """
        j2_template = Template(template, trim_blocks=True)
        clistr = j2_template.render(device)
        ssh.send(clistr)
        time.sleep(10)
        print("Close connection !!!")

