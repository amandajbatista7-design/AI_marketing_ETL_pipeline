import pandas as pd
from openai import OpenAI

#Extract the csv file
df = pd.read_csv('data/clients.csv')

#Turn into a dictionary
data = df.to_dict(orient='records')

#Mask confidential data
def mask_card(card):
    return "****-****-****-" + card[-4:]

def mask_account(account):
    return "*" * (len(str(account)) - 1) + str(account)[-1:]

for user in data:
    user['Card'] = mask_card(user['Card'])
    user['Account'] = mask_account(str(user['Account']))
    
#Load the OpenAI key
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Function to generate a personalized message for each user
def generate_message(user):
    try:
        completion = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {
                    "role": "system",
                    "content": "You are a marketing and banking account manager speciallist."
                },
                {
                    "role": "user",
                    "content": f"Generate a message for {user['Name']} about the importance of investments and savings (200 characters max)"
                }
            ]
        )
        return completion.choices[0].message.content.strip('\"')
    except Exception as e:
        print(f"Error generating message for {user['Name']}: {e}")
        return False

for user in data:
    news = generate_message(user)
    if not news:
        print(f"Skipping user {user['Name']} due to AI failure")
        continue
    user['news'] = [{"description": news}]

#Load phase - Save results in a csv file
#Check that every user has a message
valid_rows = [u for u in data if u.get('news')]
if not valid_rows:
    print("No valid messages generated. Aborting load phase,")
    exit()

output_rows = []

for user in valid_rows:
    output_rows.append({
        "ID": user["ID"],
        "Name": user["Name"],
        "Account": user["Account"],
        "Card": user["Card"],
        "Message": user["news"][0]["description"]
    })

df_out = pd.DataFrame(output_rows)
df_out.to_csv("output/marketing_messages.csv", index=False, encoding="utf-8")
