from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F

from .models import Choice, Question

# Create your views here.
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list
    }
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'polls/details.html', context)

# def detail(request, question_id):
#     try:
#         question = Question.objects.get(pk=question_id)
#         context = {
#             'question': question
#         }
#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'polls/details.html', context)
    
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', context={'question': question})

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