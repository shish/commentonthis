#!/bin/bash

export PGUSER=cot
export PGPASSWORD=c0t00t13
export PGHOST=localhost
export PGOPTIONS=--client-min-messages=warning


sudo -u postgres pg_dump cot > ../backups/cot.`date +%s`.sql || true

sudo -u postgres dropdb cot || true
sudo -u postgres dropuser cot || true

echo "create user cot with password '${PGPASSWORD}';" | sudo -u postgres psql -q
sudo -u postgres createdb -E utf8 -O cot cot

psql -d cot -f schema.sql
psql -d cot -f testdata.sql
