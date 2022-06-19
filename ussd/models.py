from django.db import models
from django.dispatch import receiver
import random
import string

# Create your models here.

class Ussdpayment(models.Model):
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=50)
    service_code = models.CharField(max_length=50)
    nw_code = models.CharField(max_length=50 , blank=True,null=True)

    QuestionVotingFOr = models.IntegerField(default=0)
    level = models.IntegerField(blank=True,null=True)
    codeinput = models.CharField(max_length=50)


    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=50,null=True ,blank=True)
    amount = models.FloatField(blank=True,null=True)


    otp = models.CharField(max_length=50,null=True ,blank=True)
    reference = models.CharField(max_length=50,blank=True,null=True)

   


class PaymentSuccess(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField(default=0)
    phone = models.CharField(max_length=200)

    def __str__(self):
        return self.phone


#level1 - display what contestant is competing for
#level2 - Get what question the user is voting for
#level3 - Enter Amount to pay - payment
#level4 - Enter otp






@receiver(models.signals.pre_save, sender=Ussdpayment)
def auto_slug_generator(sender, instance, **kwargs):
    """
    Creates a slug if there is no slug.
    """
    if not instance.email:
        instance.email = random_char(7)+"@gmail.com"



def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))