from a_songbo.vn.data.process_sqlite import SqliteDatabaseManage, Minprice


min_price = {'rb2311': 3333, 'rb2310':3444}

save_list = []
for instrument, value in min_price.items():
    save_list.append({
        'instrument': instrument,
        'price': value,
    })
with SqliteDatabaseManage().get_connect().atomic():
    Minprice.insert_many(save_list).execute()

