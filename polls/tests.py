import datetime
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse 

from .models import Question

# Create your tests here.
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is 
        in the future 
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is 
        older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days = 30)
        history_question = Question(pub_date = time)
        self.assertIs(history_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is
        less then 1 day old.
        """
        time = timezone.now() - datetime.timedelta(hours = 10)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)

    
def create_question(question_text, days):
    """
    Create a question with the given 'question_text' and published the given
    number of days offset to now (negative for questions published in the past,
    postive for q's that yet have to be published)
    """
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text=question_text, pub_date = time)


class QuestionIndexViewTest(TestCase):
    def test_no_questions(self):
        """
        If no questions exists, an appropriate message is shown
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')

        self.assertNotIn('latest_question_list', list(response.context))

    def test_past_questions(self):
        """
        Q's with a pub_date in past are displayed
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Q's with a pub_date in future are not displayed
        """
        create_question(question_text="Fut q", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertNotIn('latest_question_list', list(response.context))

    def test_future_questions_and_past_questions(self):
        """
        Even if both past and future questions exist, only past questions are displayed
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text='future', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The question index page may display multiple questions
        """
        create_question(question_text="Past question1.", days=-30)
        create_question(question_text="Past question2.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], 
            ['<Question: Past question2.>', '<Question: Past question1.>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found
        """
        future_question = create_question(question_text = 'Future question.', days = 5)
        url = reverse('polls:detail', args = (future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of question with pub_date in past
        displays the questions text
        """
        past_q = create_question(question_text = "Past", days = -4)
        url = reverse('polls:detail', args = (past_q.id,))
        response = self.client.get(url)
        self.assertContains(response, past_q.question_text)