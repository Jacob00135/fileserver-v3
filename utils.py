import psutil


def get_all_disk_path():
    name_list = []
    for p in psutil.disk_partitions():
        yield p.device
