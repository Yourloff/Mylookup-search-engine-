import re
from urllib.parse import urljoin
from urllib.request import urlopen
import psycopg2
from bs4 import *

ignorewords = {'a', 'about', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'been', 'but', 'by', 'can',
               'could', 'do', 'for', 'from', 'has', 'have', 'i', 'if', 'in', 'is', 'it', 'me', 'no', 'not', 'of', 'on',
               'one', 'or', 'so', 'that', 'the', 'them', 'there', 'they', 'this', 'to', 'was', 'we', 'what', 'which',
               'will', 'with', 'would', 'you', 'а', 'будем', 'будет', 'будете', 'будешь', 'буду', 'будут', 'будучи',
               'будь', 'будьте', 'бы', 'был', 'была', 'были', 'было', 'быть', 'в', 'вам', 'вами', 'вас', 'весь', 'во',
               'вот', 'все', 'всё', 'всего', 'всей', 'всем', 'всём', 'всеми', 'всему', 'всех', 'всею', 'всея', 'всю',
               'вся', 'вы', 'да', 'для', 'до', 'его', 'едим', 'едят', 'ее', 'её', 'ей', 'ел', 'ела', 'ем', 'ему', 'емъ',
               'если', 'ест', 'есть', 'ешь', 'еще', 'ещё', 'ею', 'же', 'за', 'и', 'из', 'или', 'им', 'ими', 'имъ', 'их',
               'к', 'как', 'кем', 'ко', 'когда', 'кого', 'ком', 'кому', 'комья', 'которая', 'которого', 'которое',
               'которой', 'котором', 'которому', 'которою', 'которую', 'которые', 'который', 'поэтому', 'по',
               'которым', 'которыми', 'которых', 'кто', 'меня', 'мне', 'мной', 'мною', 'мог', 'моги', 'могите', 'могла',
               'могли', 'могло', 'могу', 'могут', 'мое', 'моё', 'моего', 'моей', 'моем', 'моём', 'моему', 'моею',
               'можем', 'может', 'можете', 'можешь', 'мои', 'мой', 'моим', 'моими', 'моих', 'мочь', 'мою', 'моя', 'мы',
               'на', 'нам', 'нами', 'нас', 'наше', 'наш', 'наша', 'нашего', 'нашей', 'нашем', 'нашему', 'нашею', 'наши',
               'нашим', 'нашими', 'наших', 'нашу', 'не', 'него', 'нее', 'неё', 'ней', 'нем', 'нём', 'нему', 'нет',
               'нею', 'ним', 'ними', 'них', 'но', 'о', 'об', 'один', 'одна', 'одни', 'одним', 'одними', 'одних', 'одно',
               'одного', 'одной', 'одном', 'одному', 'одною', 'одну', 'он', 'она', 'оне', 'они', 'оно', 'от', 'оп',
               'при', 'с', 'сам', 'сама', 'сами', 'самим', 'самими', 'самих', 'само', 'самого', 'самом', 'самому',
               'саму', 'свое', 'своё', 'своего', 'своей', 'своем', 'своём', 'своему', 'своею', 'свои', 'свой', 'своим',
               'своими', 'своих', 'свою', 'своя', 'себе', 'себя', 'собой', 'собою', 'та', 'так', 'такая', 'такие',
               'таким', 'такими', 'таких', 'такого', 'такое', 'такой', 'таком', 'такому', 'такою', 'такую', 'те',
               'тебе', 'тебя', 'тем', 'теми', 'тех', 'то', 'тобой', 'тобою', 'того', 'той', 'только', 'том', 'томах',
               'тому', 'тот', 'тою', 'ту', 'ты', 'у', 'уже', 'чего', 'чем', 'чём', 'чему', 'что', 'чтобы', 'эта', 'эти',
               'этим', 'этими', 'этих', 'это', 'этого', 'этой', 'этом', 'этому', 'этот', 'этою', 'эту', 'я',
               }


