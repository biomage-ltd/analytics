import pandas as pd
import numpy as np
import hashlib
import sys

from datetime import datetime, timedelta

def hash_word(w):
    return hashlib.shake_256(w.encode("utf-8")).hexdigest(length=4)


# whether to return user names & emails or not
anonymize = sys.argv[1] == "True"
output_file = sys.argv[2]


print(f"anonimize? {anonymize}")
signup_df = pd.read_csv('signup-info.csv')
login_df = pd.read_csv('login-info.csv')

df = signup_df.merge(login_df, on='email', how='left')


# drop rows without a user name because they are incomplete
df = df.dropna(thresh=5).sort_values(by="signup_date", ascending=False)

# Filter out our emails
df = df[~df["email"].str.contains('biomage.net|alexvpickering@gmail.com', regex=True)]

df['number_of_logins'] = df['number_of_logins'].fillna(0).astype(pd.Int32Dtype())

df['signup_date'] = pd.to_datetime(df['signup_date']).dt.strftime("%Y-%m-%d %H:%M:%S")
df['last_login'] = pd.to_datetime(df['last_login'])


if anonymize == True:
    df["hashed_username"] = df["name"].apply(hash_word)
    df = df[["hashed_username", "signup_date","last_login", "number_of_logins"]]


print("All users:\n")
result = df.replace({pd.NaT: '-'})
print(result.to_markdown(index=False))
result.to_markdown(output_file, index=False)

days = 7
one_week_ago =  datetime.today() - timedelta(days=days)


# Returning users statistics

returning_users = df[df['last_login'] > one_week_ago]
total_users = df.shape[0]
ratio = returning_users.shape[0] / total_users * 100
print("\n\nLast %s days: " % days)
print(" * Returning users: %.2f%% (%s/%s)" % (ratio, returning_users.shape[0], total_users))
print(" * Total logins: %s" % sum(returning_users["number_of_logins"]))
