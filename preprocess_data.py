import json
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def vectorize():
    news = pd.read_csv('data/reu_identifiers.csv', names=['date', 'id', 'title'],usecols=['id', 'title'])

    news = news[news['title'].isnull() == False]
    news.reindex(labels=np.arange(len(news)))

    vectorizer = TfidfVectorizer(min_df=3,stop_words='english',  dtype=np.int16)

    X = vectorizer.fit_transform((title for title in news['title']))

    id_to_matrix_ix = {}
    for ix, row in news.iterrows():
        id_to_matrix_ix[row['id']] = ix

    np.save('id_to_vec.npy', X)
    #pickle.dump(id_to_vec, open('reu_tfidf.p', 'wb'))
    with open('id_to_matrix_ix.json', 'w') as f:
        json.dump(id_to_matrix_ix, f)





def tokenize(text):
    """Returns a list of words that make up the text.

    Note: for simplicity, lowercase everything.
    Requirement: Use Regex to satisfy this function

    Params: {text: String}
    Returns: Array
    """
    # YOUR CODE HERE
    lower = text.lower()
    tokens = re.findall('[a-z]+', lower)
    return tokens


def make_tf_dict(data):
    article_tf = {}
    unique_toks = set()
    for ix, article in data.iterrows():
        tf_dict = defaultdict(lambda: 0)
        tokens = tokenize(article['content'])
        for tok in tokens:
            tf_dict[tok] += 1
            unique_toks.add(tok)
        article_tf[article['id']] = tf_dict
    return article_tf, unique_toks


def iterate_data():
    dat1 = pd.read_csv('data/articles1.csv')
    dat2 = pd.read_csv('data/articles2.csv')
    dat3 = pd.read_csv('data/articles3.csv')

    article_tf1, unique_toks1 = make_tf_dict(dat1)
    article_tf2, unique_toks2 = make_tf_dict(dat2)
    article_tf3, unique_toks3 = make_tf_dict(dat3)

    unique_toks = unique_toks1.union(unique_toks2).union(unique_toks3)
    print('Unique Tokens:', len(unique_toks))
    article_tf = copy.copy(article_tf1.update(article_tf2).update(article_tf3))

    doc_freq = defaultdict(lambda: 0)

    for article in article_tf:
        for word in article:
            doc_freq[word] += 1


if __name__ == '__main__':
    vectorize()
