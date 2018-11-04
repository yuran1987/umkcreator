import platform, django, socket, subprocess
from collections import OrderedDict
from .core_funcs import remove_dublicates
from psutil import net_if_addrs


def get_os_info():
    return [platform.node(),                #название узла
            platform.platform(),            #Полное название операционной системы
            platform.python_version()]      #Версия python

def get_cpu_info():
    res = []
    with open('/proc/cpuinfo') as f:
        for line in f:
            # Ignore the blank line separating the information between
            # details about two processing units
            if line.strip():
                if line.rstrip('\n').startswith('model name') or line.rstrip('\n').startswith('Processor'):
                    res.append(line.rstrip('\n').split(':')[1])
    return remove_dublicates(res)

def get_cpu_cores():
    res = subprocess.run("nproc",shell=True, stdout=subprocess.PIPE)
    return res.stdout


def get_meminfo():
    meminfo = OrderedDict()
    with open('/proc/meminfo') as f:
        for line in f:
            meminfo[line.split(':')[0]] = line.split(':')[1].strip()
    return meminfo

def get_django_version():
    return django.get_version()

def get_ip_address_server():
    res = []
    for interface, snics in net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET and str(snic.address).split(".")[0] != str(127):
                res.append(snic.address)
    return res

def get_ip_client(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
