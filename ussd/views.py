from django.shortcuts import render
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
from  polls.models import *
from .models import *
# Create your views here.
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json

webhookIps = ["52.31.139.75","52.49.173.169","52.214.14.220"]

#keys

#Test key
# key = 'sk_test_60f48dab304e54252bdd5da374a980063b2b5d73'

# live
key = 'sk_live_49802921ecd505a560da644607d0f8f7bd782efb'


@api_view(['POST'])
def ussdvote(request):

    payload = request.data

    # print(payload)
  

    # Gettng the request from the user
    if request.method == 'POST':
        sessionID =  payload['session_id']
        msisdn = payload['msisdn']
        msg_type =payload['msg_type']
        ussd_body = payload['ussd_body']
        nw_code = payload['nw_code']
        service_code = payload['service_code']

    #paramenters to be sent back to the user
    params = {
        'nw_code': nw_code,
        'session_id': sessionID,
        'service_code': service_code,
        'msisdn': msisdn,
        'msg_type': "1",
        'ussd_body': "helloå" }


    #testing
    # print(params)

    user_input = capture_input(ussd_body)
    

    if msg_type == "0":
        params["ussd_body"] = "Welcome to GHAAWARDS:" + "\n Enter your Contestant code to vote Now"
        output = params
    elif msg_type == "1":
        output = processes(user_input,params)
        

    return send_response(output)


def processes(user_input,params):
    createNewProcess = True
    for ussdpatmnt in Ussdpayment.objects.all():

        #Checking if this new session on going and in process
        if ussdpatmnt.session_id == params['session_id']:
            createNewProcess = False
                   
            #display contestant is competing for of the code input
            if ussdpatmnt.level == 1:

                # search for contestant but not found display the contestant not found as a response
                try:
                    contestantFound = Contestant.objects.get(code=user_input['message'])
                except Contestant.DoesNotExist:
                    params["ussd_body"] = f'Contestant code not found \n Enter your Contestant code to vote Now'
                    return params
                     
                choiceFound = Choice.objects.filter(choice_text = contestantFound.id)
                contestantName = contestantFound.Name
                contestingFor = ""
                for c in  choiceFound:
                    contestingFor =  f'\n {c.question.id}.{c.question.question_text}'

                ussdpatmnt.codeinput = user_input['message']
                ussdpatmnt.level = 2

                ussdpatmnt.save()
                params["ussd_body"] = f'\n {contestantName} is competing for {contestingFor}'
                output = params
 
                return output

               

            #Get what Question the user is voting for
            elif ussdpatmnt.level == 2:

                # Get contestant
                contestantCode =  ussdpatmnt.codeinput
                try:
                    contestantFound = Contestant.objects.get(code=contestantCode)
                    contestantName = contestantFound.Name
                except Contestant.DoesNotExist:
                    ussdpatmnt.level = 1
                    ussdpatmnt.save()
                    params["ussd_body"] = f'Contestant code not found \n Enter your Contestant code to vote Now'
                    return params

                # Get question
                try:
                    questionFound = Question.objects.get(id=user_input['message'])
                    ussdpatmnt.QuestionVotingFOr = questionFound.id
                    ussdpatmnt.level = 3
                    ussdpatmnt.save()
                    params["ussd_body"] = f'\n Enter amount to pay on {questionFound.question_text} for {contestantName}'
                    return params

                except Question.DoesNotExist:
                    choiceFound = Choice.objects.filter(choice_text = contestantFound.id)
                    contestingFor = ""
                    for c in  choiceFound:
                        contestingFor =  f'\n {c.question.id}.{c.question.question_text}'               
                    params["ussd_body"] = f'Category voting for not found \n {contestantName} is competing for {contestingFor}'
                    return params
                except ValueError:
                    ussdpatmnt.save()
                    choiceFound = Choice.objects.filter(choice_text = contestantFound.id)
                    contestingFor = ""
                    for c in  choiceFound:
                        contestingFor =  f'\n {c.question.id}.{c.question.question_text}' 
                    params["ussd_body"] = f'Category voting for not found \n {contestantName} is competing for {contestingFor}'
                    return params

            #Get the amount to pay
            elif ussdpatmnt.level == 3:
                try:
                    contestantFound = Contestant.objects.get(code=ussdpatmnt.codeinput)
                    contestantName = contestantFound.Name
                except Contestant.DoesNotExist:
                    ussdpatmnt.level = 1
                    ussdpatmnt.save()
                    params["ussd_body"] = f'Contestant code not found \n Enter your Contestant code to vote Now'
                    return params

                try:
                    questionFound = Question.objects.get(id=ussdpatmnt.QuestionVotingFOr)
                except Question.DoesNotExist:
                    choiceFound = Choice.objects.filter(choice_text = contestantFound.id)
                    ussdpatmnt.level = 2
                    contestingFor = ""
                    for c in  choiceFound:
                        contestingFor =  f'\n {c.question.id}.{c.question.question_text}'

                    params["ussd_body"] = f'Category voting for not found \n {contestantName} is competing for {contestingFor}'
                    return params

                try:    
                    ussdpatmnt.amount = int(user_input['message'])
                    ussdpatmnt.save()
                except ValueError:
                    params["ussd_body"] = f'Amount entered is not valid \n Enter amount to pay on {questionFound.question_text} for {contestantName}'
                    return params
        
         
               
                data = json.dumps(
                    {
                        "amount": f'{ussdpatmnt.amount}00',
                        "email": f'{ussdpatmnt.email}',
                        "currency": "GHS",
                        "mobile_money": { 
                            "phone": f'{ussdpatmnt.phone}', 
                            # "phone": f'0551234987', #testing number
                            "provider": getProvider(ussdpatmnt.nw_code)
                        }})
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {key}'
                }
                response = requests.post('https://api.paystack.co/charge', headers=headers, data=data)

                print(response.json())

                try:
                    if response.json()['data']['status'] == "send_otp":
                        ussdpatmnt.level = 4
                        ussdpatmnt.reference = response.json()['data']['reference'] 
                        ussdpatmnt.save()
                        params["ussd_body"] = f'\n Enter OTP to confirm payment to vote for {contestantName}'
                        return params
                    
                    elif response.json()['data']['status'] == "pay_offline":
                        ussdpatmnt.reference = response.json()['data']['reference']
                        ussdpatmnt.save()
                        params['msg_type'] = "2"
                        params["ussd_body"] = f'\n wait to Enter your pin to vote'
                        return params
                    #test purpose will be deleted
                    # elif response.json()['data']['status'] == "success":
                    #     ussdpatmnt.reference = response.json()['data']['reference']
                    #     ussdpatmnt.save()

                except  KeyError:
                    ussdpatmnt.level = 3
                    params["ussd_body"] = f'internal error \n Enter amount to pay on {questionFound.question_text} for {contestantName}'
                    return params


            elif ussdpatmnt.level == 4:
                data = json.dumps(
                    {
                      "otp": f'{user_input["message"]}',
                      "reference": f'{ussdpatmnt.reference}'
                        })
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {key}'
                }
                response = requests.post('https://api.paystack.co/charge/submit_otp', headers=headers, data=data)

                # print(response.json())

                if response.json()['data']['status'] == "pay_offline":
                    ussdpatmnt.reference = response.json()['data']['reference']
                    ussdpatmnt.save()
                    params['msg_type'] = "2"
                    params["ussd_body"] = f'\n wait to Enter your pin to vote'
                    return params


                      
            
    if createNewProcess == True:
        print("Creating new process")
        Ussdpayment.objects.create(session_id=params['session_id'], service_code=params['service_code'],phone=params['msisdn'], nw_code = params['nw_code'],level=1)
        return processes(user_input,params)
      
        

    

