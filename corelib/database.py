# coding=utf8

import pymongo
class MongoDb(object):

    def __init__(self, host, port, user,pwd,database):
        self.host = host
        self.port = port
        self.user=user
        self.pwd=pwd
        self.db=database

    def get_db(self):
        client=pymongo.MongoClient(self.host,self.port)
        db=client[self.db]
        db.authenticate(self.user,self.pwd)
        return db
    def get_collection(self,cname):
        return self.get_db()[cname]
