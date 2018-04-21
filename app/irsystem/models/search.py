import gc
import os
import json
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def tokenize_query(query):
    """
    Returns a dictionary with structure {term : frequency}. Also preprocesses
    the input query string using the Sklearn TfidfVectorizer.
    """
    helper = TfidfVectorizer(min_df=3, stop_words='english',  dtype=np.int16)
    tfidf_preprocessor = helper.build_preprocessor()
    tfidf_tokenizer = helper.build_tokenizer()
    with open(os.path.join(os.path.dirname(__file__), 'vocab_to_ix.json')) as f:
        #vocab_to_ix = json.load(open('vocab_to_ix.json'))
        vocab_to_ix= json.load(f)
        prepro_q = tfidf_preprocessor(query)
        q_tokens = tfidf_tokenizer(prepro_q)
        gc.collect()
        query_dict = defaultdict(int)
        for tok in q_tokens:
            tfidf_vocab_ix = vocab_to_ix.get(tok, -1)
            if tfidf_vocab_ix != -1:
                query_dict[vocab_to_ix[tok]] += 1
        gc.collect()
        f.close()
        return query_dict


def get_tfidf_of_query(query_dict):
    with open(os.path.join(os.path.dirname(__file__), 'idf_vals.npy')) as f:
        #idf_vals = np.load('idf_vals.npy')
        idf_vals= np.load(f)
        ix, tf = zip(*list(query_dict.items()))
        data = []
        for i, freq in zip(ix, tf):
            data.append(idf_vals[i] * freq)
        q_vec = csr_matrix((data, (np.zeros(len(ix)), ix)), shape=(1, len(idf_vals)))
        print(q_vec)
        f.close()
        gc.collect()
        return q_vec.astype(dtype=np.float16)

def return_relevant_doc_ixs(query_vec, num_docs=20):
    with open(os.path.join(os.path.dirname(__file__), 'tfidf_mat.npy')) as f:
        #tfidf_mat = np.load('tfidf_mat.npy')
        tfidf_mat= np.load(f)
        cos_sim = (tfidf_mat.dot(query_vec.T)).T
        gc.collect()
        most_rel = zip(cos_sim.data, cos_sim.nonzero()[1])
        most_rel.sort(key=(lambda x: x[0]), reverse=True)
        f.close()
        return most_rel[:num_docs]

def return_doc_ids(query):
    """
    Return a list of document ids of the documents relevant to the query string.
    """
    tokens = tokenize_query(query)
    if tokens == {}:
        return []
    query_vec = get_tfidf_of_query(tokens)
    rel_doc_ixs = return_relevant_doc_ixs(query_vec)
    with open(os.path.join(os.path.dirname(__file__), 'matrix_ix_to_id.json')) as f:
        docix_to_docid = json.load(f)
        doc_ids = []
        for value, ix in rel_doc_ixs:
            doc_ids.append(docix_to_docid[unicode(ix)])
        f.close()
        return doc_ids

def return_docs(query):
    """
    Return the document headline text of the relevant documents.
    """
    doc_ids = return_doc_ids(query)
    if doc_ids == []:
        return []
    with open(os.path.join(os.path.dirname(__file__), 'id_to_reu_headline.json')) as f:
        id_to_title = json.load(f)
        docs = []
        for id in doc_ids:
            docs.append((id, id_to_title[id]))
        f.close()
        return docs


# if __name__ == '__main__':
#  q = 'russia election hacking'
#  docs = return_docs(q)
#  for doc in docs:
#      print(doc)
