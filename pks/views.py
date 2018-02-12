import os

from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import gnupg

def index(request):
    return render(request, 'pks/index.html')

@require_http_methods(["GET"])
def lookup(request):
    gpg = gnupg.GPG(homedir=os.path.join(settings.BASE_DIR, 'gpg'), options=['--export-options export-minimal=yes'])
    operation = request.GET.get('op', 'index')
    options = request.GET.get('options', '').lower().split(',')
    search = request.GET.get('search', '').lower()
    keys = [key for key in gpg.list_keys() if key['trust'] not in ('r', 'e') and key['ownertrust'] == 'f'] # remove expired and revoked from the list, only allow keys trusted in the keyring

    if 'search' in request.GET:
        if search.startswith('0x') and len(search) == 42: # full fingerprint
            # XXX: at the moment due to a bug in the gnupg library this is ugly...
            search = search[2:]
            key_ascii = gpg.export_keys(search)
            result = gpg.import_keys(key_ascii)
            try:
                if len([result for result in result.results if 'fingerprint' in result]) != 1:
                    raise
                validated_fingerprint = result.results[0]['fingerprint']
                validated_keyid = validated_fingerprint[-16:].lower()
                keys = [key for key in keys if key['keyid'].lower() == validated_keyid]
                if len(keys) != 1:
                    raise
            except:
                return HttpResponseServerError()
        elif search.startswith('0x') and len(search) == 18: # long key id
            search = search[2:]
            keys = [key for key in keys if key['keyid'].lower() == search]
        elif search.startswith('0x') and len(search) == 10: # short key id, unsupported
            return HttpResponseBadRequest()
        else: # search the UIDs
            keys = [key for key in keys if search in ' '.join(key['uids']).lower()]

    if operation in ('index', 'vindex'):
        if 'mr' in options:
            result = [['info', '1', str(len(keys))]]
            for key in keys:
                result.append(['pub', key['keyid'], key['algo'], key['length'], key['date'], key['expires'], ''])
                for uid in key['uids']:
                    result.append(['uid', uid, key['date'], key['expires'], ''])
            return HttpResponse('\n'.join([':'.join(x) for x in result]), content_type='text/plain')
        else:
            return render(request, 'pks/lookup_index.html', {'keys': keys, 'search': search})

    elif operation == 'get':
        if len(keys) > 1:
            return HttpResponseServerError()
        elif len(keys) == 0:
            return HttpResponseNotFound()
        key = keys[0]
        key_ascii = gpg.export_keys(key['fingerprint'])

        if 'mr' in options:
            response = HttpResponse(key_ascii)
            response['Content-Disposition'] = 'attachment; filename="public-key"'
            return response
        else:
            return render(request, 'pks/lookup_get.html', {'key': key, 'key_ascii': key_ascii})
    
    else:
        return HttpResponseBadRequest()

@csrf_exempt
@require_http_methods(["POST"])
def add(request):
    gpg = gnupg.GPG(homedir=os.path.join(settings.BASE_DIR, 'gpg'), options=['--import-options import-minimal=yes import-clean=yes'])
    result = gpg.import_keys(request.POST['keytext'])
    print(result.results)
    return HttpResponse(result.summary())
