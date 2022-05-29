import sys
import os
import re
import shutil
from threading import Thread


FILE_TYPES = {'images': ('JPEG', 'PNG', 'JPG', 'SVG', 'BMP', 'TIF', 'TIFF', 'GIF'),
              'archives': ('ZIP', 'GZ', 'TAR'),
              'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
              'audio': ('MP3', 'OGG', 'WAV', 'AMR'),
              'video':  ('AVI', 'MP4', 'MOV', 'MKV', 'MPG')
              }

files_info = {'images': [], 'archives': [], 'documents': [],
              'audio': [], 'video': [], 'unknown': [], 'known': []}


class MyThread(Thread):

    def __init__(self, file_type, extensions, item, folder, root):
        super().__init__()
        self.file_type = file_type
        self.extensions = extensions
        self.item = item
        self.folder = folder
        self.root = root

    def run(self):

        # Расширение файла
        ext = self.item[self.item.rfind(".") + 1:]
        ext_upper = ext.upper()
        normalized_item = normalize(self.item)
        # Определяем нормализованное имя папки назначения без учета корневой папки
        destination_folder = normalize(self.folder.replace(self.root, ''))
        destination_file_path = fr'{self.root}/{self.file_type}{destination_folder}/{normalized_item}'
        if ext_upper in self.extensions:
            files_info[self.file_type].append(destination_file_path)
            if ext_upper not in files_info['known']:
                files_info['known'].append(ext_upper)
            create_folders_chain(destination_folder, self.root, self.file_type)
            shutil.move(fr'{self.folder}/{self.item}', destination_file_path)

            if self.file_type == 'archives':
                archive_folder = normalized_item.removesuffix(f'.{ext}')
                create_folders_chain(
                    f'{destination_folder}/{archive_folder}', self.root, 'archives')
                shutil.unpack_archive(
                    destination_file_path, fr'{self.root}/archives{destination_folder}/{archive_folder}')
                shutil.move(destination_file_path,
                            fr'{self.root}/archives{destination_folder}/{archive_folder}')
        else:
            files_info['unknown'].append(ext_upper)


def create_folder(name):

    if not os.path.exists(name):
        os.mkdir(name)


def create_folders_chain(chain, root, file_type):

    next_folder = ''
    # Просмотр элементов пути для папки назначения
    for folder_part in chain.split('/'):
        if folder_part:
            next_folder += f'/{folder_part}'
            # Создаем вложенную папку по цепочке
            create_folder(fr'{root}/{file_type}{next_folder}')


def normalize(string):

    translit_table = {'а': 'a', 'А': 'A',
                      'б': 'b', 'Б': 'B',
                      'в': 'v', 'В': 'V',
                      'г': 'g', 'Г': 'G',
                      'ґ': 'g', 'Ґ': 'G',
                      'д': 'd', 'Д': 'D',
                      'е': 'e', 'Е': 'E',
                      'ё': 'io', 'Ё': 'Io',
                      'є': 'ye', 'Є': 'Ye',
                      'ж': 'zh', 'Ж': 'Zh',
                      'з': 'z', 'З': 'Z',
                      'и': 'i', 'И': 'I',
                      'й': 'y', 'Й': 'Y',
                      'і': 'i', 'І': 'I',
                      'ї': 'yi', 'Ї': 'Yi',
                      'к': 'k', 'К': 'K',
                      'л': 'l', 'Л': 'L',
                      'м': 'm', 'М': 'M',
                      'н': 'n', 'Н': 'N',
                      'о': 'o', 'О': 'O',
                      'п': 'p', 'П': 'P',
                      'р': 'r', 'Р': 'R',
                      'с': 's', 'С': 'S',
                      'т': 't', 'Т': 'T',
                      'у': 'u', 'У': 'U',
                      'ф': 'f', 'Ф': 'F',
                      'х': 'h', 'Х': 'H',
                      'ц': 'ts', 'Ц': 'Ts',
                      'ч': 'ch', 'Ч': 'Ch',
                      'ш': 'sh', 'Ш': 'Sh',
                      'щ': 'sch', 'Щ': 'Sch',
                      'ъ': '', 'Ъ': '',
                      'ы': 'y', 'Ы': 'Y',
                      'ь': '', 'Ь': '',
                      'э': 'e', 'Э': 'E',
                      'ю': 'iu', 'Ю': 'Iu',
                      'я': 'ia', 'Я': 'Ia'}

    for key in translit_table:
        string = string.replace(key, translit_table[key])

    return re.sub('[^A-Za-z0-9_\./:]', '_', string)


def order_files(folder, root):

    # Перебираем элементы в текущей папке
    for item in os.listdir(folder):
        if os.path.isdir(f'{folder}/{item}'):
            # Если папка не относится к стандартным
            if item not in list(FILE_TYPES.keys()):
                # Рекурсивный просмотр папки
                order_files(f'{folder}/{item}', root)
        else:
            for file_type, extensions in FILE_TYPES.items():
                # Перебираем категории файлов и рассортировываем по стандартным папкам
                MyThread(file_type, extensions, item, folder, root).start()


def remove_empty(folder):

    while True:
        empty_nonstd_folders_count = 0
        tree = os.walk(folder)
        for item in tree:
            if item[1] == [] and item[2] == [] and not item[0].endswith(tuple(FILE_TYPES.keys())):
                empty_nonstd_folders_count += 1
                os.rmdir(item[0])
        if empty_nonstd_folders_count == 0:
            break


def main():

    if len(sys.argv) == 1:
        folder_name = os.getcwd()
    else:
        folder_name = sys.argv[1]
    create_folder(fr'{folder_name}/archives')
    create_folder(fr'{folder_name}/audio')
    create_folder(fr'{folder_name}/documents')
    create_folder(fr'{folder_name}/images')
    create_folder(fr'{folder_name}/video')
    print('Начинаем сортировку...')
    order_files(folder_name, folder_name)
    print('Удаляем пустые папки...')
    remove_empty(folder_name)
    for key, value in files_info.items():
        if key == 'unknown':
            pass
        elif key == 'known':
            pass
        else:
            print('-' * 30)
            print(f'{key}:')
            print('-' * 30)
            for file in value:
                print(file)
    print('-' * 30)
    known_set = set(files_info["known"])
    if len(known_set):
        print(f'Известные расширения: {known_set}')
    else:
        print(f'Известные расширения: НЕ НАЙДЕНЫ')
    print('-' * 30)
    unknown_set = set(files_info["unknown"]) - set(files_info["known"])
    if len(unknown_set):
        print(f'Неизвестные расширения: {unknown_set}')
    else:
        print(f'Неизвестные расширения: НЕ НАЙДЕНЫ')


if __name__ == '__main__':
    main()
