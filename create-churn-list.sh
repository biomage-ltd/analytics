#!/bin/bash 

echo "name,email,signup_date,enabled,status" > signup-info.csv
aws cognito-idp list-users --user-pool-id ${COGNITO_PRODUCTION_POOL} | jq -r '( .Users[] | [.Attributes[2,3].Value, .UserCreateDate, .Enabled, .UserStatus] | @csv )' >> signup-info.csv


# Retrieve last login times from matomo

echo "email,last_login,number_of_logins" > login-info.csv
curl 'https://biomage.matomo.cloud/?module=API&method=Live.getLastVisitsDetails&format=JSON&idSite=1&token_auth=14cf6955bc983ada632ee549f88fb0b1' |
    jq -r '.[] | [ .userId, .lastActionDateTime, .visitCount ] |  @csv' |
    tr -d \" |
    sort -r -t, -k2,2 |
    awk -F',' '!seen[$1]++' >> login-info.csv


finalFile="users-churn-$(date '+%Y-%m-%d').csv"
python3 src/analytics.py false $finalFile 
