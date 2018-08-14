#! /bin/sh
#----------------------------------------------------------------------------

cd /var/www/tester/data/projects/web-shot
. /var/www/tester/data/projects/web-shot/_venv3/bin/activate

./shot.py -u https://google.com -d phantom -i 4 -q 60 -p "./shots"

deactivate
