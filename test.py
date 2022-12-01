import jedi
code = '''\
x = 3
if 1 == 2:
    x = 4
else:
    del x'''
script = jedi.Script(code)
rns = script.get_references(5, 8)
ret = script.rename(5, 8, new_name='fuck')
# ret.apply()
v = list(ret.get_changed_files().values())
print(
    dir(ret),
    dir(v[0])
    )

print(v[0].get_new_code())