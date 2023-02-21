import requests
import ipaddress
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

# Скачиваем список IP адресов
url = 'https://reestr.rublacklist.net/api/v3/ips/'
response = requests.get(url)

if response.status_code != 200:
    logging.error(f"Failed to download the IP list. Status code: {response.status_code}")
    exit(1)

ip_list = response.json()
logging.info(f"Downloaded {len(ip_list)} IPs")

# Отбираем только IPv4 адреса и конвертируем их в объекты ipaddress.IPv4Network
networks = []
for ip in tqdm(ip_list, desc="Converting IPs to IPv4Network"):
    try:
        ip_address = ipaddress.IPv4Address(ip)
        if ip_address.is_private:
            continue
        networks.append(ipaddress.IPv4Network(ip))
    except ValueError:
        pass

logging.info(f"Filtered down to {len(networks)} IPv4 networks")

# Объединяем смежные сети
merged_networks = []
for network in tqdm(sorted(networks), desc="Merging networks"):
    if not merged_networks:
        merged_networks.append(network)
    else:
        last_network = merged_networks[-1]
        if network.subnet_of(last_network):
            continue
        elif network.overlaps(last_network):
            merged_networks[-1] = last_network.supernet()
        else:
            merged_networks.append(network)

logging.info(f"Merged down to {len(merged_networks)} networks")

# Преобразуем список сетей в AllowedIPs формат
allowed_ips = []
for network in tqdm(merged_networks, desc="Generating AllowedIPs"):
    allowed_ips.append(str(network))

logging.info(f"Generated {len(allowed_ips)} AllowedIPs")

# Записываем результат в файл
with open("allowed_ips.txt", "w") as f:
    f.write("AllowedIPs = ")
    f.write(", ".join(allowed_ips))

logging.info("Done")
