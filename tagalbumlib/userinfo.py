import os
import webapp2
import urllib
from google.appengine.api import users
from tagalbumlib import photoaccount
from google.appengine.ext.webapp.util import run_wsgi_app

PROVIDERMAINURI = 'https://www.google.com/accounts/o8/id'
providers = {
    'Google'   : 'https://www.google.com/accounts/o8/id',
    'Yahoo'    : 'yahoo.com',
    'MySpace'  : 'myspace.com',
    'AOL'      : 'aol.com',
    'MyOpenID' : 'myopenid.com'
    # add more here
}
def getUserID():
    user = users.get_current_user()
    if user:
        return user.user_id()
    else:
        return "anoy"
    
def UserINFO():
    user = users.get_current_user()
    if user:  # signed in already
        for num in range(0,2):
            if int(user.user_id()) == int(photoaccount.AccountAuthID[num]) and str(user.federated_identity()) == str(photoaccount.AccountAuthFED[num]):
                return 1
        return 2 #2 -> must change '2' move to server
    else:     # let user choose authenticator
        return 0

def printLoginPage(self):
        self.response.out.write('Hello world! Sign in at: ')
        for name, uri in providers.items():
            self.response.out.write('[<a href="%s">%s</a>]' % (
                users.create_login_url(federated_identity=uri), name))

def printacc(self):
        user = users.get_current_user()
        if user:
            self.response.out.write("<br/> email : ")
            self.response.out.write(user.email())
            self.response.out.write("<br/> id : ")
            self.response.out.write(user.user_id())
            self.response.out.write("<br/> fed : ")
            self.response.out.write(user.federated_identity())
        else:
            self.response.out.write('[<a href="%s">Login</a>]' % users.create_login_url(federated_identity=PROVIDERMAINURI))
