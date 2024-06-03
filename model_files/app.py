from flask import Flask, request, jsonify
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from textblob import TextBlob
import nltk
import warnings

# Suppress scikit-learn version mismatch warnings
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# Download NLTK resources if not already downloaded
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

# Initialize Flask application
app = Flask(__name__)

# Load the pre-trained models and vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')
scaler = joblib.load('scaler.pkl')
svm_model = joblib.load('best_logreg_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

def preprocess_text(text):
    # Preprocessing function
    text = text.lower()
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    tokens = TextBlob(text).words
    porter_stemmer = PorterStemmer()
    tokens = [porter_stemmer.stem(word) for word in tokens]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    review_content = data['review_content']

    # Preprocess and vectorize the input data
    review_content_processed = preprocess_text(review_content)
    review_tfidf = vectorizer.transform([review_content_processed])
    review_tfidf_scaled = scaler.transform(review_tfidf)

    # Predict the label
    prediction = svm_model.predict(review_tfidf_scaled)
    label = label_encoder.inverse_transform(prediction)

    # Return the prediction as JSON
    return jsonify({'label': label[0]})

if __name__ == '__main__':
    app.run(debug=True)
