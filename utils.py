import os
import psutil
from collections import OrderedDict

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
filesize_unit_list = ['B', 'KB', 'MB', 'GB', 'TB']


class MyFile(object):

    def __init__(self, dirpath, filename):
        self.dirpath = dirpath
        self.filename = filename
        self.filepath = os.path.join(dirpath, filename)

        self.__type = None
        self.__size_int = None
        self.__size_str = None
        self.__date_float = None
        self.__date_str = None

    @property
    def file_type(self):
        if self.__type is not None:
            return self.__type

        if os.path.isdir(self.filepath):
            self.__type = 'dir'
            return self.__type

        index = self.filename.rfind('.')
        if index < 0:
            self.__type = 'unknown'
            return self.__type

        extend_name = self.filename[index + 1:]
        self.__type = extension_type_map.get(extend_name, 'unknown')

        return self.__type

    @property
    def size_int(self):
        if self.__size_int is not None:
            return self.__size_int

        if os.path.isdir(self.filepath):
            self.__size_int = float('inf')
            return self.__size_int

        self.__size_int = os.path.getsize(self.filepath)
        return self.__size_int

    @property
    def size_str(self):
        if self.__size_str is not None:
            return self.__size_str
        
        if os.path.isdir(self.filepath):
            self.__size_str = ''
            return self.__size_str

        size = self.size_int
        i = 0
        while size >= 1024:
            size = size / 1024
            i = i + 1
        self.__size_str = '{} {}'.format(round(size, 2), filesize_unit_list[i])

        return self.__size_str
    
    @property
    def date_float(self):
        if self.__date_float is not None:
            return self.__date_float

        self.__date_float = os.path.getmtime(self.filepath)
        return self.__date_float

    @property
    def date_str(self):
        if self.__date_str is not None:
            return self.__date_str
    
        self.__date_str = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(self.date_float)
        )
        return self.__date_str


class MyDir(object):

    def __init__(self, path):
        self.path = path

        self.__files = None
    
    @property
    def files(self):
        if self.__files is not None:
            return self.__files

        self.__files = []
        for fn in os.listdir(self.path):
            myfile = MyFile(self.path, fn)
            self.__files.append(myfile)

        return self.__files

    def sort_files(self, by='type', ascending=False):
        if by == 'type':
            self.sort_files_by_type(ascending)
        elif by == 'name':
            self.sort_files_by_name(ascending)
        elif by == 'size':
            self.sort_files_by_size(ascending)
        elif by == 'date':
            self.sort_files_by_date(ascending)
        else:
            self.sort_files_by_type(ascending)

    def sort_files_by_type(self, ascending=False):
        if ascending:
            d = OrderedDict({
                'unknown': [],
                'text': [],
                'package': [],
                'image': [],
                'audio': [],
                'video': [],
                'dir': []
            })
        else:
            d = OrderedDict({
                'dir': [],
                'video': [],
                'audio': [],
                'image': [],
                'package': [],
                'text': [],
                'unknown': []
            })

        for f in self.files:
            d[f.file_type].append(f)

        sorted_files = []
        for ls in d.values():
            sorted_files.extend(ls)

        self.__files = sorted_files

    def sort_files_by_name(self, ascending=False):
        self.__files = sorted(
            self.files,
            key=lambda f: f.filename,
            reverse=ascending
        )
    
    def sort_files_by_size(self, ascending=False):
        self.__files = sorted(
            self.files,
            key=lambda f: f.size_int,
            reverse=not ascending
        )

    def sort_files_by_date(self, ascending=False):
        self.__files = sorted(
            self.files,
            key=lambda f: f.date_float,
            reverse=not ascending
        )


def get_all_disk_path():
    name_list = []
    for p in psutil.disk_partitions():
        yield p.device
