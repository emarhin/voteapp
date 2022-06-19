from django.db import models
from .utils import unique_slug_generator
from django.dispatch import receiver


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text


class Contestant(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=200)
    code =  models.SlugField(max_length=200,unique=True ,null=True ,blank=True)

    def __str__(self):
        return f'{self.Name} {self.code}'

  




class Choice(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.ForeignKey(Contestant, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)


    def __str__(self):
        return self.choice_text.Name


class webPayment(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    amount = models.IntegerField(default=0)
    email = models.CharField(max_length=200)
    question_id = models.IntegerField(default=0)
    choice = models.CharField(max_length=200)
    reference = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.Name


        
        
@receiver(models.signals.pre_save, sender=Contestant)
def auto_slug_generator(sender, instance, **kwargs):
    """
    Creates a slug if there is no slug.
    """
    if not instance.code:
        instance.code = unique_slug_generator(instance)
        
      
   