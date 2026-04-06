import sqlite3
conn = sqlite3.connect('autoeval.db')
c = conn.cursor()
c.execute("UPDATE classrooms SET teacher_id=93 WHERE teacher_id=1")
conn.commit()
c.execute("SELECT id, name, teacher_id FROM classrooms")
print("CLASSROOMS AFTER FIX:", c.fetchall())
conn.close()
print("Done.")
