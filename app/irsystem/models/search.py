import gc
import os
import json
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix, load_npz
from sklearn.feature_extraction.text import TfidfVectorizer



BASE = os.path.abspath(__file__).replace("search.py", "")

def tokenize_query(query, ds):
    """
    Returns a dictionary with structure {term : frequency}. Also preprocesses
    the input query string using the Sklearn TfidfVectorizer.
    """
    helper = TfidfVectorizer(min_df=3, stop_words='english',  dtype=np.int16)
    tfidf_preprocessor = helper.build_preprocessor()
    tfidf_tokenizer = helper.build_tokenizer()
    with open(os.path.join(BASE, os.path.join(ds, 'vocab_to_ix.json'))) as f:
    #with open(os.path.join(ds, 'vocab_to_ix.json')) as f:
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


def get_tfidf_of_query(query_dict, ds):
    """
    Create query vector
    """
    with open(os.path.join(BASE, os.path.join(ds, 'idf_vals.npy'))) as f:
    #with open(os.path.join(ds, 'idf_vals.npy')) as f:
        idf_vals= np.load(f)
        ix, tf = zip(*list(query_dict.items()))
        data = []
        for i, freq in zip(ix, tf):
            data.append(idf_vals[i] * freq)
        q_vec = csr_matrix((data, (np.zeros(len(ix)), ix)), shape=(1, len(idf_vals)))
        f.close()
        gc.collect()
        return q_vec.astype(dtype=np.float16)


def return_relevant_red_doc_ixs(query_vec, ds, t):
    """
    Return relevant document ids that pass threshold t
    """
    with open(os.path.join(BASE, os.path.join(ds, 'tfidf_mat.npz'))) as f:
    #with open(os.path.join(ds, 'tfidf_mat.npz')) as f:
        tfidf_mat= load_npz(f)
        cos_sim = (tfidf_mat.dot(query_vec.T)).T
        gc.collect()
        most_rel = zip(cos_sim.data, cos_sim.nonzero()[1])
        most_rel = [(val, ix) for val, ix in most_rel if val > t]
        f.close()
        return most_rel


def return_red_ixs(query, ds, t=5):
    tokens = tokenize_query(query, ds)
    if tokens == {}:
        return []
    query_vec = get_tfidf_of_query(tokens, ds)
    rel_doc_ixs = return_relevant_red_doc_ixs(query_vec, ds, t)
    return rel_doc_ixs


def return_reu_ids(query, ds, t=5):
    tokens = tokenize_query(query, ds)
    if tokens == {}:
        return []
    query_vec = get_tfidf_of_query(tokens, ds)
    rel_doc_ixs = return_relevant_reu_doc_ids(query_vec, ds, t)
    return rel_doc_ixs


def return_relevant_reu_doc_ids(query_vec, ds, t):
    with open(os.path.join(BASE, os.path.join(ds, 'tfidf_mat.npz'))) as f:
    #with open(os.path.join(ds, 'tfidf_mat.npz')) as f:
        tfidf_mat= load_npz(f)
        cos_sim = (tfidf_mat.dot(query_vec.T)).T
        gc.collect()
        most_rel = zip(cos_sim.data, cos_sim.nonzero()[1])
        with open(os.path.join(BASE, os.path.join(ds, 'matrix_ix_to_val.json'))) as f2:
        #with open(os.path.join(ds, 'matrix_ix_to_val.json')) as f2:
            ix_to_val = json.load(f2)
            most_rel = [(val, ix_to_val[str(ix)].encode("utf8")) for val, ix in most_rel if val > t]
        f.close()
        f2.close()
        return most_rel


def reu_id_decomp(reuters_ids):
    """
    Return a tuple where the first value is a
    dictionary {reuter_id: cossim score} and the
    second value is a set of all relevant reuter ids
    """
    d = {}
    reu_ids = set()
    for val, reu_id in reuters_ids:
        d[reu_id] = val
        reu_ids.add(reu_id)
    return (d, reu_ids)


def complete_search(query):
    """
    Given a user query, return large cards where
    reddit links to reuters headlines as well as
    small cards that contain reuters headlines 
    (That had no reddit match)
    """
    reddit_ixs = return_red_ixs(query, 'reddit', t=3)
    reuters_ids = set(return_reu_ids(query, 'reuters', t=3))
    reu_id_dict, reu_id_set = reu_id_decomp(reuters_ids)
    cards = []
    with open(os.path.join(BASE, os.path.join('reddit', 'matrix_ix_to_val.json'))) as f1:
    #with open(os.path.join('reddit', 'matrix_ix_to_val.json')) as f1:
        with open(os.path.join(BASE, os.path.join('reuters', 'date_to_id.json'))) as f2:
        #with open(os.path.join('reuters', 'date_to_id.json')) as f2:
            with open(os.path.join(BASE, os.path.join('reuters', 'id_to_reu_headline.json'))) as f3:
            #with open(os.path.join('reuters', 'id_to_reu_headline.json')) as f3:
                reddit_ix_to_val = json.load(f1)
                date_to_id = json.load(f2)
                id_to_headline = json.load(f3)
                #Iterate over reddit tuples (i.e. big cards)
                for val, ix in reddit_ixs:
                    tup = reddit_ix_to_val[str(ix)]
                    tup_ixs = date_to_id.get(str(tup[0]), -1)
                    #Reddit has date, but reuters does not
                    if tup_ixs == -1:
                        #print("IN -1")
                        card = (str(tup[0]), tup[1].encode("utf8"), tup[2], tup[3], tup[4].encode("utf8"), [])
                        cards.append(card)
                        continue
                    tup_ixs = set([date.encode("utf8") for date in tup_ixs])
                    inter = reu_id_set.intersection(tup_ixs)
                    inter = [id_to_headline[reu_id].encode("utf8") for reu_id in inter]
                    card = (str(tup[0]), tup[1].encode("utf8"), tup[2], tup[3], tup[4].encode("utf8"), inter)
                    reu_id_set -= set(tup_ixs)
                    cards.append(card)
            
                #Iterate over reuter ixs not covered through reddit (i.e. small cards)
                for reu_id in reu_id_set:
                    cossim = reu_id_dict[reu_id]
                    if cossim > 5.5:
                        date = str(reu_id)[:8]
                        headline = id_to_headline[str(reu_id)]
                        card = (date, headline.encode("utf8"))
                        cards.append(card)
    f1.close()
    f2.close()
    f3.close()
    return cards

#if __name__ == '__main__':
#  q = 'russia election hacking'
#  docs = complete_search(q)
#  for doc in docs:
#      print(doc)
