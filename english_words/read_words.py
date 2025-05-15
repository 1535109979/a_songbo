from peewee import *

db = SqliteDatabase('my_database.db')
db.connect()

class WordsDBM(Model):
    id = AutoField(primary_key=True)
    english = CharField()
    chinese = CharField()
    read_times = IntegerField(default=0)
    enhance = IntegerField(default=0)

    class Meta:
        database = db  # 指定该 Model 使用的数据库
        table_name = 'words'  # 指定数据表名称


class EnglishWords(object):
    def __init__(self):
        pass

    def uodate_words(self):
        data = open('words.txt').readlines()

        for line in data:
            english = line.split('\t')[0].lower()
            chinese = line.split('\t')[-1].strip('\n')

            try:
                WordsDBM.get(WordsDBM.english == english)
            except:
                words_dbm = WordsDBM(english=english, chinese=chinese)
                words_dbm.save()
                print(english, chinese)

    def study_words(self):
        while 1:
            mode = input('<---1:遍历  2:强化  ---> 输入：')
            if mode == '1':
                self.words = WordsDBM.select().order_by(WordsDBM.read_times,WordsDBM.english)
            elif mode == '2':
                self.words = WordsDBM.select().where(WordsDBM.enhance > 0)

            while 1:
                for word in self.words:
                    print(word.english)
                    word.read_times += 1

                    choose = input('<---0:选择模式 1:不会 2:会--->输入：')
                    if choose == '1' and mode == '1':
                        word.enhance += 1
                    if choose == '2' and mode=='2':
                        word.enhance -= 1
                    if choose == '0':
                        break

                    print(word.chinese)
                    print()

                    word.save()

                mode = input('<---1:遍历  2:强化  ---> 输入：')
                if mode == '1':
                    self.words = WordsDBM.select().order_by(WordsDBM.english)
                elif mode == '2':
                    self.words = WordsDBM.select().where(WordsDBM.enhance > 0)


if __name__ == '__main__':
    # WordsDBM.create_table()

    EnglishWords().uodate_words()
    # EnglishWords().study_words()
