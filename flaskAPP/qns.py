import shelve

class FAQ:
    # db = shelve.open('faqstorage.db','r')
    # last_id = db['FAQ_id']
    # db.close()
    # id = last_id

    def __init__(self,question,answer,date):
        # FAQ.id +=1
        #
        # db = shelve.open('faqstorage.db','c')
        #
        # last_id = FAQ.id
        # db['FAQ_id'] = last_id
        # db.close()

        self.__qns_id = 0
        self.__question = question
        self.__answer = answer
        self.__date = date


    def get_qns_id(self):
        return self.__qns_id

    def get_question(self):
        return self.__question

    def get_answer(self):
        return self.__answer

    def get_date(self):
        return self.__date

    def set_qns_id(self,qns_id):
        self.__qns_id = qns_id

    def set_question(self,question):
        self.__question = question

    def set_answer(self,answer):
        self.__answer = answer

    def set_date(self,date):
        self.__date = date

