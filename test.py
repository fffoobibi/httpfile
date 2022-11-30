import jedi
code = '''\
x = 3
if 1 == 2:
    x = 4
else:
    del x'''
script = jedi.Script(code)
rns = script.get_references(5, 8)
print(rns)