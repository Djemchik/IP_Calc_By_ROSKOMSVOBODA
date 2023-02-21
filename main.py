import requests
from tqdm import tqdm

# делаем GET-запрос к API и получаем данные в формате JSON
url = "https://reestr.rublacklist.net/api/v3/ips/"
response = requests.get(url)
data = response.json()

# выбираем только IPv4-адреса и объединяем их, если это возможно
ipv4_addresses = []
for address in tqdm(data, desc="Processing IP addresses"):
    if ":" not in address:
        ipv4_addresses.append(address)

# записываем адреса в файл в формате "Allowed IPs = адрес/маска подсети, адрес/маска подсети, ..."
with open("allowed_ips.txt", "w") as f:
    f.write("AllowedIPs = ")
    for i, address in enumerate(ipv4_addresses):
        if "/" not in address:
            address += "/32"  # добавляем маску подсети по умолчанию
        f.write(address)
        if i != len(ipv4_addresses) - 1:
            f.write(", ")
