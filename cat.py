import sqlite3
def catreturner(chatid):
 con = sqlite3.connect('statsbase.db')
 cursorObj = con.cursor()
 rows = cursorObj.execute("SELECT category from stats WHERE fromuserid = ?", (chatid,)).fetchall()
 if rows == []:
  return 'music.db'
 else:
  return list(rows)[0][0]
 con.close()
