#!/bin/bash

# Updates ddns.info, changeip.com and so on

USERNAME=user
PASSWORD=pass
INTERVAL=2h

for ((;;)); do
    curl -sk "https://www.changeip.com/update.asp?u=${USERNAME}&p=${PASSWORD}&cmd=update&set=1&offline=0" 2&>> /dev/null
    sleep ${INTERVAL}
done
