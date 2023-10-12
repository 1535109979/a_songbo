import akshare as ak

option_sina_hist_df = ak.option_sse_daily_sina(symbol='cu2311P56000')
print(option_sina_hist_df)

url = ('http://futsseapi.eastmoney.com/list/option/151?callback=aaa_callback&orderBy=zdf&sort=desc&pageSize=20&page'
       'Index=0&callbackName=aaa_callback&token=58b2fa8f54638b60b87d69b31969089c&'
       'field=dm%2Csc%2Cname%2Cp%2Czsjd%2Czde%2Czdf%2Cf152%2Cvol%2Ccje%2Cccl%2Cxqj%2Csyr%2Crz%2Czjsj%2Co&'
       'blockName=callback&_=1696751221180')
