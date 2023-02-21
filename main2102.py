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


# делаем GET-запрос к API и получаем данные в формате JSON
url = "https://reestr.rublacklist.net/api/v3/ips/"
response = requests.get(url)
data = response.json()

# выбираем только IPv4-адреса и объединяем их, если это возможно
ipv4_addresses = []
for i, address in enumerate(tqdm(data, desc="Processing IP addresses")):
    if ":" not in address:
        ipv4_addresses.append(address)
    # выводим прогресс выполнения цикла каждые 5000 итераций
    if i > 0 and i % 5000 == 0:
        tqdm.write(f"Processed {i} IPv4 addresses")

# рассчитываем маски подсетей
allowed_ips = calculate_allowed_ips(ipv4_addresses)

# выводим результат
result = "Allowed IPs = " + ", ".join(allowed_ips)
print("\033[92m" + result + "\033[0m")  # выводим сообщение в зеленом цвете

print("\033[1m" + "\033[91m" + "УСПЕХ" + "\033[0m") # выводим сообщение "УСПЕХ" в разноцветных буквах
