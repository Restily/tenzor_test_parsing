import sys
from typing import Optional
from urllib.request import urlopen


class Client:

    @classmethod
    def __decode_body(cls, response) -> bytes:
        """
        Декодинг ответа от сервера (html-страницы)

        :param response: Ответ от сервера (функция get_page)
        
        :return: Декодированную страницу в кодировке charset (по умолчанию utf-8)
        :rtype: bytes
        """
        charset = 'utf-8'

        for header in response.getheaders():
            if header[0] == 'Content-Type':
                s = 'charset='

                idx = header[1].rfind(s)

                if idx != -1:
                    charset = header[1][idx + len(s):]

        return response.read().decode(charset)

    @classmethod
    def get_page(cls, url: str) -> str:
        """
        Получение содержимого страницы

        :param url: url страницы

        :return: HTML страница
        :rtype: str
        """
        print("Идет загрузка страницы...")

        try:
            with urlopen(url, timeout=10) as response:
                body = cls.__decode_body(response)

                print("Страница загружена")

                return str(body)
        except Exception as error:
            print(
                f'Возникла ошибка при загрузке страницы: {error}. Происходит выход из программы.')
            sys.exit(1)