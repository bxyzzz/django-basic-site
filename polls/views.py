from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.views import generic
from django.contrib import messages
# SOURCE: https://stackoverflow.com/questions/47923952/python-django-how-to-display-error-messages-on-invalid-login
from .models import Choice, Question, Comment
# shit i didnt import comment that's why... [1:58 AM]
# IT'S BECAUSE I DIDN'T MAKEMIGRATE. i spent 2 hours my god [2:09 AM]
# ok i give up [2:29 AM]
# just kidding i figured it out i think im just tired from working 8 hrs straight [2:41 AM]
# YES I FIGURED IT OUT [3:05 AM]
# Error messages included [3:29 AM]
from django.utils import timezone

"""
Non-Generic Views:

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}

    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html',{'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # OLD stub: response = "You're looking at the results of question %s."

    return render(request, 'polls/results.html', {'question': question})
"""

def comments(request):
    # I know the page must exist so I'm not having a 404 error.

    return render(request, 'polls/comments.html')
    #return HttpResponse("You're commenting: ")

def commentlist(request):
    all_comments_list = Comment.objects.all()
    context = {'all_comments_list': all_comments_list}

    #return HttpResponse(all_comments_list)
    return render(request, 'polls/commentlist.html', context)

def addcomment(request):

    commenttitle = request.POST['commenttitle']
    commenttext = request.POST['commenttext']

    if commenttitle == '':
        messages.error(request,'You cannot submit a comment without a title.')
        if commenttext == '':
            messages.error(request,"You cannot submit a comment without text.")
        return render(request, 'polls/comments.html')

    if commenttext == '':
        messages.error(request,"You cannot submit a comment without text.")
        return render(request, 'polls/comments.html', {
            'error_message': "You cannot submit a comment without text.",
        })
    
    c = Comment(title=commenttitle, text=commenttext)
    c.save()

    return HttpResponseRedirect(reverse('polls:commentlist'))


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        # Return last 5 published questions (excluding questions with publish date in the future)
        """
        Exclude any questions that don't have any choices.
        
            Took code from StackOverflow because I didn't know the isnull attribute:
                https://stackoverflow.com/questions/26825058/preventing-polls-without-choices-from-being-published
        """

        return Question.objects.exclude(choice__isnull=True).filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]
    
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        return Question.objects.exclude(choice__isnull=True)

def vote(request, question_id):
### FAILS RACE_CONDITIONS!!! https://docs.djangoproject.com/en/4.1/ref/models/expressions/#avoiding-race-conditions-using-f

    # get_object_or_404 looks for the value given the specific key 'pk', else return 404 HTTP error

    question = get_object_or_404(Question, pk=question_id)
    # What is choice_set? 
        # ANSWER: https://stackoverflow.com/questions/2048777/what-is-choice-set-in-this-django-app-tutorial
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    else:
        selected_choice.votes += 1
        selected_choice.save()
        # When dealing with POST data, ALWAYS return an HttpResponseRedirect
            # Prevents data from being posted twice if the user reenters the form using the back button

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
