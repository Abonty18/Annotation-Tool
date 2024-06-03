import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from textblob import TextBlob
import nltk

# Download NLTK resources if not already downloaded
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

# Define the path to your CSV file
file_path = 'final_reviews.csv'
# Read the file with the detected encoding
df = pd.read_csv(file_path, encoding='Windows-1252')

# Extract relevant columns
df = df[['review_content', 'final_label']]

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    tokens = TextBlob(text).words
    porter_stemmer = PorterStemmer()
    tokens = [porter_stemmer.stem(word) for word in tokens]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Apply preprocessing
df['review_processed'] = df['review_content'].apply(preprocess_text)

# Load the pre-trained vectorizer and scaler
vectorizer = joblib.load('tfidf_vectorizer.pkl')
scaler = joblib.load('scaler.pkl')

# Transform the reviews
X_tfidf = vectorizer.transform(df['review_processed'])
X_scaled = scaler.transform(X_tfidf)

# Load the pre-trained label encoder and model
label_encoder = joblib.load('label_encoder.pkl')
svm_model = joblib.load('best_logreg_model.pkl')

# Encode the labels
y_encoded = label_encoder.transform(df['final_label'])

# Train the model
svm_model.fit(X_scaled, y_encoded)

# Save the updated model
joblib.dump(svm_model, 'best_logreg_model.pkl')

print("Model trained and saved successfully.")