def send_response(output):
    # print(output)
    return Response(output, content_type='application/json')



def capture_input(text):
    captured_text = text.replace(" ", "")
    if len(text) <= 0:
        user_input = {
            'level': 0,
            'message': captured_text
        }

    else:
        split_text = captured_text.split('*')
        user_input = {
            'split_text': split_text,
            'level': len(split_text),
            'message': captured_text
        }

    return user_input


@api_view(['POST'])
def verify_payment(request):
 
    # print(request.headers['X-Forwarded-For'])

    if request.headers['X-Forwarded-For'] in webhookIps:
        if request.data['event'] == "charge.success":
            # print(request.data['data']['reference'])

            status , data = verifyPayByRef(request.data['data']['reference'])

            # print(f'{status} ---- {data}')
            # print(res)

            if data['status'] == "success" and status == True:
                print("Payment Successful")

                #Get the reference from the database stored for the charge
                ussdpayment = Ussdpayment.objects.get(reference=request.data['data']['reference'])

                AmountPaid = request.data['data']['amount']

                ActualAmount = AmountPaid/100
                voteToAdd = ActualAmount /  0.5
                voteToAdd = int(voteToAdd)
                
                contestantCode = ussdpayment.codeinput
                contestantFound = Contestant.objects.get(code=contestantCode)
                choiceFound = Choice.objects.filter(choice_text = contestantFound.id)

                #Get choice id the user voting for
                q = ussdpayment.QuestionVotingFOr

                for c in  choiceFound:
                    if c.question.id == q:
                        c.votes += voteToAdd
                        c.save()
                        PaymentSuccess.objects.create(amount= ActualAmount , phone=ussdpayment.phone )
                        ussdpayment.delete()
                        break

                return Response({"status": "success"})
            else:
                print("Payment Failed")
                return Response({"status": "failed"}) 


 

def getProvider(providecode):
    if providecode == '01':
        return 'mtn'
    elif providecode == '02':
        return 'vod'
    elif providecode == '03' or providecode == "06":
        return 'tgo'






def verifyPayByRef(ref):
    base_url = 'https://api.paystack.co'
    path = f'/transaction/verify/{ref}'
    headers = {
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
        }
    url = base_url + path
    response = requests.get(url, headers=headers)

    # print(response.json())
   
    if response.status_code == 200:
        response_data = response.json()
        # print(response_data)
        return response_data['status'], response_data['data']
    response_data = response.json()
    return False, {"status":"unsuccessful"}



def manualverify(request):
    for x in Ussdpayment.objects.all(): 
        status , data = verifyPayByRef(x.reference)

        # print(f'{status} ---- {data}')
        # print(res)

        if data['status'] == "success" and status == True:
            print("Payment Successful")

            #Get the reference from the database stored for the charge
            ussdpayment = Ussdpayment.objects.get(reference=request.data['data']['reference'])

            AmountPaid = x.amount

            voteToAdd = AmountPaid /  0.5
            voteToAdd = int(voteToAdd)
            
            contestantCode = ussdpayment.codeinput
            contestantFound = Contestant.objects.get(code=contestantCode)
            choiceFound = Choice.objects.filter(choice_text = contestantFound.id)

            #Get choice id the user voting for
            q = ussdpayment.QuestionVotingFOr

            for c in  choiceFound:
                if c.question.id == q:
                    c.votes += voteToAdd
                    c.save()
                    PaymentSuccess.objects.create(amount= AmountPaid , phone=ussdpayment.phone )
                    ussdpayment.delete()
                    break

            return Response({"status": "success"})
        else:
            print("Payment Failed")
            return Response({"status": "failed"})