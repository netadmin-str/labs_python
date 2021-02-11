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
            output = ssh.send_command(command, use_textfsm=True)
            for element in output:
                device_version = element['version']

    return {ip: device_version}


if __name__ == "__main__":
    filename = "devices_all.yaml"

    with open(filename) as f:
        devices = yaml.safe_load(f)
    print("Количество устройств:", len(devices))

    all_done = send_command_to_devices(
        devices, commands="show version", max_threads=16
    )

    print(all_done)
    file = open('host_version.csv', 'w')

    for key, value in all_done.items():
        line = str(key) + ';' + value
        file.write(line + '\n')

    file.close()





