#!/bin/sh

pip install -r REQUIREMENTS.txt

cd /home/nuwa
mkdir .subversion
echo '[global]
store-plaintext-passwords = yes
' > .subversion/servers

cd /home/nuwa/app
svn co https://code.nuwainfo.com/svn/Pandora/trunk/Containers --username Deploy --password ei0W1aUeP1pcRvJoV4X8ZC2xm
cd /home/nuwa/app/deploy

python manage.py migrate --noinput
if [[ $? -ne 0 ]] ; then
    # Unknown why (not investigate yet), MySQL will complain foreign key 
    # constrain error on first time migrate, so we migrate twice if needed.
    python manage.py migrate --noinput
fi

python manage.py search_apps
python manage.py collectstatic --noinput
python manage.py deploy configure
