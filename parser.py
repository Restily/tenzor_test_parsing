from client import Client
from utils import Utils


class Parser:

    def __init__(self) -> None:
        self.cur_str_length = 0
        self.max_str_length = 80
        self.article_text = ''
        self.page_body: str

    def _parse_title(self, page_body: str) -> str:
        """
        Получение заголовка статьи из тега <title>

        :param page_body: HTML страницы

        :return: Заголовок статьи
        :rtype: str
        """
        title_tag = '<title>'

        # Поиск тега
        ind = page_body.find(title_tag) + len(title_tag)

        if ind == -1:
            raise Exception('Не получилось найти тег заголовка')

        text = page_body[ind:ind+1000]

        tind = len(text) + 1
        inds = ['—', '-', ':']

        # Извлечение названия без разделителей
        for raz_ind in inds:
            idx = text.find(raz_ind)

            if idx != -1:
                tind = min(idx, tind)

        if tind == -1:
            raise Exception('Не получилось найти заголовок')

        return text[:tind].lstrip(' ')

    def __remove_html_symbols(self, string: str) -> str:
        """
        Преобразование символов из HTML-кодировки в нормальный вид
        """
        symbols = {
            '&nbsp;': ' ',
            '&ndash;': '-',
            '&mdash;': '—',
            '&laquo;': '«',
            '&raquo;': '»'
        }

        for sym_code, symbol in symbols.items():
            string = string.replace(sym_code, symbol)

        return string

    def save_str(self, string: str, line_break: bool = False) -> None:
        """
        Преобразование строк из статьи по шаблону для записи в файл
        """
        string = self.__remove_html_symbols(string)

        # Разделение строки по словам
        string = string.split()

        for word in string:
            # Проверка на длину строки
            if self.cur_str_length + len(word) > self.max_str_length:
                self.article_text += f'\n{word} '
                self.cur_str_length = 0
            else:
                self.article_text += f'{word} '

            self.cur_str_length += len(word) + 1

        # Проверка на абзац/заголовок
        if line_break:
            self.article_text += '\n\n'
            self.cur_str_length = 0

    # def find(
    #     self,
    #     substr: str,
    #     start: Optional[int] = None,
    #     end: Optional[int] = None
    # ) -> int:
    #     """
    #     Функция для поиска первого вхождения подстроки в строке

    #     Данная функция доступна по умолчанию в Python, но здесь модификация для
    #     поиска по всей странице (то есть индексы идут с 0 до len(self.page_body))

    #     :param substr: Подстрока, которую необходимо найти
    #     :param start: Индекс элемента в строке, с которого производится поиск (по умолчанию 0)
    #     :param end: Индекс элемента в строке, до которого производится поиск (по умолчанию len(self.page_body))

    #     :return: Индекс вхождения подстроки в строку
    #     :rtype: int
    #     """
    #     if start is None:
    #         start = 0

    #     if end is None:
    #         end = len(self.page_body)

    #     idx = self.page_body[start:end].find(substr)

    #     if idx == -1:
    #         raise Exception('Не удалось найти строку')

    #     return idx + start

    def parse_tag_text(self, string: str, base_url: str) -> str:
        """
        Обработка строки из тега <p>

        :param string: строка для обработки
        :param base_url: 

        :rtype: str
        """
        text = []

        a_ind = string.find('<a')

        if a_ind == -1:
            return string

        while '<a' in string:
            a_ind = string.find('<a')

            text.append(string[:a_ind])

            ref = string[a_ind:].find('href=') + a_ind

            url_start = ref + len('href=')
            url_end = min(
                string[url_start:].find(' ') + url_start,
                string[url_start:].find('>') + url_start
            )

            idx = string.find('>') + 1
            end_idx = string.find('</a>')

            if string[url_start] == '"':
                url_start += 1

            if string[url_end] == '"':
                url_end += 1

            url = string[url_start:url_end]

            if url[0] == '/':
                url = f'{base_url}{url}'

            text.append(f'[{url}] {string[idx:end_idx]}')
            string = string[end_idx + len('</a>'):]

        text.append(string)

        # Очищение от запятых и точек в начале строк
        for i in range(len(text)):
            if text[i][0] == ',' or text[i][0] == '.':
                text[i - 1] += text[i][0]
                text[i] = text[i][1:]

        return ' '.join(text)

    def __delete_tags(self, page: str) -> str:
        """
        Удаление ненужных текстовых тегов

        :param page: HTML-страница

        :return: отформатированная HTML-страница
        :rtype: str
        """
        tags = ['<b>', '<strong>', '<i>', '<em>']

        for tag in tags:
            page = page.replace(tag, '')
            page = page.replace(f'</{tag[1:]}', '')

        return page

    def _parse_article(self, url: str) -> None:
        """
        Парсинг статьи
        """
        page_body = Client.get_page(url)
        page_body = self.__delete_tags(page_body)

        title = self._parse_title(page_body)
        self.save_str(title, True)

        # Нахождение индекса заголовка
        tind = 0
        ans_ind = -1
        title_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        while tind < len(page_body) and ans_ind < 0:
            tind = page_body.find(title, tind + len(title))

            if tind == -1:
                raise

            if page_body[tind - 1] == '>':
                cur_text = page_body[:tind - 1]

                errs = 0
                max_errs = 5

                while errs < max_errs:
                    lind = cur_text.rfind('<')

                    if lind == -1:
                        break

                    tag = cur_text[lind+1:lind+10]

                    if any([t in tag for t in title_tags]):
                        ans_ind = tind

                        break

                    cur_text = cur_text[:lind]
                    errs += 1

        page_body = page_body[tind + len(title):]
        check_end = 0
        start_check_end = False

        # Обработка тегов
        while True:
            tag_ind = page_body.find('<')

            tag_end_ind = min(
                page_body[tag_ind:].find(' '),
                page_body[tag_ind:].find('>')
            ) + tag_ind

            tag = page_body[tag_ind:tag_end_ind]

            if '<p' not in tag and '<div' not in tag:
                if check_end == 15:
                    break

                if start_check_end:
                    check_end += 1

                if not tag:
                    end_ind += 1
                elif tag[1] == '/':
                    end_ind = page_body[tag_ind:].find('>')
                else:
                    end_ind = page_body.find(f'</{tag[1:]}>')
            elif '<p' in tag:
                st_ind = page_body[tag_ind:].find('>') + 1 + tag_ind
                end_ind = page_body[tag_ind:].find('</p>') + tag_ind

                if '<a' in page_body[st_ind:end_ind]:
                    save_str = self.parse_tag_text(
                        page_body[st_ind:end_ind], 'https://lenta.ru')
                else:
                    page_body[st_ind:end_ind]
                    save_str = page_body[st_ind:end_ind]

                self.save_str(save_str)
                self.save_str('', True)
                start_check_end = True
            else:
                end_ind = page_body.find('>')

            end_ind = max(tag_ind + 1, end_ind)
            page_body = page_body[end_ind:]

        print('Парсинг завершен')

    def start(self, url: str) -> None:
        """
        Запуск парсера
        """
        self._parse_article(url)

        config = Utils.parse_url_config(url)

        Utils.save_text(
            dir=config['dir'],
            filename=config['filename'],
            text=self.article_text
        )
