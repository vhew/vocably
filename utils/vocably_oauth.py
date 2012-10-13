#!/bin/python
# -*- coding: utf-8 -*-

# Functions for authenticating with OAuth2 on Google's servers

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

import imaplib, json
from urllib import urlopen, urlencode

import score

def initialize_module():
    global flow, storage
    flow = flow_from_clientsecrets('config/client_secrets.json',
                                   scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://mail.google.com/',
                                   redirect_uri='http://hype.hk:8080/oauth2callback')
    storage = Storage('config/credentials')

def authorization_url():
    return flow.step1_get_authorize_url()

def authorize(code):
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
    print "Stored credentials"

def fetch_mail():
    print "Getting user profile data and email address"
    credentials = storage.get()
    params = { 'access_token': credentials.access_token }
    data = urlopen('https://www.googleapis.com/oauth2/v1/userinfo?%s' % urlencode(params)).read()
    data = json.loads(data)
    auth_str = "user=%s\1auth=Bearer %s\1\1" % (data['email'], credentials.access_token)

    print "Authenticating against GMail IMAP servers"
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_conn.authenticate('XOAUTH2', lambda x: auth_str)
    imap_conn.select('INBOX') #"[Gmail]/Sent Mail"

    # Pull email bodies
    resp, data = imap_conn.search(None, 'ALL')
    email_text = ""
    for num in data[0].split():
        resp, body = imap_conn.fetch(num, '(BODY[TEXT])')
        email_text += body[0][1]
    return email_text

def deauthorize():
    if imap_conn:
        imap_conn.close()
        imap_conn.logout()

initialize_module()
