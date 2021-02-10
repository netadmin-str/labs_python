from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler
import yaml
from ntc_templates.parse import parse_output

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
            output_parsed = ssh.send_command(command, use_textfsm=True)

            for element in output_parsed:
                device_id = element['neighbor'].split('.')
                description = 'Connect to ' + device_id[0]
                result.update({element['local_interface']: description})
                commands = ['int ' + element['local_interface'],
                            'description ' + description]
                ssh.send_config_set(commands)

    return {ip: result}

if __name__ == "__main__":
    filename = "devices_all.yaml"

    with open(filename) as f:
        devices = yaml.safe_load(f)
    print("Количество устройств:", len(devices))

    all_done = send_command_to_devices(
        devices, commands="show cdp neighbors", max_threads=16
    )

    file = open('description_from_cdp_result.csv', 'w')

    for key, value in all_done.items():
        for key_int, value_desc in value.items():
            line = str(key)+';'+key_int+';'+value_desc
            print(line)
            file.write(line + '\n')

    file.close()



    

