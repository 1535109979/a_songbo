from collections import Counter

cover_count = Counter([1,2,3,4,5,3,4])

co = ''
for k,v in cover_count.items():
    co += str(k) + ':' + str(v) + ','

print(co)


