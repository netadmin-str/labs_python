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
    result = ""
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        interface_count = 0
        for command in commands:
            output = ssh.send_command(command)
            output_parsed = parse_output(platform="cisco_ios", command="show ip interface brief", data=output)
            for element in output_parsed:
                if element['status'] == 'administratively down':
                    show_int = ssh.send_command("sh int " + element['intf'])
                    show_int_parsed = parse_output(platform="cisco_ios", command="show interfaces", data=show_int)
                    if show_int_parsed[0]['last_input'] == 'never':
                        interface_count += 1
                elif element['status'] == 'down':
                    interface_count += 1
        result = interface_count
    return {ip: result}


if __name__ == "__main__":
    filename = "devices_all.yaml"

    with open(filename) as f:
        devices = yaml.safe_load(f)
    print("Количество устройств:", len(devices))

    all_done = send_command_to_devices(
        devices, commands="sh ip int br", max_threads=16
    )

    print(all_done)
    interface_count = 0
    for key in all_done:
        interface_count += all_done[key]

    print(f'Intreface count {interface_count}')

