from django.urls import path
from .views import landing_page, signup, login_view, dashboard, logout_view,check_sentiment

urlpatterns = [
    path('', landing_page, name='landing'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('check_sentiment/', check_sentiment, name='check_sentiment'),
]
