from datetime import datetime

from django import template
from django.utils import timezone

register = template.Library()

def key_algo(value):
	algorithms = {
		0: 'Unknown',
		1: 'RSA encrypt and sign',
		2: 'RSA encrypt only',
		3: 'RSA sign only',
		16: 'ElGamal encrypt only',
		17: 'DSA',
		18: 'ECDH',
		19: 'ECDSA',
		20: 'ElGamal encrypt and sign',
		21: 'DH'
	}
    
	return algorithms.get(int(value), 'Unknown')

def first_word(value):
    return value.split()[0]

def timestamp_to_datetime(value):
    try:
        return timezone.make_aware(datetime.fromtimestamp(int(value)), timezone.get_current_timezone())
    except:
        return ''

register.filter('key_algo', key_algo)
register.filter('first_word', first_word)
register.filter('timestamp_to_datetime', timestamp_to_datetime)
