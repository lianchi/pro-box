import netifaces


def get_local_ipaddr():
    results = []
    for i in netifaces.interfaces():
        info = netifaces.ifaddresses(i)
        if netifaces.AF_INET not in info:
            continue
        results.append(info[netifaces.AF_INET][0]['addr'])
    return results

if __name__ == '__main__':
    print(get_local_ipaddr())