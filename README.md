# moderated-pgp-key-server

A vaguely compliant PGP key server that only serves locally trusted keys from a GnuPG `pubring.gpg` file.

## Installation

Create a new Django 1.11 project and add the `pks` and `django.contrib.humanize` applications to your `INSTALLED_APPS` and a line like `url(r'^pks/', include('pks.urls')),` to your project's `urls.py`.

Edit your `settings.py` file to specify a location for the GnuPG home directory that will be used. A suggested default would be `PKS_GPG_HOME = os.path.join(settings.BASE_DIR, 'gpg')`.

## Usage

You can send keys to the key server in the usual way, e.g. `gpg2 --keyserver https://keys.example.com/ --send-keys  2E22230EBB27C5981EBB6D1EF4CA4E9697B0282E` however they will not be immediately reflected in the key index.

To allow a key to be requested from the server you must first run e.g. `gpg2 --edit-key 2E22230EBB27C5981EBB6D1EF4CA4E9697B0282E` and change the "ownertrust" value of the key (by entering `trust`) to "fully".

It is recommended you combine this with a "CA key" that also signs all the keys you currently trust in your environment, and invite your users to import and ownertrust just the "CA key". This way they needn't manage their own local ownertrust, only the operator of the "CA" needs to make changes (assuming the users periodically update their keystores).

PGP is a bit of a nightmare.

## Caveats

It's probably not a good idea to just stuff random POST data in to `gpg`. Sandbox accordingly.

This code isn't really keyserver spec compliant, but it works OK.
