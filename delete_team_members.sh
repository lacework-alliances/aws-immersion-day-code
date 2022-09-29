#! /bin/bash
# Usage: ./delete_team_members.sh input.csv lw_account access_token
while IFS=","$'\r' read -r rec1 rec2 rec3
do
  sleep 5
  echo "Email Address: $rec1"
  echo "Name: $rec2"
  IFS=' '
  read -a namearr <<< $rec2
  echo "First Name: ${namearr[0]}"
  echo "Last Name: ${namearr[1]}"
  echo "Company: $rec3"
  search_response=$(curl -v --request POST \
          --url "https://$2.lacework.net/api/v2/TeamMembers/search" \
          --header 'Content-Type: application/json' \
          --header "Authorization: Bearer $3" \
          --header 'Org-Access: false' \
          --data '{"filters": [{"expression": "eq","field": "userName","value": "'"$rec1"'"}]}')
  data=$(jq -r '.data' <<< "${search_response}")
  data_length=$(jq length <<< "${data}")
  echo $data_length
  if [ "$data_length" -eq "0" ]; then
     continue
  fi
  record=$(jq '.[0]' <<< "${data}")
  echo $record
  userguid=$(jq -r '.[0].userGuid' <<< "${data}")
  echo $userguid
  delete_response=$(curl -v --request DELETE \
            --url "https://$2.lacework.net/api/v2/TeamMembers/$userguid" \
            --header 'Content-Type: application/json' \
            --header "Authorization: Bearer $3" \
            --header 'Org-Access: false')
  echo $delete_response
done < <(cut -d "," -f1,2,3 $1 | tail -n +2)
