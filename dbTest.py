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


# 我的token=AXXMRm1rdxj69E3IWDrKBnatzhhPYrgmvL8G1ikehnV

tapCardList=[]
aa=40941101
for i in range(20):
    tapCardList.append(str(aa))
    aa+=1

VtapCard=random.choice(tapCardList)
print(VtapCard)

for row in db.execute(f'SELECT token FROM table1 where card == {VtapCard}'):
    print(row)