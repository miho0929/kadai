import requests

def get_wikipedia_summary(shachi_name):
    endpoint = "https://ja.wikipedia.org/api/rest_v1/page/summary/" + shachi_name
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return data.get('extract', '情報が見つかりませんでした。')
    else:
        return '情報が見つかりませんでした。'
