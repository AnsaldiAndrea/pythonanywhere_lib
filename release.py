from datetime import datetime

def insert(db, values):
    cursor = db.cursor()
    try:
        if values['release_date']:
            ex = ('insert into releases (manga_id,subtitle,volume,release_date,price,cover) '
            'values({manga_id},"{subtitle}",{volume},\'{release_date}\',{price},"{cover}") '
            'on duplicate key update cover=values(cover), release_date=values(release_date)').format_map(values)
            cursor.execute(ex)
            db.commit()
        else:
            ex = ('insert into releases (manga_id,subtitle,volume,price,cover) '
            'values({manga_id},"{subtitle}",{volune},{price},"{cover}") '
            'on duplicate key update cover=values(cover)').format_map(values)
            cursor.execute(ex)
            db.commit()
        update_collection(db,values)
        update_manga(db,values)
    except Exception as e:
        print(e)
        db.rollback()

def update_collection(db,values):
    statement = 'insert into collection (manga_id,subtitle,volume,cover) values({manga_id},"{subtitle}",{volume},"{cover}")'.format_map(values)
    otherwise = 'update collection set cover="{cover}" where manga_id={manga_id} and volume={volume}'.format_map(values)
    update(db,statement,otherwise)

def update_manga(db,values):
    t = datetime.strptime(values['release_date'],'%Y-%m-%d').isocalendar()[:2]
    now = datetime.now().isocalendar()[:2]
    #print(t,now)
    if t <= now:
        cursor = db.cursor()
        cursor.execute('select volumes,released,status,complete from manga where id={manga_id}'.format_map(values))
        manga = cursor.fetchone()
        volumes,released,status,complete = manga[0],manga[1],manga[2],manga[3]=='1'
        if values['volume']>released:
            update(db,'update manga set released={volume}, cover="{cover}" where id={manga_id}'.format_map(values))
        if values['volume']==1 and status=='TBA':
            update(db,'update manga set status="Ongoing" where id={manga_id}'.format_map(values))
        if values['volume']==volumes and complete:
            update(db,'update manga set status="Complete" where id={manga_id}'.format_map(values))


def unknown(db,values):
    #title_volume,publisher,release_date,price,cover
    release_date = datetime.strptime(values['release_date'], '%d/%m/%Y') if values['release_date'] else datetime.now()
    values['release_date']=release_date.strftime('%Y-%m-%d')
    ex = ('insert into unknown (title,subtitle,publisher,release_date,price,cover) '
        'values("{title_volume}","{subtitle}","{publisher}",\'{release_date}\',{price},"{cover}")').format_map(values)
    update(db,ex)

def update(db,statement,otherwise=None):
    try:
        db.cursor().execute(statement)
        db.commit()
    except Exception as e:
        db.rollback()
        if otherwise:
            update(db,otherwise)
