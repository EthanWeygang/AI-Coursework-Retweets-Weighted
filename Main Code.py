import pickle
import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import nltk
import os
import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download('stopwords')

# Load the model and vectorizer
# Make sure you have downloaded the Model and Vectorizer File Correctly
with open(r'./sentiment_model_and_vectorizer.sav', 'rb') as file:
    loaded_vectorizer, loaded_model = pickle.load(file)

print("Model and vectorizer loaded successfully!")


# Path to the dataset CSV file
#Change this to any csv file you want! 
dataset_csv_path = r"./Tweets.csv"

# Check if the file exists and is accessible
if not os.path.isfile(dataset_csv_path):
    raise FileNotFoundError(f"The dataset file {dataset_csv_path} does not exist.")
  

# Read the CSV file directly
brand_tweets_df = pd.read_csv(dataset_csv_path)
if brand_tweets_df.isnull().values.any():
  brand_tweets_df = brand_tweets_df.dropna()


brand_tweets_df['likes'] = pd.to_numeric(brand_tweets_df['likes']) # Turns 'likes' column to numeric type (instead of string)

def analyze_brand_tweets():
    # Ensure 'text' column exists (adjust if column name is different)
    if 'Text' not in brand_tweets_df.columns:
        print("Error: 'Text' column not found in the CSV file. Please ensure your CSV has a 'Text' column.")
        return

    # Preprocess the text data (using the same stemming function as in your original training)
    port_stem_new = PorterStemmer()

    def stemming(content):
        stemmed_content = re.sub('[^a-zA-Z]', ' ', content)
        stemmed_content = stemmed_content.lower()
        stemmed_content = stemmed_content.split()
        stemmed_content = [port_stem_new.stem(word) for word in stemmed_content if not word in stopwords.words('english')]
        stemmed_content = ' '.join(stemmed_content)
        return stemmed_content

    brand_tweets_df['stemmed_content'] = brand_tweets_df['Text'].apply(stemming)

    # Vectorize the tweets using the same vectorizer used during training (You'll need to load or recreate this vectorizer)
    X_brand_tweets = loaded_vectorizer.transform(brand_tweets_df['stemmed_content'].values)

    # Predict sentiments for brand tweets
    predictions = loaded_model.predict(X_brand_tweets)

    brand_tweets_df['Predicted_Sentiment'] = predictions

    sentiment_counts = pd.Series(predictions).value_counts(normalize=True) * 100

    sentiment_map = {0: "Negative", 1: "Positive", 2: "Neutral"}
    brand_tweets_df['Sentiment_Label'] = brand_tweets_df['Predicted_Sentiment'].map(sentiment_map)

    
    likes_per_sentiment = brand_tweets_df.groupby("Predicted_Sentiment")["likes"] # Groups sentiments likes together
    summed_likes_per_sentiment = likes_per_sentiment.sum()

   
    total_likes = brand_tweets_df["likes"].sum()
    positive_percentage = (summed_likes_per_sentiment.get(1, 0) / total_likes) * 100
    neutral_percentage = (summed_likes_per_sentiment.get(2, 0) / total_likes) * 100  # Find the distribution of the likes
    negative_percentage = (summed_likes_per_sentiment.get(0, 0) / total_likes) * 100

    Brand_Name = input("Enter the Brand Name: ")

    print(f"\nSentiment Distribution for {Brand_Name}:")
    print(f"Positive: {sentiment_counts.get(1, 0):.2f}%")
    print(f"Negative: {sentiment_counts.get(0, 0):.2f}%")
    print(f"Neutral: {sentiment_counts.get(2, 0):.2f}%")

    print(f"\nLike-Based Sentiment Distribution for {Brand_Name}:")
    print(f"Positive: {positive_percentage:.2f}%")
    print(f"Negative: {negative_percentage:.2f}%") # Prints the percentage of likes for each sentiment
    print(f"Neutral: {neutral_percentage:.2f}%") 

    total_brand_score = 100 - (sentiment_counts.get(1, 0) / sentiment_counts.get(0, 0) + sentiment_counts.get(1, 0))
    print(f"\nBrand Score for {Brand_Name}: {total_brand_score:.2f}%")

    total_brand_score = 100 - (positive_percentage / positive_percentage + negative_percentage) # Calculates the brand score

    print(f"Like-Based brand Score for {Brand_Name}: {total_brand_score:.2f}%")

    print_some_negative_tweets = input("\nDo you want to print some negative tweets? (yes/no): ").lower()
    if print_some_negative_tweets == 'yes':
        print("\nSome Negative Tweets:")
        print(brand_tweets_df.loc[brand_tweets_df['Predicted_Sentiment'] == 0, 'Text'].head(5).to_list())
    else:
        print("Skipping printing some negative tweets.")

    print_some_positive_tweets = input("\nDo you want to print some positive tweets? (yes/no): ").lower()
    if print_some_positive_tweets == 'yes':
        print("\nSome Positive Tweets:")
        print(brand_tweets_df.loc[brand_tweets_df['Predicted_Sentiment'] == 1, 'Text'].head(5).to_list())
    else:
        print("Skipping printing some positive tweets.")

    print_some_neutral_tweets = input("\nDo you want to print some neutral tweets? (yes/no): ").lower()
    if print_some_neutral_tweets == 'yes':
        print("\nSome Neutral Tweets:")
        print(brand_tweets_df.loc[brand_tweets_df['Predicted_Sentiment'] == 2, 'Text'].head(5).to_list())
    else:
        print("Skipping printing some neutral tweets.")
    
    print_some_neutral_tweets = input("\nDo you want to print some high liked tweets? (yes/no): ").lower()
    if print_some_neutral_tweets == 'yes':
        print("\nSome High Liked Tweets:")
        highest_liked = brand_tweets_df.loc[brand_tweets_df["likes"].nlargest(5).index] # locates row of tweets with top 5 highest amounts of likes
        print(highest_liked["Text"])
    else:
        print("Skipping printing some high liked tweets.")

analyze_brand_tweets()
