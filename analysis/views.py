from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import SentimentAnalysis
import pickle
import re

# Load the sentiment analysis model and label encoder
with open('sentiment_model.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)

# Landing page view
def landing_page(request):
    return render(request, 'analysis/landing.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'analysis/signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'analysis/login.html')

# Dashboard view
@login_required
def dashboard(request):
    sentiments = SentimentAnalysis.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'analysis/dashboard.html', {
        'sentiments': sentiments,
        'username': request.user.username  # Pass the username to the template
    })

# Logout view
def logout_view(request):
    logout(request)
    return redirect('landing')

# Text cleaning function
def clean_text(text):
    """
    Clean the input text by removing URLs, hashtags, mentions, and punctuation.
    """
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

# Sentiment prediction function
def predict_sentiment(news_text):
    """
    Predict the sentiment of the given news text using the pre-trained model.
    """
    # Clean the input text
    cleaned_text = clean_text(news_text)

    # Prepare the input for the model
    input_data = [cleaned_text]  # Wrap in a list for batch processing

    # Make a prediction
    prediction = loaded_model.predict(input_data)

    # Map the prediction to sentiment labels
    sentiment_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
    sentiment_label = sentiment_mapping.get(prediction[0], 'unknown')  # Fallback to 'unknown' if needed

    return sentiment_label

# Check sentiment view
@login_required
def check_sentiment(request):
    if request.method == 'POST':
        news_text = request.POST['news_text']
        
        # Predict sentiment based on the user input
        sentiment = predict_sentiment(news_text)  # Returns 'negative', 'neutral', or 'positive'
        
        # Create a new SentimentAnalysis object in the database
        SentimentAnalysis.objects.create(user=request.user, text=news_text, sentiment=sentiment)
        
        # Redirect to the dashboard after saving the result
        return redirect('dashboard')
