from django.contrib import admin
from django.urls import path

from . import views 

app_name = 'polls'
urlpatterns = [
    # Ex: /polls/
    path('', views.IndexView.as_view(), name='index'),
    # Ex: /polls/5
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # Ex: /polls/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # Ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
    # Ex: /polls/comments/
    path('comments/', views.comments, name='comments'),
    # Ex: /polls/comments/list
    path('comments/list/', views.commentlist, name='commentlist'),
    # Ex: /polls/comments/add
    path('comments/add/', views.addcomment, name='addcomment'),

]
