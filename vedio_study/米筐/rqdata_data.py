import pandas as pd
import rqdatac
rqdatac.init(username='15605173271', password='songbo1997')

print(rqdatac.info())

# data = rqdatac.get_price('000001.XSHE', start_date=20150101, end_date="2015-02-01")
# print(data)

bytes_dict = rqdatac.user.get_quota()
print(bytes_dict)
used = bytes_dict['bytes_used'] / bytes_dict['bytes_limit']
print(used)
quit()

# dominant = rqdatac.futures.get_dominant('RB', '20230801')
# print(dominant)

# data = rqdatac.get_price('603030.XSHG',
#                          start_date='2023-10-01',
#                          end_date='2023-11-02',
#                          frequency='1m',
#                          )
# print(data)

# data.to_csv('data/603030.csv')

data = rqdatac.futures.get_dominant('AP',
                                    start_date='2023-10-01',
                                    end_date='2023-11-02',
                                    rule=1,
                                    rank=2)
print(data)
