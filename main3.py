import ipaddress
import requests
from tqdm import tqdm


def merge_networks(networks):
    """
    Объединяет пересекающиеся подсети в список подсетей, которые их заменяют
    """
    if not networks:
        return []

    networks = [ipaddress.ip_network(n) for n in networks]
    networks.sort(key=lambda n: (n.prefixlen, n.num_addresses))

    new_networks = [networks[0]]

    for network in networks[1:]:
        if new_networks[-1].overlaps(network):
            new_networks[-1] = new_networks[-1].supernet()
        else:
            new_networks.append(network)

    return [str(n) for n in new_networks]


def calculate_allowed_ips(ip_addresses):
    allowed_ips = set()

    for ip_address in ip_addresses:
        if ":" not in ip_address:
            network = ipaddress.ip_network(ip_address)
            for current_network in allowed_ips.copy():
                if ipaddress.ip_network(current_network).overlaps(network):
                    allowed_ips.remove(current_network)
                    network = ipaddress.ip_network(
                        str(ipaddress.collapse_addresses([current_network, network]))
                    )
            allowed_ips.add(str(network))

    return merge_networks(allowed_ips)


def main():
    url = "https://reestr.rublacklist.net/api/v3/ips/"
    response = requests.get(url)
    data = response.json()
    ipv4_addresses = [a for a in data if ":" not in a]

    with open("allowed_ips.txt", "w") as f:
        for i, allowed_ip in enumerate(tqdm(calculate_allowed_ips(ipv4_addresses), desc="Calculating Allowed IPs")):
            f.write(f"AllowedIPs = {allowed_ip}\n")
            if i > 0 and i % 1000 == 0:
                tqdm.write(f"Wrote {i} Allowed IPs to file")

    print("\033[92m" + "Done." + "\033[0m")


if __name__ == "__main__":
    main()
