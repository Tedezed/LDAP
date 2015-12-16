#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://github.com/Tedezed

import os
import getpass
from json import loads

file_name = 'humans.js'
name_value = 'humanos'

passwd = getpass.getpass('Contraseña del usuario admin LDAP: ')

# JSON
f = open(file_name,'r')
content = f.read()
f.close()
json_humans = loads(content)
list_humans = json_humans[name_value]

for i in list_humans:
	cn = remover_acentos(str(i['nombre'].encode('utf8')))
	print cn
	com = 'ldapdelete -x -D "cn=admin,dc=example,dc=org" -h localhost -p 389 -w %s "cn=%s,dc=example,dc=org"' % (passwd, cn)
	os.system(com)