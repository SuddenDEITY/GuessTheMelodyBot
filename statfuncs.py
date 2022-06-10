import sqlite3
import schedule
import time
import random
from random import shuffle
from SQLighter import SQLighter
import config
import utils
from threading import Thread

def optionsforvic(right_answer, wrong_answers):
    all_answers = '{},{}'.format(right_answer, wrong_answers)
    # Создаем лист (массив) и записываем в него все элементы
    list_items = []
    for item in all_answers.split(','):
        list_items.append(item)
    # Хорошенько перемешаем все элементы
    shuffle(list_items)
    return list_items


def getrandomsong(base):
 db_worker = SQLighter(base)
 row = db_worker.select_single(random.randint(1, db_worker.count_rows()))
 db_worker.close()
 return row


def dailydeleter():
  con = sqlite3.connect('statsbase.db')
  cursorObj = con.cursor()
  cursorObj.execute("DELETE FROM dailystats")
  con.commit()
  con.close()

def savecategory(category , chatid):
    con = sqlite3.connect('statsbase.db')
    cursorObj = con.cursor()
    cursorObj.execute("UPDATE stats SET category = ? where fromuserid = ?", [category,chatid])
    con.commit()
    con.close()


def getinfacts():
 con = sqlite3.connect('ifacts.db')
 cursorObj = con.cursor()
 rows = cursorObj.execute("SELECT * from intfacts").fetchall()
 return list(rows)
 con.close()


def statsreturner(chatid):
 con = sqlite3.connect('statsbase.db')
 cursorObj = con.cursor()
 mainrow = cursorObj.execute("SELECT username , score FROM stats WHERE fromuserid = ? ORDER BY score DESC LIMIT 10",(chatid,)).fetchall()
 rows = cursorObj.execute("SELECT username , score FROM stats ORDER BY score DESC LIMIT 10").fetchall()
 return list(mainrow + rows)
 con.close()

def dailystatsreturner(chatid):
  con = sqlite3.connect('statsbase.db')
  cursorObj = con.cursor()
  mainrow = cursorObj.execute("SELECT username , score FROM dailystats WHERE fromuserid = ? ORDER BY score DESC LIMIT 10",(chatid,)).fetchall()
  rows = cursorObj.execute("SELECT username , score FROM dailystats ORDER BY score DESC LIMIT 10").fetchall()
  return list(mainrow + rows)
  con.close()

def currentansreturner(chatid):
  con = sqlite3.connect('statsbase.db')
  cursorObj = con.cursor()
  mainrow = cursorObj.execute("SELECT currentans FROM stats WHERE fromuserid = ?",(chatid,)).fetchone()
  return list(mainrow)
  con.close()


def nickchanger(chatid,name):
    con = sqlite3.connect('statsbase.db')
    cursorObj = con.cursor()
    cursorObj.execute("UPDATE dailystats SET username = ? WHERE fromuserid = ?", [name, chatid])
    cursorObj.execute("UPDATE stats SET username = ? WHERE fromuserid = ?", [name, chatid])
    con.commit()
    con.close()

def scoreupdater(chatid,userid,bl):
 con = sqlite3.connect('statsbase.db')
 cursorObj = con.cursor()
 if not bool(cursorObj.execute(f'SELECT * FROM stats WHERE fromuserid={chatid};').fetchall()):
   if not userid:
    cursorObj.execute("INSERT INTO stats (fromuserid, score, statpl ,statmn, k ,username , currentans) VALUES(?,0,0,0,0,?,0)", [chatid, chatid])
   else:
    cursorObj.execute("INSERT INTO stats (fromuserid, score, statpl ,statmn, k ,username , currentans) VALUES(?,0,0,0,0,?,0)",[chatid, userid])
 usrnm = cursorObj.execute(f'SELECT username FROM stats WHERE fromuserid={chatid};').fetchone()
 if not bool(cursorObj.execute(f'SELECT * FROM stats WHERE fromuserid={chatid};').fetchall()):
    cursorObj.execute("INSERT INTO stats (fromuserid, score, statpl ,statmn, k , username, currentans, category) VALUES(?,0,0,0,0,0,?,?)", [chatid, usrnm[0],'music.db'])
 if bl == True: {
 cursorObj.execute("UPDATE stats SET currentans = currentans +  1 where fromuserid = ?", [chatid]),
 cursorObj.execute("UPDATE stats SET score = score +  25 + k*k where fromuserid = ?",  [chatid]),
 cursorObj.execute("UPDATE stats SET statpl = statpl + 1 where fromuserid = ?" , [chatid]),
 cursorObj.execute("UPDATE stats SET k = k + 1 where fromuserid = ?", [chatid]),
 cursorObj.execute("UPDATE dailystats SET score = score +  25 + k*k where fromuserid = ?", [chatid]),
 cursorObj.execute("UPDATE dailystats SET statpl = statpl + 1 where fromuserid = ?", [chatid]),
 cursorObj.execute("UPDATE dailystats SET k = k + 1 where fromuserid = ?", [chatid])}
 else:
  cursorObj.execute("UPDATE stats SET currentans = currentans +  1 where fromuserid = ?", [chatid]),
  cursorObj.execute("UPDATE stats SET statmn = statmn + 1 where fromuserid = ?", [chatid]),
  cursorObj.execute("UPDATE stats SET k = 0 where fromuserid = ?", [chatid])
  cursorObj.execute("UPDATE dailystats SET statmn = statmn + 1 where fromuserid = ?", [chatid]),
  cursorObj.execute("UPDATE dailystats SET k = 0 where fromuserid = ?", [chatid])
  try:
   cursorObj.execute("UPDATE stats SET score = score - 25 where fromuserid = ?", [chatid])
  except:
   cursorObj.execute("UPDATE stats SET score = 0 where fromuserid = ?", [chatid])
  try:
   cursorObj.execute("UPDATE dailystats SET score = score - 25 where fromuserid = ?", [chatid])
  except:
   cursorObj.execute("UPDATE dailystats SET score = 0 where fromuserid = ?", [chatid])

 if list(cursorObj.execute(f"SELECT currentans FROM stats WHERE fromuserid={chatid};").fetchone())[0] > 10:
  cursorObj.execute("UPDATE stats SET currentans = 0 where fromuserid = ?", [chatid])
 rows = cursorObj.execute(f"SELECT * FROM stats WHERE fromuserid={chatid};").fetchall()
 con.commit()
 con.close()
 for row in rows:
  pass
 return list(row)


def resetstats(chatid):
 con = sqlite3.connect('statsbase.db')
 cursorObj = con.cursor()
 cursorObj.execute("DELETE FROM stats WHERE fromuserid = ?", [chatid])
 con.commit()
 con.close()

def run_scheduled_jobs():
 schedule.every().day.at("23:59").do(dailydeleter)
 while True:
  schedule.run_pending()
  time.sleep(55)



my_thread = Thread(target=run_scheduled_jobs)
my_thread.start()




