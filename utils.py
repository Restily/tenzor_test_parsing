import os

from config import BASE_DIR


class Utils:

    @staticmethod
    def parse_url_config(url: str) -> dict:
        """
        Обработка URL из командной строки
        """
        if 'http' not in url or 'https' not in url:
            raise Exception("""
                Не найден протокол (http или https). 
                Пожалуйста, вставьте полную ссылку.
            """)

        proto_ind = url.find('://')

        if proto_ind == -1:
            raise Exception('Неверный формат URL')

        if url[-1] == '/':
            url = url[:-1]

        full_url = url[proto_ind+len('://'):].split('/')

        if '.' in full_url[-1]:
            filename = full_url[-1].split('.')[0]
        else:
            filename = full_url[-1]

        return {
            'base_url': full_url[0],
            'url': url,
            'dir': '/'.join(full_url[:-1]),
            'filename': filename
        }

    @staticmethod
    def save_text(dir: str, filename: str, text: str) -> None:
        """
        Сохранение текста в заданной директории

        Схема: [BASE_DIR]/[dir]/[filename].txt

        :param dir: директория файла
        :param filename: имя файла
        :param text: текст, который нужно сохранить в файл
        """
        print('Сохранение в файл...')

        dir = f'{BASE_DIR}/{dir}'

        if not os.path.exists(dir):
            os.makedirs(dir)

        path = f'{dir}/{filename}.txt'

        with open(f'{dir}/{filename}.txt', 'w') as f:
            f.write(text)

        print(f'Статья сохранена в файле: {path}')
