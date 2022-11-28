import jsontree
import datetime
data = jsontree.jsontree()
data.username = 'doug'
data.meta.date = datetime.datetime.now()
data.somethingelse = [1,2,3]

data['username'] == 'doug'
jsontree.mapped_jsontree()
ser = jsontree.dumps(data)
backagain = jsontree.loads(ser)
cloned = jsontree.clone(data)
print(cloned)