import pexpect
import json

PROMPT = '#'
devices = json.load(open("devices.json"))
USERNAME = 'admin'
PASSWORD = 'cisco'

for device in devices:
    child = pexpect.spawn('telnet ' + device["ip_management"])
    child.expect('Username')
    child.sendline(USERNAME)
    child.expect('Password')
    child.sendline(PASSWORD)
    child.expect(PROMPT)

    child.sendline("conf t")
    child.expect(PROMPT)
    child.sendline("int lo0")
    child.expect(PROMPT)
    child.sendline("ip add " + device["ip_loopback"] + " 255.255.255.255")
    child.expect(PROMPT)

    for _ in range(2):
        child.sendline('exit')
        child.expect(PROMPT)
    
    child.sendline('show ip int br')
    child.expect(PROMPT)
    
    result = child.before
    print()
    print(result.decode('UTF-8'))

    child.sendline('exit')
    

