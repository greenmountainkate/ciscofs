# coding=utf-8
"""


"""
import time
from pymongo import ReturnDocument, UpdateMany
from pymongo.errors import BulkWriteError


def upsert_keyword_and_update_lists(pf_db, error_db, doc_id, tup):
    """

    :param error_db:
    :param pf_db:
    :param doc_id:
    :param tup:
    :return:
    """
    keyword, doc_freq = tup
    doc_id_and_freq = (doc_id, int(doc_freq))
    keywords = "keyWords"
    key = keywords + '.' + keyword

    try:
        pf_db.find_one_and_update(
            {"_id": doc_id},  # query filter
            {
                "$set": {
                    key: [doc_id_and_freq]
                }
            },  # update to apply
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        current_doc_list = pf_db.find_one(
            {"_id": {"$ne": doc_id}, key: {'$exists': True}},  # not most recent upsert from current html file
            {key: 1, "_id": False} # projection returns keyWords field as dictionary without document id
        )

        if current_doc_list is None:  # this was the first time keyword was added to any doc, done
            return

        doc_list = current_doc_list.get('keyWords').get(keyword) #retrieve keyword list of document/frequency pairs
        doc_list.append(doc_id_and_freq) #add current doc_id and keyword frequency to this list

        # now update all occurrences of this keyword in any previous html file db documents with new list
        #set update request to use with bulk_write for efficiency
        request = [UpdateMany(
            {key: {'$exists': True}},
            {
                "$set": {
                    key: doc_list
                }
            }
        )]
        try:
            pf_db.bulk_write(request)
        except BulkWriteError as e:
            timestamp = time.strftime('%x %X %Z')
            error_log = {
                'Time': timestamp,
                'ErrorMessage': [
                    f"Error updating previous files with keyword: {keyword} from file_id: {doc_id} Error: {e}"
                ]
            }
            # write to error collection
            error_db.insert_one(error_log)
            pass

    except Exception as e:
        timestamp = time.strftime('%x %X %Z')
        error_log = {
            'Time': timestamp,
            'ErrorMessage': [
                f"Error adding \"{keyword}\" to file_id \"{doc_id}\" db doc. Error: {e}"
            ]
        }
        # write to error collection
        error_db.insert_one(error_log)
        pass
