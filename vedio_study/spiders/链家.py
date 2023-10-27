import requests

url = ('https://cd.lianjia.com/ershoufang/lessresult/?ids=106102805176%2C106110364658%2C106116123744%2C106114950043%'
       '2C106108182476%2C106116312056%2C106116150735%2C106112517129%2C106114358544%2C106116122715%2C106115766706%'
       '2C106111991847%2C106112103251%2C106114755078%2C106114101990%2C106116148148%2C106116090281&recommend_'
       'ext_info=%7B%22resblock_id%22%3A%5B1611057410255%5D%2C%22decoration_type%22%3A%5B2%5D%7D')

res = requests.get(url)
data = res.json().get('data').get('houseLessResult')

for h, v in data.items():
       print(v)

       # quit()
