import time
import pickle
import pandas as pd
from newspaper import Article

def scrape(lbound=0, ubound=10000):
    rdat = pd.read_csv('data/reddit_data.csv')
    article_text = {}
    for ix, row in rdat[lbound:ubound].iterrows():
        start = time.time()
        article = Article(row['url'])
        article.download()
        try:
            article.parse()
            if (article.text != ''):
                article_text[ix] = article.text
        except:
            article_text[ix] = 'N/A'
        if ix % 100 == 0:
            print('Progress at article #', ix, '   completed at', ("{0:.2f}".format((time.time()-start)/60.)), 'minutes')
    end = time.time()
    save_str = 'reddit_article_text' + str(lbound) + 'to' + str(ubound) + '.p'
    print(end - start)
    pickle.dump(article_text, open(save_str, 'wb'), protocol=2)

if __name__ == '__main__':
    scrape(0, 25000)
