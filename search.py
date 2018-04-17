import gc
import json
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def tokenize_query(query):
    helper = TfidfVectorizer(min_df=3, stop_words='english',  dtype=np.int16)
    tfidf_preprocessor = helper.build_preprocessor()
    tfidf_tokenizer = helper.build_tokenizer()
    vocab_to_ix = json.load(open('vocab_to_ix.json'))
    prepro_q = tfidf_preprocessor(query)
    q_tokens = tfidf_tokenizer(prepro_q)
    gc.collect()
    query_dict = defaultdict(int)
    for tok in q_tokens:
        tfidf_vocab_ix = vocab_to_ix.get(tok, -1)
        if tfidf_vocab_ix != -1:
            query_dict[vocab_to_ix[tok]] += 1
    gc.collect()
    return query_dict


def get_tfidf_of_query(query_dict):
    idf_vals = np.load('idf_vals.npy')
    ix, tf = zip(*list(query_dict.items()))
    data = []
    for i, freq in zip(ix, tf):
        data.append(idf_vals[i] * freq)
    q_vec = csr_matrix((data, (np.zeros(len(ix)), ix)), shape=(1, len(idf_vals)))
    print(q_vec)
    gc.collect()
    return q_vec.astype(dtype=np.float16)

def return_relevant_doc_ixs(query_vec, num_docs=20):
    tfidf_mat = np.load('tfidf_mat.npy')
    cos_sim = (tfidf_mat.dot(query_vec.T)).T
    gc.collect()
    most_rel = zip(cos_sim.data, cos_sim.nonzero()[1])
    most_rel.sort(key=(lambda x: x[0]), reverse=True)
    return most_rel[:num_docs]

def return_doc_ids(query):
    tokens = tokenize_query(query)
    query_vec = get_tfidf_of_query(tokens)
    rel_doc_ixs = return_relevant_doc_ixs(query_vec)
    docix_to_docid = json.load(open('matrix_ix_to_id.json'))
    doc_ids = []
    for value, ix in rel_doc_ixs:
        doc_ids.append(docix_to_docid[unicode(ix)])
    return doc_ids

def return_docs(query):
    doc_ids = return_doc_ids(query)
    id_to_title = json.load(open('id_to_reu_headline.json'))
    docs = []
    for id in doc_ids:
        docs.append((id, id_to_title[id]))
    return docs


# if __name__ == '__main__':
#     q = 'china threatens war against japan'
#     docs = return_docs(q)
#     print(docs)
