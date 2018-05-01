import gc
import copy
import json
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.preprocessing import normalize
from scipy.sparse.linalg import svds
from scipy.sparse import save_npz, load_npz, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

BASE = "/app/app/irsystem/models/"

def vectorize_ALLTHENEWS():
    dat1 = pd.read_csv('data/articles1.csv', usecols=['content'])
    dat2 = pd.read_csv('data/articles2.csv', usecols=['content'])
    dat3 = pd.read_csv('data/articles3.csv', usecols=['content'])
    gc.collect()
    vectorizer = TfidfVectorizer( min_df = 10, max_df=30000, stop_words='english',  dtype=np.int16)
    gc.collect()
    X = vectorizer.fit_transform((article for article in pd.concat([dat1, dat2, dat3])['content'])).astype(dtype=np.float16)
    gc.collect()
    save_npz('allthenews_tfidf_mat.npz', X)
    gc.collect()
    print('Vocab Length: ', len(vectorizer.vocabulary_))
    pickle.dump(vectorizer.vocabulary_, open('allthenews_vocab_ix.p', 'wb'), protocol=2)



def make_SVD():
    tfidf_mat = load_npz('allthenews_tfidf_mat.npz')
    gc.collect()
    u, sigma, v_trans = svds(tfidf_mat.asfptype().transpose(), k=100)
    np.save('u.npy', u)
    np.save('sigma.npy', sigma)
    np.save('v_trans.npy', v_trans)

def closest_words(word_in, words_compressed, word_to_ix, index_to_word, k=3, cutoff=.9):
    if word_in not in word_to_ix:
        return []
    sims = words_compressed.dot(words_compressed[word_to_ix[word_in],:])
    sims[sims < cutoff] = 0
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_word[i]) for i in asort[1:] if sims[i]>0]

def expand_query(query_tokens_ix, query_tokens_term, reu_vocab_to_ix):
    expanded_query = copy.deepcopy(query_tokens_ix)
    with open(os.path.join(BASE, 'u.npy'), 'rb') as u:
        with open(os.path.join(BASE, 'v_trans.npy'), 'rb') as v_trans:
            words_compressed = np.load(u)
            docs_compressed = np.load(v_trans)
            words_compressed = normalize(words_compressed, axis = 1)

            ATN_word_to_ix = pickle.load(open(os.path.join(BASE, 'allthenews_vocab_ix.p'), 'rb'))
            ATN_ix_to_word = {i:t for t,i in ATN_word_to_ix.iteritems()}
            for tok in query_tokens_term:
                syns = closest_words(tok, words_compressed, ATN_word_to_ix, ATN_ix_to_word)
                for w in syns:
                    reu_ix = reu_vocab_to_ix.get(w, -1)
                    if reu_ix != -1:
                        expanded_query[reu_vocab_to_ix[w]] = max(.6/len(query_tokens_term), .2)
            gc.collect()
            return expanded_query


if __name__ == '__main__':
    vectorize_ALLTHENEWS()
    make_SVD()
