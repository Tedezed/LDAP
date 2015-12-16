#!/bin/sh
ip_ldap="localhost"
port=389
base="dc=example,dc=org"

ldapsearch -x -h $ip_ldap -p $port -b $base -s sub "(&(objectClass=posixAccount) (objectClass=ldapPublicKey) (cn=$1))" | \
	sed -n '/^ /{H;d};/sshPublicKey:/x;$g;s/\n *//g;s/sshPublicKey: //gp'