#!/bin/bash

while getopts 'n:p:t' opt; do
  case "$opt" in
    n  ) name="$OPTARG" ;;
    p  ) password="$OPTARG" ;;
    t  ) create_test_privileges=true;;
    \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;
    :  ) echo "Missing option argument for -$OPTARG" >&2; exit 1;;
    *  ) echo "Unimplemented option: -$option" >&2; exit 1;;
  esac
done

# include snippet to grant test_db privileges if '-t' flag used
if [ "$create_test_privileges" = true ] ; then
  read -r -d '' grant_test_privilege_snippet <<EOF
GRANT ALL PRIVILEGES ON test_${name}_db.* TO '${name}_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON test_${name}_db.* TO '${name}_admin'@'%' WITH GRANT OPTION;
EOF
else
  grant_test_privilege_snippet=''
fi

#define enroll.sql template.
cat  << EOF
CREATE DATABASE ${name}_db;

CREATE USER '${name}_admin'@'localhost' IDENTIFIED BY '${password}';
CREATE USER '${name}_admin'@'%' IDENTIFIED BY '${password}';

GRANT ALL PRIVILEGES ON ${name}_db.* TO '${name}_admin'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON ${name}_db.* TO '${name}_admin'@'%' WITH GRANT OPTION;
${grant_test_privilege_snippet}

FLUSH PRIVILEGES;
EOF