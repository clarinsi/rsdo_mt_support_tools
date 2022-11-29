import requests
import time

# define location of the anonymisation service
ANON_URL = ""

# csv file to anonymize
TO_ANON = ""

def anonymize(sent):
    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
    }

    json_data = {
        'text': sent,
    }

    response = requests.post(ANON_URL, headers=headers, json=json_data)
    
    if len(response.json()["annotations"]) > 0:
        print(sent, response.json())
    return response.json()



with open(TO_ANON, "r") as pf:
    for line in pf:
        line = line.strip().split("\t")
        anon = anonymize(line[1])
        if len(anon["annotations"]) > 0:
            with open("ijs_anon.csv", "a") as wf:
                wf.write(str(anon) + "\n")


