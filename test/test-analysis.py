import numpy as np
import os
import string
from nltk.stem.porter import *
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD

stemmer = PorterStemmer()

#load stopwords
stopword_path = 'stopwords_en.txt'
with open(stopword_path, 'r') as stopwordFile:
	stopwords = [word.strip() for word in stopwordFile.readlines()]

trainDir = './test-core/'

vectorizer = CountVectorizer(min_df= 1)
corpus = []

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print "Topic #%d:" % (topic_idx + 1)
        print " ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]) + '\n'

#iterate over experiences, treat the data, and add to corpus
categories = os.listdir(trainDir)
for drug in categories:
	path = trainDir + drug
	aggregatedText = ''
	for experience in os.listdir(path):
		expPath = path + '/' + experience
		print expPath
		with open(expPath, 'r') as experienceFile:
			words = experienceFile.read().strip().split()

			#eliminate stopwords, stem the remaining terms
			editedWords = [word.strip().strip(string.punctuation).lower() for word in words if word.strip().strip(string.punctuation).lower() not in stopwords]
			editedWords = [stemmer.stem(word) for word in editedWords]
			aggregatedText += ' '.join(editedWords)

	#have a distinct corpus for each drug
	corpus.append(aggregatedText)

#fit the corpus
x = vectorizer.fit_transform(corpus)
feature_names = vectorizer.get_feature_names()
countData =  x.toarray()

#tf_idf transform
transformer = TfidfTransformer(smooth_idf= False)
tf_idf = transformer.fit_transform(countData).toarray()

#perform singular value decomposition
svd = TruncatedSVD(n_components= 5)
svdTransform = svd.fit_transform(tf_idf)
print(svdTransform)

#perform non-neg matrix factorization
nmf = NMF(n_components= 5)
nmfTransform = nmf.fit_transform(tf_idf)
print(nmfTransform)

print "SVD TOPICS\n-=-=-=-=-=-=-"
print_top_words(svd, feature_names, 10)

print "NMF TOPICS\n-=-=-=-=-=-=-"
print_top_words(nmf, feature_names, 10)

nmf_transform_sparse = sparse.csr_matrix(nmfTransform)
similarities = cosine_similarity(nmf_transform_sparse)

sortedIndices = np.argsort(similarities, axis= 1)

#the most similar drug will always be itself (which is a good sign!)
#so must find the SECOND most similar, which will be a different drug
maximumIndices = sortedIndices[:,-2]

for index, drug in enumerate(categories):
	print "Drug: " + drug
	print "Most similar: " + categories[maximumIndices[index]]
	print "=-=--=-=-=-=-=-=-"
