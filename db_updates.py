# coding=utf-8
"""
Module manages the upsert (insert if new, update otherwise) of a new keyword into the keyWords field of an html
file's database document.  The keyWords field holds a dictionary where the key for each entry is a particular keyword
and the value is a list of tuples.  Each tuple contains a document's unique id and the frequency with which that
keyword is found in that particular html file.  After the upsert, the entire collection of documents is checked for this
keyword and lists updated if necessary to include current doc, using bulk_write for efficiency.

"""
import time
from pymongo import ReturnDocument, UpdateMany
from pymongo.errors import BulkWriteError


def upsert_keyword_and_update_lists(pf_db, error_db, doc_id, tup):
    """
    This function creates the document id, word frequency tuple for this html file and then checks
    to see if any previous document in the database also contains this keyword.  If so, the list is pulled from a
    previous document, the tuple for this document/frequency is added to the list, and then a request for update which
    sets the updated list as the value for this keyword is bulk written to all documents in the database containing
    this keyword, including the document for the html file currently being processed.

    :param error_db: database that holds error log messages
    :param pf_db: database that holds parsed html file documents
    :param doc_id: ObjectId that holds the unique id for the current document
    :param tup: tuple that holds the keyword and the frequency count for that keyword in the current html file
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
            {key: 1, "_id": False}  # projection returns keyWords field as dictionary without document id
        )

        if current_doc_list is None:  # this was the first time keyword was added to any doc, done
            return

        doc_list = current_doc_list.get('keyWords').get(keyword)  # retrieve keyword list of document/frequency pairs
        doc_list.append(doc_id_and_freq)  # add current doc_id and keyword frequency to this list

        # now update all occurrences of this keyword in any previous html file db documents with new list
        # set update request to use with bulk_write for efficiency
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
