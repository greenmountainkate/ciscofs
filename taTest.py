# coding=utf-8
"""

"""

# calculate tf for this doc then back calculate Idf and get updated tf-idf through database
imp_words = pd.DataFrame({'docID': str(parsed_file_id), 'word': wl_no_headers})
print(imp_words.head())

print(imp_words.describe())


#make series from this doc
#append to dictionary??

#make dictionary doc as own doc
# add each doc info to dict doc and then reference dict doc in file db doc

