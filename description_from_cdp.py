from netmiko import ConnectHandler
from ntc_templates.parse import parse_output

hosts = ['192.168.1.101', '192.168.1.102','192.168.1.103']



for host_ip in hosts:
    sshCli = ConnectHandler(
            device_type = 'cisco_ios',
            host = host_ip,
            port = 22,
            username = 'admin',
            password = 'cisco'
            )

    output = sshCli.send_command("sh cdp nei")
    output_parsed = parse_output(platform="cisco_ios", command="show cdp neighbors", data=output)

    for element in output_parsed:
        device_id = element['neighbor'].split('.')
        description = 'Connect to ' + device_id[0]
        print(host_ip + ' ' + element['local_interface'] + ' - ' + description)
        commands = ['int ' + element['local_interface'],
                    'description ' + description]
        sshCli.send_config_set(commands)
    
    print(host_ip + ': OK')

    

