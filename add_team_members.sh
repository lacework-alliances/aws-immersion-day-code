#! /bin/bash
while IFS="," read -r rec1 rec2 rec3
do
  sleep 30
  echo "Email Address: $rec1"
  echo "Name: $rec2"
  IFS=' '
  read -a namearr <<< $rec2
  echo "First Name: ${namearr[0]}"
  echo "Last Name: ${namearr[1]}"
  echo "Company: $rec3"
  curl -v --location --request POST "https://$2.lacework.net/api/v2/TeamMembers" \
          --header 'Content-Type: application/json' \
          --header "Authorization: Bearer $3" \
          --header 'Org-Access: false' \
          --data-raw '{
          "props": {
          "firstName": "'"${namearr[0]}"'",
          "lastName": "'"${namearr[1]}"'",
          "company": "'"$rec3"'",
          "accountAdmin": false
          },
          "userEnabled": "1",
          "userName": "'"$rec1"'"
          }' 
done < <(cut -d "," -f1,6,8 $1 | tail -n +2)