import requests
import pandas
import json
import general_functions as gf

gf.getMyPrfls()

my_prfls = json.loads(open("data/myPrflsForCookieRobot.json", 'r', encoding='utf-8').read())

gf.download_csv()
df = pandas.read_csv("data/TableName - main.csv")
port = gf.port

for prfl in my_prfls:
    cookies = df.loc[df['id'] == prfl['name'], 'cookie'].values[0]
    print(prfl['name'], cookies)
    data = cookies
    resp = requests.request('POST',
                            f"http://127.0.0.1:{port}/api/v1/profile/cookies/import/webext?profileId={prfl['uuid']}",
                            data=data)
    print(resp.text)
