# coding=utf-8

def make_word_freq_dict(pf_collection):

    keywords = {
        "keyword_list_format":[('doc_id', 'word_freq')],
    }

    return pf_collection.insert_one(keywords).inserted_id

def add_keyword(pf_collection, dict_id, doc_id, tup):
    keyword, doc_freq = tup
    print("Keyword: ", keyword)
    print("Doc_freq: ", doc_freq)
    print("Type of Doc_freq: ", type(doc_freq))
    try:
        pf_collection.find_one_and_update(
            {"_id": dict_id},  # query filter
            {
                "$addToSet": {
                    keyword: (doc_id, int(doc_freq))
                }
            },  # update to apply
            upsert=True
        )
    except Exception as e:
        #TODO log exception
        print("Error adding \"{0}\" to dictionary: ".format(keyword), e)
        pass


