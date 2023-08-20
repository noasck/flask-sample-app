#!/bin/sh

sleep 0.1
yoyo $ACCOUNTING_APP_YOYO_COMMAND -c "/usr/src/yoyo.ini" --batch --database "postgresql+psycopg://\
$ACCOUNTING_APP_POSTGRES_USER:$ACCOUNTING_APP_POSTGRES_PASSWORD\
@$ACCOUNTING_APP_POSTGRES_HOST:$ACCOUNTING_APP_POSTGRES_PORT\
/$ACCOUNTING_APP_POSTGRES_DB"

echo "Migrations applied."

exec "$@"