# Poblar LDAP con JSON

##### Poblar_LDAP.py -> Para añadir los usuarios del fichero humans.js.
##### Eliminar_LDAP.py -> Para eliminar los usuarios del fichero humans.js.
##### humans.json -> Usuarios que vamos a añadir a nuestro LDAP.
##### public_key.sh -> Script para consultar la clave publica del usuario.

Añadimos el esquema openssh-lpk, para poder incluir claves públicas ssh en un directorio LDAP:
```
nano openssh-lpk.ldif
```

```
dn: cn=openssh-lpk,cn=schema,cn=config
objectClass: olcSchemaConfig
cn: openssh-lpk
olcAttributeTypes: ( 1.3.6.1.4.1.24552.500.1.1.1.13 NAME 'sshPublicKey'
  DESC 'MANDATORY: OpenSSH Public key'
  EQUALITY octetStringMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.40 )
olcObjectClasses: ( 1.3.6.1.4.1.24552.500.1.1.2.0 NAME 'ldapPublicKey' SUP top AUXILIARY
  DESC 'MANDATORY: OpenSSH LPK objectclass'
  MAY ( sshPublicKey $ uid )
  )
```

```
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f openssh-lpk.ldif
```

Creamos un virtualenv:
```
cd .virtualenv
virtualenv ldap
cd ldap
```

Activamos el virtualenv anterior:
```
source bin/activate
```

Instalamos python-ldap:
```
pip install python-ldap
```

Instalamos libnss-ldapd para la autenticación de usuario en LDAP:
```
apt-get install libnss-ldapd ldap-utils
```

Configuración durante la instalación:

Conexión:
```
ldap://localhost:389/
```

Base de nuestro árbol:
```
dc=example,dc=org
```
Configuración de NSS con LDAP:
```
passwd
group
```

Configuramos /etc/pam.d/common-session
```
session [success=ok default=ignore]     pam_ldap.so minimum_uid=2000
```

Configuramos mkhomedir en pam-configs:
```
nano /usr/share/pam-configs/mkhomedir
```

```
Name: Create home directory during login
Default: yes
Priority: 900
Session-Type: Additional
Session:
        required        pam_mkhomedir.so umask=0022 skel=/etc/skel
```

Actualizamos pam con:
```
sudo pam-auth-update
```

Creamos nuestro script para obtener la clave publica del usuario del ldap:
```
nano /usr/bin/public_key.sh
```

```
#!/bin/sh
ip_ldap="localhost"
port=389
base="dc=example,dc=org"

ldapsearch -x -h $ip_ldap -p $port -b $base -s sub "(&(objectClass=posixAccount) (objectClass=ldapPublicKey) (cn=$1))" | \
	sed -n '/^ /{H;d};/sshPublicKey:/x;$g;s/\n *//g;s/sshPublicKey: //gp'
```

Comprobamos su funcionamiento de script:
```
(ldap)root@debian:/home/debian/ldap/python# sh /usr/bin/public_key.sh morrigan.rigan
ssh-rsa ssh-rsa Clave_RSA_Publica
```

Editamos y especificamos la ruta del script:
```
nano /etc/ssh/sshd_config
```

```
# LDAP SSH
AuthorizedKeysCommand /usr/bin/public_key.sh
AuthorizedKeysCommandUser root
```

Reiniciamos:
```
service sshd restart
```
