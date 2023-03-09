from django.test import TestCase
from django.utils import timezone

import datetime

from .models import Question, Comment
from django.urls import reverse

# 2/14/23 | 8:52 PM | @ Apartment, actually kind of mildly hyper-focused today

# FIN @ 10:12 PM, did extra optional tests!! honestly kinda fun/interesting tbh

# Create your tests here.

def create_question(question_text, days):
    """
    Create a question with the given text 'question_text' and published the given number of 'days'
    offset to now (negative for questions published in the past, and positive for those in the future)
    """
    time = timezone.now() + datetime.timedelta(days=days)

    return Question.objects.create(question_text=question_text, pub_date=time)  

def create_choice(question, choice_text=""):
    """
    Given an input question, create a choice for that question.
    """
    # This is from Part 2 of the Django tutorial!
    question.choice_set.create(choice_text=choice_text, votes=0)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a past pub_date are displayed on the index page.
        """
        question = create_question(question_text="Past Question Test.", days=-30)
        create_choice(question)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a future pub_date are NOT displayed on the index page.
        """
        question = create_question(question_text="Future Question Test.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [],
        )

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question)
        create_choice(create_question(question_text="Future question.", days=30))
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions. 
            ME: also, must be in correct order since [question1, question2]
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)

        create_choice(question1)
        create_choice(question2)

        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

    # Damn this was kind of hard honestly to figure out this myself [10:07 PM], spent like 35 minutes on this so far
    def test_questions_has_no_choices(self):
        """
        Questions without any choices should not be published in the first place (NOT just not displaying it).
        """
        no_choices_question = create_question(question_text="No choices.", days=0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [],
        )
    
    def test_question_has_choices(self):
        """
        Questions with choices should be able to be published and displayed.
        """
        choices_question = create_question(question_text="Choices.", days=0)
        create_choice(choices_question, "Choice 1.")
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [choices_question],
        )

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently returns False for questions whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently returns True for questions whose pub_date is within the last day
        """
        time = timezone.now() - datetime.timedelta(days=0, hours=23, minutes=59, seconds=50)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)