class crawlersearch:
    # Инициализация сканера с именем базы данных
    def __init__(self):
        self.con = psycopg2.connect(dbname='mylookup', user='postgres',
                                    password='pythonPsql1999', host='localhost')
        self.cur = self.con.cursor()

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def get_urls(self):
        self.cur.execute('SELECT link_site from users_featuredsite')
        url = self.cur.fetchall()
        return url

    # Вспомогательная функция для получения идентификатора записи и добавления
    # это если его нет
    def getentryid(self, table, field, value):
        self.cur.execute("select rowid from %s where %s='%s'" % (table, field, value))
        res = self.cur.fetchone()
        if res is None:
            self.cur.execute("insert into %s (%s) values ('%s') RETURNING rowid" % (table, field, value))
            return self.cur.fetchone()[0]
        else:
            return res[0]

    def getentryurlid(self, table, field, value, title):
        self.cur.execute("select rowid from %s where %s='%s'" % (table, field, value))
        res = self.cur.fetchone()
        if res is None:
            self.cur.execute("insert into %s (%s, title) values ('%s', '%s') RETURNING rowid" % (
                table, field, value, title.replace("'", "")))
            return self.cur.fetchone()[0]
        else:
            return res[0]

    # Индексировать отдельную страницу
    def addtoindex(self, url, soup):
        global title
        if self.isindexed(url):
            return
        print('Индексируется: ' + url)

        text = self.gettextonly(soup)
        words = self.separatewords(text)
        isrobots = url.find("robots.txt")
        istitles = url.find('title')
        if isrobots == -1:
            if istitles == -1:
                title = soup.find('title').string
                urlid = self.getentryurlid('users_urllist', 'url', url, title)
            else:
                urlid = self.getentryurlid('users_urllist', 'url', url, url)
        else:
            urlid = self.getentryurlid('users_urllist', 'url', url, "robots.txt")

        # Связать каждое слово с этим URL
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('users_wordlist', 'word', word)
            self.cur.execute(
                "insert into users_wordlocation(urlid, wordid, loc) values (%d,%d,%d)" % (urlid, wordid, i))

    # Извлечь текст со страницы HTML (без тегов)
    def gettextonly(self, soup):
        v = soup.string
        if v is None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # Разделить слова любым непробельным символом
    def separatewords(self, text):
        splitter = re.compile('\\W+')
        return [s.lower() for s in splitter.split(text) if s != '']

    # Возвращает true, если данный URL уже проиндексирован
    def isindexed(self, url):
        self.cur.execute("select rowid from users_urllist where url='%s'" % url)
        u = self.cur.fetchone()
        if u is not None:
            # Проверяем, что страница посещалась
            self.cur.execute('select * from users_wordlocation where urlid=%d' % u[0])
            v = self.cur.fetchone()
            if v is not None:
                return True
        return False

    # Добавить ссылку между двумя страницами
    def addlinkref(self, urlFrom, urlTo, linkText):
        words = self.separatewords(linkText)
        fromid = self.getentryid('users_urllist', 'url', urlFrom)  # page
        toid = self.getentryurlid('users_urllist', 'url', urlTo, linkText)  # url
        if fromid == toid:
            return
        self.cur.execute("insert into users_link(fromid,toid) values (%d,%d) RETURNING rowid" % (fromid, toid))
        linkid = self.cur.fetchone()[0]
        for word in words:
            if word in ignorewords:
                continue
            wordid = self.getentryid('users_wordlist', 'word', word)
            self.cur.execute("insert into users_linkwords(linkid,wordid) values (%d,%d)" % (linkid, wordid))

    # Начиная со списка страниц, сделайте ширину
    # первый поиск до заданной глубины, индексация страниц
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urlopen(page)
                except Exception as e:
                    print("Не могу открыть %s " % page)
                    print("%s " % e)
                    continue
                soup = BeautifulSoup(c.read(), 'html.parser')
                self.addtoindex(page, soup)

                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]  # удалить часть URL после знака #
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)

                self.dbcommit()
            pages = newpages


# class Command(BaseCommand):
#     help = 'Сканирование сайтов'
#     def handle(self, *args, **options):
#         p = crawler()
#         urls = p.get_urls()
#         for i in urls:
#             p.crawl(i)
def main():
    p = crawlersearch()
    urls = p.get_urls()
    for i in urls:
        p.crawl(i)


if __name__ == "__main__":
    main()
