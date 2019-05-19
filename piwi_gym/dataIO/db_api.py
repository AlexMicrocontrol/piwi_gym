from pymongo import MongoClient
from pymongo import errors


class MongoCustomAPI(object):
    def __init__(self, db_name, collection_name,  port=27017):
        self.batch_idx = 1
        self._conn = MongoClient('localhost', port=port, maxPoolSize=4)
        self._db = self._conn[db_name]
        self._collection = self._db[collection_name]

    def insert(self, document):
        self._collection.insert_one(document)

    def find_all(self):
        cursor = self._collection.find({})
        return cursor

    def get_next_sequenze(self, sequenze_len=50):
        cursor = self._collection.find().skip(self.batch_idx).limit(sequenze_len)
        self.batch_idx += 1
        return cursor

    def reset_idx(self):
        self.batch_idx = 1

    def get_last_N(self, N):
        return self._collection.find({}).skip(self._collection.count() - N)

    def drop_collection(self):
        self._collection.drop({})

#mongo = MongoCustomAPI('trade_logger', 'btc_eth')
#print(mongo.find_all())
