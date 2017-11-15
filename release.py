from datetime import datetime


def insert(db, values):
    cursor = db.cursor()
    try:
        if values['release_date']:
            ex = ('INSERT INTO releases (manga_id,subtitle,volume,release_date,price,cover) '
                  'VALUES({manga_id},"{subtitle}",{volume},\'{release_date}\',{price},"{cover}") '
                  'ON DUPLICATE KEY UPDATE cover=values(cover), release_date=values(release_date)').format_map(values)
            cursor.execute(ex)
            db.commit()
        else:
            ex = ('INSERT INTO releases (manga_id,subtitle,volume,price,cover) '
                  'VALUES({manga_id},"{subtitle}",{volune},{price},"{cover}") '
                  'ON DUPLICATE KEY UPDATE cover=values(cover)').format_map(values)
            cursor.execute(ex)
            db.commit()
        update_collection(db, values)
        update_manga(db, values)
    except Exception as e:
        print(e)
        db.rollback()


def update_collection(db, values):
    statement = 'INSERT INTO collection (manga_id,subtitle,volume,cover) VALUES({manga_id},"{subtitle}",{volume},"{cover}")'.format_map(
        values)
    otherwise = 'UPDATE collection SET cover="{cover}" WHERE manga_id={manga_id} AND volume={volume}'.format_map(values)
    update(db, statement, otherwise)


def update_manga(db, values):
    t = datetime.strptime(values['release_date'], '%Y-%m-%d').isocalendar()[:2]
    now = datetime.now().isocalendar()[:2]
    # print(t,now)
    if t <= now:
        cursor = db.cursor()
        cursor.execute('SELECT volumes,released,status,complete FROM manga WHERE id={manga_id}'.format_map(values))
        manga = cursor.fetchone()
        volumes, released, status, complete = manga[0], manga[1], manga[2], manga[3] == '1'
        if values['volume'] > released:
            update(db, 'UPDATE manga SET released={volume}, cover="{cover}" WHERE id={manga_id}'.format_map(values))
        if values['volume'] == 1 and status == 'TBA':
            update(db, 'UPDATE manga SET status="Ongoing" WHERE id={manga_id}'.format_map(values))
        if values['volume'] == volumes and complete:
            update(db, 'UPDATE manga SET status="Complete" WHERE id={manga_id}'.format_map(values))


def unknown(db, values):
    # title_volume,publisher,release_date,price,cover
    values['release_date'] = values['release_date'] if values['release_date'] else datetime.now().strftime('%Y-%m-%d')
    ex = ('INSERT INTO unknown (title,subtitle,publisher,release_date,price,cover) '
          'VALUES("{title_volume}","{subtitle}","{publisher}",\'{release_date}\',{price},"{cover}")').format_map(values)
    update(db, ex)


def update(db, statement, otherwise=None):
    try:
        db.cursor().execute(statement)
        db.commit()
    except Exception:
        db.rollback()
        if otherwise:
            update(db, otherwise)
