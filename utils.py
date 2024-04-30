import os
import psutil

extension_type_map = {
    'rar': 'package',
    'zip': 'package',
    '7z': 'package',
    'gz': 'package',
    'tar': 'package',
    'mp4': 'video',
    'm4v': 'video',
    'mkv': 'video',
    'webm': 'video',
    'mov': 'video',
    'avi': 'video',
    'wmv': 'video',
    'mpg': 'video',
    'flv': 'video',
    'mpeg': 'video',
    'rm': 'video',
    'ram': 'video',
    'rmvb': 'video',
    'jpg': 'image',
    'png': 'image',
    'jpeg': 'image',
    'gif': 'image',
    'webp': 'image',
    'ico': 'image',
    'bmp': 'image',
    'psd': 'image',
    'dwg': 'image',
    'xcf': 'image',
    'jpx': 'image',
    'apng': 'image',
    'cr2': 'image',
    'tif': 'image',
    'jxr': 'image',
    'heic': 'image',
    'mp3': 'audio',
    'wav': 'audio',
    'm4a': 'audio',
    'flac': 'audio',
    'aac': 'audio',
    'ogg': 'audio',
    'mid': 'audio',
    'amr': 'audio',
    'aiff': 'audio',
    'txt': 'text',
    'py': 'text',
    'js': 'text',
    'ipynb': 'text',
    'ini': 'text',
    'css': 'text',
    'scss': 'text',
    'sass': 'text',
    'html': 'text',
    'xml': 'text',
    'json': 'text',
    'java': 'text',
    'c': 'text',
    'cpp': 'text',
    'md': 'text'
}


def get_all_disk_path():
    name_list = []
    for p in psutil.disk_partitions():
        yield p.device


def get_file_type(filepaths):
    file_type = []
    for fp in filepaths:
        if os.path.isdir(fp):
            file_type.append('dir')
            continue

        fn = os.path.basename(fp)
        index = fn.rfind('.')
        if index < 0:
            file_type.append('unknown')
            continue
        extend_name = fn[index + 1:]
        t = extension_type_map.get(extend_name, 'unknown')
        file_type.append(t)

    return file_type
