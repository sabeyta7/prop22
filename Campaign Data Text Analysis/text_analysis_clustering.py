import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.cluster import KMeans, AgglomerativeClustering
import matplotlib.pyplot as plt
from gensim import corpora, models
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis
import pyLDAvis.sklearn

# Assuming you have a DataFrame named 'df' containing articles in the 'text' column
df ['text_lower'] = df['text'].str.lower()
df.loc[:,'tokenized'] = df['text_lower'].copy().apply(lambda article: word_tokenize(article))# if pd.isnull(article) else [])
df.loc[:,'tokenized_stop'] = df['tokenized'].apply(lambda x: [e for e in x if e not in stowords_set])
print("tokenized stop")
df.loc[:,'tokenized_punct'] = df['tokenized_stop'].apply(lambda x: [e for e in x if e not in punct])
df.loc[:,'tokenized_stemmed'] = df['tokenized_punct'].apply(lambda x: stemming(x))
print("tokenized stem")
df.loc[:,'text_edited'] = df['tokenized_punct'].copy().apply(lambda row:' '.join(row))
df.loc[:,'stem_edited'] = df['tokenized_stemmed'].copy().apply(lambda row:' '.join(row))

# Step 1: Adding information into each article like word distributions, parts of speech
df['word_dist'] = df['tokenized_punct'].apply(lambda article: nltk.FreqDist(article))
df['part_of_speech'] = df['tokenized_punct'].apply(lambda article: nltk.pos_tag(article))
df['chunked_speech'] = df['part_of_speech'].apply(lambda article: nltk.ne_chunk(article))

# Step 2: Making more accurate parts of speech
df['adjectives'] = df['part_of_speech'].apply(lambda article: [word for word, pos in article if pos.startswith('JJ')])
df['nouns'] = df['part_of_speech'].apply(lambda article: [word for word, pos in article if pos.startswith('NN')])
df['verbs'] = df['part_of_speech'].apply(lambda article: [word for word, pos in article if pos.startswith('VB')])

# Step 3: Adding frequencies of parts of speech
df['adj_dist'] = df['adjectives'].apply(lambda article: nltk.FreqDist(article))
df['noun_dist'] = df['nouns'].apply(lambda article: nltk.FreqDist(article))
df['verb_dist'] = df['verbs'].apply(lambda article: nltk.FreqDist(article))

# Step 4: Adding frequencies of parts of speech
df['common_adj'] = df['adj_dist'].apply(lambda article: article.most_common(10))
df['common_noun'] = df['noun_dist'].apply(lambda article: article.most_common(10))
df['common_verb'] = df['verb_dist'].apply(lambda article: article.most_common(10))

# Step 5: Adding word count
df['text_length'] = df['tokenized_punct'].apply(len)

# Step 6: Convert the text into a TF-IDF matrix
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['text'])

# Step 7: Apply dimensionality reduction techniques (PCA and SVD) to the TF-IDF matrix
pca = PCA(n_components=2)
svd = TruncatedSVD(n_components=2)
reduced_pca = pca.fit_transform(tfidf_matrix.toarray())
reduced_svd = svd.fit_transform(tfidf_matrix)

# Step 8: Make elbow plots to find good starting parameters
# Create a list of different number of clusters to try
num_clusters = range(1, 11)  # Try from 1 to 10 clusters

# Initialize lists to store the inertia (for K-means) and connectivity (for Agglomerative) scores
inertia_scores = []
connectivity_scores = []

# Loop through different number of clusters and calculate the scores
for n_clusters in num_clusters:
    # K-means
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(reduced_svd)
    inertia_scores.append(kmeans.inertia_)  # Append the inertia score to the list

    # Agglomerative Clustering
    agglomerative = AgglomerativeClustering(n_clusters=n_clusters)
    agglomerative.fit(reduced_svd)
    connectivity_scores.append(agglomerative.connectivity_)  # Append the connectivity score to the list

# Plot the elbow plots
plt.figure(figsize=(10, 6))

