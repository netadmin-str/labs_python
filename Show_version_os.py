from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler
import yaml
from ntc_templates.parse import parse_output

hosts = ['192.168.1.101']
#line = 'Cisco IOS Software, Linux Software (I86BI_LINUXL2-ADVENTERPRISEK9-M), Version 15.2(CML_NIGHTLY_20151103)FLO_DSGS7, EARLY DEPLOYMENT DEVELOPMENT BUILD, synced to  FLO_DSGS7_POSTCOLLAPSE_TEAM_TRACK_DSGS_PI5'


for host_ip in hosts:
    sshCli = ConnectHandler(
        device_type='cisco_ios',
        host=host_ip,
        port=22,
        username='admin',
        password='cisco'
    )

    output = sshCli.send_command("sh ip arp", use_textfsm=True)
    print(output)
   # output_parsed = parse_output(platform="cisco_ios", command="show ver eve", data=output)
   # print(output_parsed)
'''
   for element in output_parsed:
        device_id = element['neighbor'].split('.')
        description = 'Connect to ' + device_id[0]
        print(host_ip + ' ' + element['local_interface'] + ' - ' + description)
        commands = ['int ' + element['local_interface'],
                    'description ' + description]
        sshCli.send_config_set(commands)

    print(host_ip + ': OK')

'''
def send_command_to_devices(devices, commands, max_threads=2):
    data = {}
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_ssh = [
            executor.submit(send_show, device, commands) for device in devices
        ]
        for f in as_completed(future_ssh):
            result = f.result()
            data.update(result)
    return data


def send_show(device_dict, commands):
    if type(commands) == str:
        commands = [commands]
    ip = device_dict["ip"]
    result = {}
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        for command in commands:
            output = ssh.send_command(command)
            output_parsed = parse_output(platform="cisco_ios", command="show version", data=output)

            for element in output_parsed:
                device_id = element['neighbor'].split('.')
                description = 'Connect to ' + device_id[0]
                result.update({element['local_interface']: description})
                commands = ['int ' + element['local_interface'],
                            'description ' + description]
                ssh.send_config_set(commands)

    return {ip: result}


'''if __name__ == "__main__":
    filename = "devices_all.yaml"

    with open(filename) as f:
        devices = yaml.safe_load(f)
    print("Количество устройств:", len(devices))

    all_done = send_command_to_devices(
        devices, commands="show version", max_threads=16
    )

    # print(all_done)
    file = open('description_from_cdp_result.csv', 'w')

    for key, value in all_done.items():
        for key_int, value_desc in value.items():
            line = str(key) + ';' + key_int + ';' + value_desc
            file.write(line + '\n')

    file.close()
'''




