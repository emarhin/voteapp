from django.shortcuts import render ,redirect
from django.contrib.auth import authenticate , logout , login
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User 
from django.views.decorators.csrf import csrf_protect
from polls.models import *
from ussd.models import PaymentSuccess


# Create your views here.


def loginAdmin(request): 
    if request.user.is_authenticated:
        print("authenticated")
        return redirect("dashboard:home")

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return  redirect('dashboard:home')
            else:
                return render(request, 'dashboard/login.html',{'error_message': "Your account has been disabled"})
        else:
            return render(request, 'dashboard/login.html',{'error_message': "Invalid login credentials"})

    return render(request, 'dashboard/login.html')


@login_required(login_url='/dashboard/login/')
def index(request):
    totalQC={
        'total_contestants': Contestant.objects.count(),
        'total_questions': Question.objects.count(),
    }

    moneyVotes={
        'total_votes': 0,
        'total_amount': 0
    }

    for i in webPayment.objects.all():
        if i.verified:
            moneyVotes['total_votes'] += 1
            moneyVotes['total_amount'] += i.amount
        else:
            pass

    for um in PaymentSuccess.objects.all():
            moneyVotes['total_votes'] += 1
            moneyVotes['total_amount'] += um.amount
       
        
    return render(request, 'dashboard/index.html' , {'totalQC':totalQC , 'moneyVotes':moneyVotes})


@login_required(login_url='/dashboard/login/')
def Questions(request):
    questions = Question.objects.all()
    return render(request, 'dashboard/question.html',{'questions':questions})

@login_required(login_url='/dashboard/login/')
def Contestants(request):
    contestants = Contestant.objects.all()
    data =[]
    for contestant in contestants:
        choices = Choice.objects.filter(choice_text=contestant.id)
        for c in choices:
            data.append(c)

    return render(request, 'dashboard/contestant.html',{'choices':data})

# @login_required(login_url='/dashboard/login/')
# def webPayments(request):
#     payments = webPayment.objects.all()
#     return render(request, 'dashboard/webPayment.html',{'payments':payments})



def LogoutOut(request):
    logout(request)
    return redirect('dashboard:login')


