import gc
import os
import json
import numpy as np
import sys
from collections import defaultdict
from scipy.sparse import csr_matrix, load_npz
from query_expansion import expand_query
from sklearn.feature_extraction.text import TfidfVectorizer

BASE = "/app/app/irsystem/models/"

def tokenize_query(query, ds):
    """
    Returns a dictionary with structure {term : frequency}. Also preprocesses
    the input query string using the Sklearn TfidfVectorizer.
    """
    print >> sys.stderr, "tokenize_query"
    helper = TfidfVectorizer(min_df=3, stop_words='english',  dtype=np.int16)
    tfidf_preprocessor = helper.build_preprocessor()
    tfidf_tokenizer = helper.build_tokenizer()
    with open(os.path.join(BASE, os.path.join(ds, 'vocab_to_ix.json'))) as f:
        vocab_to_ix= json.load(f)
        prepro_q = tfidf_preprocessor(query)
        q_tokens = tfidf_tokenizer(prepro_q)
        gc.collect()
        query_dict_ix = defaultdict(int)
        query_dict_term = defaultdict(int)
        for tok in q_tokens:
            tfidf_vocab_ix = vocab_to_ix.get(tok, -1)
            if tfidf_vocab_ix != -1:
                query_dict_ix[vocab_to_ix[tok]] += 1
                query_dict_term[tok] += 1
        expanded_query_dict = expand_query(query_dict_ix, query_dict_term, f)
        gc.collect()
        f.close()
        return expanded_query_dict


def get_tfidf_of_query(query_dict, ds):
    """
    Create query vector
    """
    print >> sys.stderr, "get_tfidf_of_query"
    with open(os.path.join(BASE,os.path.join(ds, 'idf_vals.npy'))) as f:
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
    print >> sys.stderr, "return_relevant_red_doc_ixs"
    with open(os.path.join(BASE, os.path.join(ds, 'tfidf_mat.npz'))) as f:
        tfidf_mat= load_npz(f)
        cos_sim = (tfidf_mat.dot(query_vec.T)).T
        gc.collect()
        most_rel = zip(cos_sim.data, cos_sim.nonzero()[1])
        most_rel = [(val, ix) for val, ix in most_rel if val > t]
        f.close()
        return most_rel


def return_red_ixs(query, ds, t=5):
    print >> sys.stderr, "return_red_ixs"
    tokens = tokenize_query(query, ds)
    if tokens == {}:
        return []
    query_vec = get_tfidf_of_query(tokens, ds)
    rel_doc_ixs = return_relevant_red_doc_ixs(query_vec, ds, t)
    return rel_doc_ixs


def return_reu_ids(query, ds, t=5):
    print >> sys.stderr, "return_reu_ids"
    tokens = tokenize_query(query, ds)
    if tokens == {}:
        return []
    query_vec = get_tfidf_of_query(tokens, ds)
    rel_doc_ixs = return_relevant_reu_doc_ids(query_vec, ds, t)
    return rel_doc_ixs


def return_relevant_reu_doc_ids(query_vec, ds, t):
    print >> sys.stderr, "return_relevant_reu_doc_ids"
    with open(os.path.join(BASE, os.path.join(ds, 'tfidf_mat.npz'))) as f:
        tfidf_mat= load_npz(f)
        cos_sim = (tfidf_mat.dot(query_vec.T)).T
        gc.collect()
        most_rel = zip(cos_sim.data, cos_sim.nonzero()[1])
        with open(os.path.join(BASE, os.path.join(ds, 'matrix_ix_to_val.json'))) as f2:
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
    print >> sys.stderr, "reu_id_decomp"
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
    print >> sys.stderr, "complete search start"
    reddit_ixs = return_red_ixs(query, 'reddit', t=3)
    reuters_ids = set(return_reu_ids(query, 'reuters', t=3))
    print >> sys.stderr, "size of set: " + str(len(reuters_ids))
    reu_id_dict, reu_id_set = reu_id_decomp(reuters_ids)
    print >> sys.stderr, "decomped"
    cards = []
    with open(os.path.join(BASE, os.path.join('reddit', 'matrix_ix_to_val.json'))) as f1:
        with open(os.path.join(BASE, os.path.join('reuters', 'date_to_id.json'))) as f2:
            print >> sys.stderr, "opened files"
            reddit_ix_to_val = json.load(f1)
            date_to_id = json.load(f2)

            print >> sys.stderr, "loaded files"
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
                card = (str(tup[0]), tup[1].encode("utf8"), tup[2], tup[3], tup[4].encode("utf8"), inter)
                reu_id_set -= set(tup_ixs)
                cards.append(card)
            f1.close()
            f2.close()
            #Iterate over reuter ixs not covered through reddit (i.e. small cards)
            for reu_id in reu_id_set:
                cossim = reu_id_dict[reu_id]
                if cossim > 5.5:
                    date = str(reu_id)[:8]
                    card = (date, reu_id)
                    cards.append(card)
    gc.collect()

    with open(os.path.join(BASE, os.path.join('reuters', 'id_to_reu_headline.csv'))) as f3:
        print >> sys.stderr, "tryna load f3"
        id_to_reu= pandas.read_csv(f3)
        print >> sys.stderr, "loaded f3"




        f3.close()
    return cards

if __name__ == '__main__':
    q = 'russia election hacking'
    docs = complete_search(q)
    for doc in docs:
        print(doc)
