#!/bin/bash
echo "Start to migrate bkiam"
for filename in bkuser_core/bkiam/migrations/*.json; do
  echo ">>>>>>>>>>>>> migrating $filename ..."
  python bkuser_core/bkiam/migrations/do_migrate.py -f "$filename" -a ${BK_APP_CODE} -s ${BK_APP_SECRET} -t ${BK_IAM_V3_INNER_HOST}
done
