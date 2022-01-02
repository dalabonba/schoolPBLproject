import sqlite3,random


conn = sqlite3.connect('test.db')
db = conn.cursor()

# dbCardInt=40941101
# for i in range(20):
#     dbCard=str(dbCardInt)
#     dbToken=dbCard[0:2+1]+"to"+dbCard[3:5+1]+"ken"+dbCard[6:7+1]
#     db.execute(f"insert into table1(card,token) values('{dbCard}','{dbToken}');")
#     dbCardInt+=1

# conn.commit()


# 我的token=9d3YLjEyqOLna9ZYlgBC1tUswQUvo7U5rDyfaYOlcgT

tapCardList=[]
aa=40941101
for i in range(20):
    tapCardList.append(str(aa))
    aa+=1

VtapCard=random.choice(tapCardList)
print(VtapCard)

db.execute(f'SELECT token FROM table1 where card == {VtapCard}')
for i in db.fetchone():
    print(i)


db.execute('SELECT token FROM table1 where card == 40941101')
for i in db.fetchall():
    print(i)


db.execute('SELECT token FROM table1 where card == 40941101')
for i in db.fetchmany(2):
    print(i)
