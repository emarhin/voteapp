import json
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework.response import Response
import requests
from .models import Question, Choice , webPayment

#Landing page 
def LandingPage(request):
  return render(request, 'pages/index.html')


# Get questions and display them
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

# Show specific question and choices
def detail(request, question_id):
  try:
    question = Question.objects.get(pk=question_id)
  except Question.DoesNotExist:
    raise Http404("Question does not exist")
  return render(request, 'polls/detail.html', { 'question': question })

# Get question and display results
def results(request, question_id):
  question = get_object_or_404(Question, pk=question_id)
  return render(request, 'polls/results.html', { 'question': question })

# Vote for a question choice
def vote(request, question_id):
    if request.method=='POST':
      Name =request.POST['fullName']
      phone=request.POST['phonenumber']
      amount=request.POST['amount']
      email=request.POST['email']
      
      question = get_object_or_404(Question, pk=question_id)

      # print(amount)

      #throw error to front page if choice is not selected
      try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
      except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

      return render(request, 'polls/payment.html',{"email":email,'phone':phone,'amount':amount,'question_id':question_id,'choice':request.POST['choice'],'Name':Name})

    
def verifyPayment(request,ref: str) -> HttpResponse:
  amount = request.POST['amount']
  choice = request.POST['choice']
  phone = request.POST['phone']
  email = request.POST['email']
  Name = request.POST['Name']
  question_id = request.POST['question_id']
  reference = ref
  status, response = verify_payment(reference)
  
  if status:
      question = get_object_or_404(Question, pk=question_id)
      question.choice_set.get(pk=choice) 
      selected_choice = question.choice_set.get(pk=choice)

      votesToAdd = int(amount) / 0.5
      selected_choice.votes += votesToAdd
      selected_choice.save()
     
     
      webPayment.objects.create(Name=Name,phone=phone,amount=amount,email=email,question_id=question_id,choice=choice,reference=reference,status=status,verified=True)
      return HttpResponse(question_id)
  else:
      webPayment.objects.create(Name=Name,phone=phone,amount=amount,email=email,question_id=question_id,choice=choice,reference=reference,status=status,verified=False)
      return HttpResponse(False)



def verify_payment(ref):
      base_url = 'https://api.paystack.co'
      path = f'/transaction/verify/{ref}'
      headers = {
            'Authorization': f'Bearer sk_live_49802921ecd505a560da644607d0f8f7bd782efb',
            'Content-Type': 'application/json',
        }
      url = base_url + path
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
          response_data = response.json()
          return response_data['status'], response_data['data']
      response_data = response.json()
      return response_data['status'], response_data['message']



