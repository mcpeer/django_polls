from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic

from .models import Choice, Question

from django.utils import timezone

# Create your views here.
# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {
#         'latest_question_list': latest_question_list
#     }
#     return render(request, 'polls/index.html', context)
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions, excl
        those to be published in the future

        __lte means less then or equal to
        """
        return Question.objects.filter(
            pub_date__lte = timezone.now()
        ).order_by('-pub_date')[:5]

class ScheduledView(generic.ListView):
    template_name = 'polls/scheduled.html'
    context_object_name = 'scheduled_question_list'

    def get_queryset(self):
        """
        Return the first five upcoming scheduled questions

        __gt means greater then
        """
        return Question.objects.filter(
            pub_date__gt = timezone.now()
        ).order_by('pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        excl any q's that arent' published yet
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/result.html'

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     context = {'question': question}
#     return render(request, 'polls/details.html', context)

# def detail(request, question_id):
#     try:
#         question = Question.objects.get(pk=question_id)
#         context = {
#             'question': question
#         }
#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'polls/details.html', context)
    
# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', context={'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try: 
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request, 'polls/details.html', context = {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # We use the F() object to update the votes, to avoid Race conditions.
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        # always return an HttpResponseRedirect after successfully dealing 
        # with POST data. This prevents data from being posted twice if a user hits the 
        # back button. 
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))