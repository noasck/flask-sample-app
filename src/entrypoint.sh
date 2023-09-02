#!/bin/sh

if python $PWD/src/init_db.py; then

echo "Migrations applied."
exec "$@"

fi
