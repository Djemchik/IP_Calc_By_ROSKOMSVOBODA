import ipaddress
import requests
from tqdm import tqdm  # прогресс-бар

def calculate_allowed_ips(ip_addresses):
    allowed_ips = set()
    for ip_address in ip_addresses:
        if ":" not in ip_address:
            network = ipaddress.ip_network(ip_address)
            for current_network in allowed_ips.copy():
                if ipaddress.ip_network(current_network).overlaps(network):
                    allowed_ips.remove(current_network)
                    network = ipaddress.ip_network(str(ipaddress.collapse_addresses([current_network, network])))
            allowed_ips.add(str(network))
    return allowed_ips


# def calculate_allowed_ips(ip_list):
#     """
#     Рассчитывает маски подсетей для списка IP-адресов в формате CIDR.

#     :param ip_list: список IP-адресов в формате CIDR
#     :return: список масок подсетей в формате CIDR
#     """
#     # преобразуем каждый IP-адрес в объект ipaddress.IPv4Network
#     networks = [ipaddress.IPv4Network(ip) for ip in ip_list]

#     # сортируем список сетей по адресу
#     sorted_networks = sorted(networks)

#     # объединяем перекрывающиеся сети
#     merged_networks = []
#     current_network = sorted_networks[0]
#     for network in sorted_networks[1:]:
#         if current_network.overlaps(network):
#             current_network = current_network.supernet_of(network)
#         else:
#             merged_networks.append(current_network)
#             current_network = network
#         # выводим прогресс выполнения цикла каждые 1000 итераций
#         if len(merged_networks) % 1000 == 0:
#             tqdm.write(f"Processed {len(merged_networks)} networks")

#     merged_networks.append(current_network)

#     # преобразуем каждую маску подсети в формат "адрес/маска подсети"
#     allowed_ips = [f"{str(network.network_address)}/{str(network.netmask)}" for network in merged_networks]

#     return allowed_ips

# делаем GET-запрос к API и получаем данные в формате JSON
url = "https://reestr.rublacklist.net/api/v3/ips/"
response = requests.get(url)
data = response.json()

# выбираем только IPv4-адреса и объединяем их, если это возможно
ipv4_addresses = []
for address in tqdm(data, desc="Processing IP addresses"):
    if ":" not in address:
        ipv4_addresses.append(address)
    # выводим прогресс выполнения цикла каждые 5000 итераций
    if len(ipv4_addresses) % 5000 == 0:
        tqdm.write(f"Processed {len(ipv4_addresses)} IPv4 addresses")

# рассчитываем маски подсетей
allowed_ips = calculate_allowed_ips(ipv4_addresses)

# выводим результат
result = "Allowed IPs = " + ", ".join(allowed_ips)
print("\033[92m" + result + "\033[0m")  # выводим сообщение в зеленом цвете
