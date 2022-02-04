import pexpect
import json

PROMPT = '#'
devices = json.load(open("devices.json"))
USERNAME = 'admin'
PASSWORD = 'cisco'

child = pexpect.spawn('telnet ' + '10.0.15.106')
child.expect('Username')
child.sendline(USERNAME)
child.expect('Password')
child.sendline(PASSWORD)
child.expect(PROMPT)

for device in devices:
    child.sendline('telnet ' + device["ip_management"])
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

    result = child.before
    print(result)
    print()
    print(result.decode('UTF-8'))

    for _ in range(3):
        child.sendline('exit')
        child.expect(PROMPT)
    
    

