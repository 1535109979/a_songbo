import requests


# 获取当前 IP 地址
def get_current_ip():
    response = requests.get('https://api.ipify.org')
    if response.status_code == 200:
        return response.text
    else:
        return None


# 查询 IP 地址对应的地址信息
def get_ip_address_info(ip):
    response = requests.get(f'http://ip-api.com/json/{ip}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


# 获取当前 IP 地址
current_ip = get_current_ip()
if current_ip:
    print(f"当前 IP 地址是：{current_ip}")

    # 查询当前 IP 地址对应的地址信息
    address_info = get_ip_address_info(current_ip)
    if address_info:
        print("地址信息：")
        print(f"国家：{address_info['country']}")
        print(f"地区：{address_info['regionName']}")
        print(f"城市：{address_info['city']}")
    else:
        print("无法获取地址信息")
else:
    print("无法获取当前 IP 地址")