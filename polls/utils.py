import random
import string
from django.utils.text import slugify


def random_string_generator():
    return random.randint(0,10000)

def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        # We are using .lower() method for case insensitive
        # you can use instance.<fieldname> if you want to use another field
        str = "GA"
        slug = slugify(str)

    Contestant = instance.__class__
    qs_exists = Contestant.objects.filter(code=slug).exists()
    if qs_exists:
        new_slug = "{slug}{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator()
                )
        return unique_slug_generator(instance, new_slug=new_slug)
        # print(sl)
    return slug

def replace_all(text):
    rep = {
        'ı':'i',
        'ş':'s',
        'ü':'u',
        'ö':'o',
        'ğ':'g',
        'ç':'c'
    }
    for i, j in rep.items():
            text = text.replace(i, j)
    return text