# Elbow plot for K-means
plt.subplot(1, 2, 1)
plt.plot(num_clusters, inertia_scores, marker='o')
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.title('Elbow Plot for K-means')

# Elbow plot for Agglomerative Clustering
plt.subplot(1, 2, 2)
plt.plot(num_clusters, connectivity_scores, marker='o')
plt.xlabel('Number of Clusters')
plt.ylabel('Connectivity')
plt.title('Elbow Plot for Agglomerative Clustering')

plt.tight_layout()
plt.show()

# Step 9: Use two clustering algorithms (K-means and AgglomerativeClustering) on the reduced TF-IDF matrix
kmeans = KMeans(n_clusters="# of clusters")
agglomerative = AgglomerativeClustering(n_clusters="# of clusters")
kmeans_clusters = kmeans.fit_predict(reduced_svd)
agglomerative_clusters = agglomerative.fit_predict(reduced_svd)

# Combine cluster labels into the DataFrame
df['kmeans_cluster_label'] = kmeans_clusters
df['agglomerative_cluster_label'] = agglomerative_clusters

# Step 10: Extracting Top Features from Each Cluster for K-means
kmeans_top_features = []
for cluster_label in range(3):
    cluster_articles = df[df['kmeans_cluster_label'] == cluster_label]['text_edited']
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cluster_articles)
    feature_names = vectorizer.get_feature_names_out()
    top_features = np.argsort(tfidf_matrix.sum(axis=0).A1)[::-1][:10]  # Get the indices of top features
    top_feature_words = [feature_names[i] for i in top_features]
    kmeans_top_features.append(top_feature_words)

df['kmeans_top_features'] = pd.Series(kmeans_top_features)

# Step 10: Extracting Top Features from Each Cluster for Agglomerative Clustering
agglomerative_top_features = []
for cluster_label in range(3):
    cluster_articles = df[df['agglomerative_cluster_label'] == cluster_label]['text_edited']
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cluster_articles)
    feature_names = vectorizer.get_feature_names_out()
    top_features = np.argsort(tfidf_matrix.sum(axis=0).A1)[::-1][:10]  # Get the indices of top features
    top_feature_words = [feature_names[i] for i in top_features]
    agglomerative_top_features.append(top_feature_words)

df['agglomerative_top_features'] = pd.Series(agglomerative_top_features)

# Step 11: Word Concordances for K-means
for cluster_label in range(3):
    print(f"Concordances for K-means Cluster {cluster_label}:")
    cluster_articles = df[df['kmeans_cluster_label'] == cluster_label]['text']
    for article in cluster_articles:
        text = nltk.Text(nltk.word_tokenize(article))
        concordance_list = text.concordance_list("word_to_search", width=80, lines=5)  # Replace "word_to_search" with the word to search for
        concordances = [concordance.line for concordance in concordance_list]
        for concordance in concordances:
            print(concordance)

# Step 11: Word Concordances for Agglomerative Clustering
for cluster_label in range(3):
    print(f"Concordances for Agglomerative Cluster {cluster_label}:")
    cluster_articles = df[df['agglomerative_cluster_label'] == cluster_label]['text']
    for article in cluster_articles:
        text = nltk.Text(nltk.word_tokenize(article))
        concordance_list = text.concordance_list("word_to_search", width=80, lines=5)  # Replace "word_to_search" with the word to search for
        concordances = [concordance.line for concordance in concordance_list]
        for concordance in concordances:
            print(concordance)
            


"""
Alternative of LDA
"""

# Step 1: Preprocessing
documents = df['text_edited'].tolist()  # Replace this with your own list of documents
tf_vectorizer = TfidfVectorizer(stop_words='english')
tf = tf_vectorizer.fit_transform(documents)

# Step 2: LDA Model
num_topics = 5  # You can change this to the desired number of topics
lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
lda_model.fit(tf)

# Step 3: Visualize the LDA model
pyLDAvis.enable_notebook()
vis = pyLDAvis.sklearn.prepare(lda_model, tf, tf_vectorizer)
pyLDAvis.display(vis)