import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from textblob import TextBlob
import nltk
import re

# Download NLTK resources if not already downloaded
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

# Define the path to your CSV file
file_path = 'final_reviews.csv'

# Read the file with the detected encoding
df = pd.read_csv(file_path, encoding='Windows-1252')

# Extract relevant columns
df = df[['processed_review_content', 'final_label']]

# Handle missing values
df = df.dropna(subset=['processed_review_content'])

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    tokens = TextBlob(text).words
    porter_stemmer = PorterStemmer()
    tokens = [porter_stemmer.stem(word) for word in tokens]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Apply preprocessing
df['review_processed'] = df['processed_review_content'].apply(preprocess_text)

# Load the pre-trained vectorizer and scaler
vectorizer = joblib.load('tfidf_vectorizer.pkl')
scaler = joblib.load('scaler.pkl')

# Transform the reviews
X_tfidf = vectorizer.transform(df['review_processed'])
X_scaled = scaler.transform(X_tfidf)

# Load the pre-trained label encoder
label_encoder = joblib.load('label_encoder.pkl')

# Encode the labels
y_encoded = label_encoder.transform(df['final_label'])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# Hyperparameter tuning with Grid Search for Logistic Regression
param_grid_logreg = {
    'C': [0.01, 0.1, 1, 10, 100],
    'solver': ['lbfgs', 'liblinear', 'saga', 'newton-cg'],
    'max_iter': [1000, 2000, 5000, 10000]
}

grid_search_logreg = GridSearchCV(LogisticRegression(), param_grid_logreg, cv=5, scoring='accuracy')
grid_search_logreg.fit(X_train, y_train)

# Best parameters and model for Logistic Regression
best_params_logreg = grid_search_logreg.best_params_
print(f"Best Parameters for Logistic Regression: {best_params_logreg}")

# Train the model with best parameters
best_logreg_model = grid_search_logreg.best_estimator_
best_logreg_model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred_logreg = best_logreg_model.predict(X_test)

# Calculate accuracy for Logistic Regression
accuracy_logreg = accuracy_score(y_test, y_pred_logreg)
print(f"Logistic Regression Model Accuracy: {accuracy_logreg * 100:.2f}%")

# Convert target names to strings
target_names = [str(cls) for cls in label_encoder.classes_]

# Print classification report for Logistic Regression
print("Logistic Regression Classification Report")
print(classification_report(y_test, y_pred_logreg, target_names=target_names))

# Random Forest Model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions with Random Forest
y_pred_rf = rf_model.predict(X_test)

# Calculate accuracy for Random Forest
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print(f"Random Forest Model Accuracy: {accuracy_rf * 100:.2f}%")

# Print classification report for Random Forest
print("Random Forest Classification Report")
print(classification_report(y_test, y_pred_rf, target_names=target_names))

# Support Vector Machine (SVM) Model
param_grid_svm = {
    'C': [0.1, 1, 10, 100],
    'kernel': ['linear', 'rbf'],
    'gamma': ['scale', 'auto']
}

grid_search_svm = GridSearchCV(SVC(), param_grid_svm, cv=5, scoring='accuracy')
grid_search_svm.fit(X_train, y_train)

# Best parameters and model for SVM
best_params_svm = grid_search_svm.best_params_
print(f"Best Parameters for SVM: {best_params_svm}")

# Train the model with best parameters
best_svm_model = grid_search_svm.best_estimator_
best_svm_model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred_svm = best_svm_model.predict(X_test)

# Calculate accuracy for SVM
accuracy_svm = accuracy_score(y_test, y_pred_svm)
print(f"SVM Model Accuracy: {accuracy_svm * 100:.2f}%")

# Print classification report for SVM
print("SVM Classification Report")
print(classification_report(y_test, y_pred_svm, target_names=target_names))

# Gradient Boosting Model
gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb_model.fit(X_train, y_train)

# Make predictions with Gradient Boosting
y_pred_gb = gb_model.predict(X_test)

# Calculate accuracy for Gradient Boosting
accuracy_gb = accuracy_score(y_test, y_pred_gb)
print(f"Gradient Boosting Model Accuracy: {accuracy_gb * 100:.2f}%")

# Print classification report for Gradient Boosting
print("Gradient Boosting Classification Report")
print(classification_report(y_test, y_pred_gb, target_names=target_names))

# XGBoost Model
xgb_model = XGBClassifier(n_estimators=100, random_state=42)
xgb_model.fit(X_train, y_train)

# Make predictions with XGBoost
y_pred_xgb = xgb_model.predict(X_test)

# Calculate accuracy for XGBoost
accuracy_xgb = accuracy_score(y_test, y_pred_xgb)
print(f"XGBoost Model Accuracy: {accuracy_xgb * 100:.2f}%")

# Print classification report for XGBoost
print("XGBoost Classification Report")
print(classification_report(y_test, y_pred_xgb, target_names=target_names))

# Save the updated models
joblib.dump(best_logreg_model, 'best_logreg_model1.pkl')
joblib.dump(rf_model, 'best_rf_model.pkl')
joblib.dump(best_svm_model, 'best_svm_model.pkl')
joblib.dump(gb_model, 'best_gb_model.pkl')
joblib.dump(xgb_model, 'best_xgb_model.pkl')
