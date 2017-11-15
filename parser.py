import re
import MySQLdb as mysql
from datetime import datetime
import mypackage.release as release


class Parser:
    def __init__(self):
        self.db = mysql.connect(
            host='Raistrike.mysql.pythonanywhere-services.com',
            user="Raistrike",
            passwd="Nuvoletta2", db="Raistrike$data")
        cur = self.db.cursor()
        cur.execute('SELECT id,title FROM manga')
        title_dict = {re.sub('[^\w]', '', x[1]).lower(): x[0] for x in cur.fetchall()}
        cur.execute('SELECT * FROM alias')
        for x in cur.fetchall():
            title_dict[x[1]] = x[0]
        self.title_dict = title_dict

    def __enter__(self):
        return self

    def parseall(self, values):
        to_correct = []
        for x in values:
            pub = x['publisher']
            if pub == 'planet':
                regex_planet(self.db, x, self.title_dict)
                continue
            if pub == 'star':
                regex_star(self.db, x, self.title_dict)
                continue
            if pub == 'jpop':
                regex_jpop(self.db, x, self.title_dict, to_correct)
                continue
        for x in correct_jpop(to_correct):
            release.insert(self.db, x)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit")
        self.db.close()


def regex_planet(db, values, title_dict):
    match = re.fullmatch('((.*)\\s(\\d+))|(.*)', values['title_volume'])
    if match and match.group(1):
        title = match.group(2)
        volume = int(match.group(3))
        lower = re.sub('[^\w]', '', title).lower()
        if lower in title_dict:
            release.insert(db, to_dict(title_dict[lower], volume, values))
        else:
            release.unknown(db, values)
    elif match and match.group(4):
        title = match.group(4)
        lower = re.sub('[^\w]', '', title).lower()
        if lower in title_dict:
            release.insert(db, to_dict(title_dict[lower], 1, values))
        else:
            release.unknown(db, values)


def regex_star(db, values, title_dict):
    match = re.fullmatch('((.*)\\sn\\.\\s(\\d+))|((.*)\\svolume\\sunico)', values['title_volume'])
    if match and match.group(1):
        title = match.group(2)
        volume = int(match.group(3))
        lower = re.sub('[^\w]', '', title).lower()
        if lower in title_dict:
            release.insert(db, to_dict(title_dict[lower], volume, values))
        else:
            release.unknown(db, values)
    elif match and match.group(4):
        title = match.group(5)
        lower = re.sub('[^\w]', '', title).lower()
        if lower in title_dict:
            release.insert(db, to_dict(title_dict[lower], 1, values))
        else:
            release.unknown(db, values)


def regex_jpop(db, values, title_dict, to_correct):
    match = re.fullmatch('((.*)\\s(\\d+))|(.*)', values['title_volume'])
    if match and match.group(1):
        title = match.group(2)
        volume = int(match.group(3))
        lower = re.sub('[^\w]', '', title).lower()
        if lower in title_dict:
            to_correct.append(to_dict(title_dict[lower], volume, values))
        else:
            release.unknown(db, values)
    elif match and match.group(4):
        title = match.group(4)
        lower = re.sub('[^\w]', '', title).lower()
        if lower in title_dict:
            to_correct.append(to_dict(title_dict[lower], 1, values))
        else:
            release.unknown(db, values)


def correct_jpop(values):
    news_list = [x for x in values if not x['cover']]
    other = [x for x in values if x not in news_list]
    for n in news_list:
        o = [x for x in other if x['manga_id'] == n['manga_id'] and x['volume'] == n['volume']]
        if o:
            n['cover'] = o[0]['cover']
    return news_list


def to_dict(manga_id, volume, values):
    return {'manga_id': manga_id,
            'subtitle': values['subtitle'],
            'volume': volume,
            'publisher': values['publisher'],
            'release_date': values['release_date'] if values['release_date'] else datetime.now().strftime('%Y-%m-%d'),
            'price': values['price'] if values['price'] else '0',
            'cover': values['cover']}
