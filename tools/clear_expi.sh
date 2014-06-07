#!/bin/bash

# Here is the upload hold path
UPLOADPATH=$(dirname $(dirname $(readlink -f $0)))/upload
DB_USER="infile"
DB_PASSWD="infile"
DB_NAME="infile"

day=$(date +"%-d")
rm -rf "$UPLOADPATH/$day"

echo "DELETE FROM res WHERE etime < CURRENT_TIMESTAMP() ; DELETE FROM file WHERE etime < CURRENT_TIMESTAMP();" | mysql -u "$DB_USER" -p"$DB_PASSWD" "$DB_NAME"
