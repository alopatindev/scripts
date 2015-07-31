#!/bin/bash

set -e

# your username
USERNAME=""

# your id/secret from https://delicious.com/settings/developer
CLIENT_ID=""
CLIENT_SECRET=""

echo "Enter a password for user ${USERNAME}"
read -s PASSWORD

echo -n "login..."
ACCESS_TOKEN=$(wget -qO - "https://avosapi.delicious.com/api/v1/oauth/token" --post-data "client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&grant_type=credentials&username=${USERNAME}&password=${PASSWORD}" | jq '.access_token' | sed 's!"!!g')
echo " ok"

echo -n "fetching bookmarks..."
URL=$(wget -qO - "https://api.delicious.com/v1/posts/all?tag=linux" --header "Authorization: Bearer ${ACCESS_TOKEN}" \
    | sed 's!href="!\n!g' \
    | egrep --color=no '^http' \
    | sed 's!" private=.*!!g' \
    | shuf -n1)
echo " ok"

echo "you url today is ${URL}"
${BROWSER} "${URL}"
