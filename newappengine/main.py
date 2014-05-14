#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import urllib2
import cookielib
import re
import urlparse
import sys
import webapp2
import os
import urllib
import json
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
#from facebook import Facebook
import facebook
import subprocess

FACEBOOK_USER_NAME = "username"
FACEBOOK_PASSWORD = "password"
FACEBOOK_APP_ID     = '1423052547964707'
FACEBOOK_APP_SECRET = 'a738dcf3f3fb3811d596a0bccb7b53c6'
FACEBOOK_ACCESS_TOKEN = 'CAAUOQj2ePyMBAGxOsFJs3UDFF1Yp2qy0obL6j6nYVpH66ltRK0WWFXWaEaDnZCCiRVNyatuuhxZB15B6HZArlNFLPqZBcN5nfP5lnvjOvyP9Azz0RmzxHUCF9Vu6kIcpPwwvrkbmAsN7mr4e04Pgv5jlq3SgMwuIi1HoU6f5myZCi994gS6lWxK9FTCW4T0kZD'


class MainHandler(webapp2.RequestHandler):
    def get(self):
        graph = facebook.GraphAPI()
        fb = Facebook(FACEBOOK_USER_NAME, FACEBOOK_PASSWORD)
        response = fb.login()
        if response:
            access_token = fb.get_access_token(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            album_link = fb.get_photo_albums(FACEBOOK_ACCESS_TOKEN)
            #self.response.write(str(albums)) 
            template_values = {'url': album_link}
            path = os.path.join(os.path.dirname(__file__), 'display.html')
            self.response.out.write(template.render(path, template_values))            
        else:
            self.response.write(str("Login failed."))        
        
        
class Facebook():
    def __init__(self, email, password):
        self.email = email
        self.password = password

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('Referer', 'http://login.facebook.com/login.php'),
                            ('Content-Type', 'application/x-www-form-urlencoded'),
                            ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7 (.NET CLR 3.5.30729)')]
        self.opener = opener

    def login(self):
        """
        Login to facebook.com
        """
        url = 'https://login.facebook.com/login.php?login_attempt=1'
        data = "locale=en_US&non_com_login=&email="+self.email+"&pass="+self.password+"&lsd=20TOl"
        usock = self.opener.open('http://www.facebook.com')
        usock = self.opener.open(url, data)
        if "Logout" in usock.read():
            return "Logged in."
        else:
            return False

    def get_access_token(self, app_id, app_secret):
        """
        Get application access token.
        """
        oauth_args = dict(client_id     = app_id,
                          client_secret = app_secret,
                          grant_type    = 'client_credentials')
        try:
            url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)
            request = urllib2.Request(url) 
            response = urllib2.urlopen(request)        
            access_token = str(response.read()).split('access_token=')[1]
            return access_token
        except Exception, e:
            return str(e)

    def get_user_id(self):
        """
        """
        #result = urlfetch.fetch(url = "https://graph.facebook.com/me?fields=id,name", validate_certificate=False, headers = {'use_intranet': 'yes'})
        graph = facebook.GraphAPI("CAACEdEose0cBAGTnMt6eoDEOpM1PYZBbbu2kGjBp6sVE9mb8sc6kMVZBFJoVZACatAmzJgIxFGDv3Anj8BZB5ZARhQR3B1zEdFVhuVDnnH7ytEzZAvugifms8HoAffFNTzaCOXvSZCj6XDYMlNSwfI5McPSRvqkdXhAGyc4eqZBY1SgeiU4FrTupAccmalA5wM3Gjk5b66190gZDZD") # After receiving it through Facebook
        profile = graph.get_object('me') #Would return error if there is some problem with the token
        albums = graph.get_connections("me", "albums")
        #email = profile['email'] # Get email
        #name = profile['name'] # Get name
        return albums

    def get_photo_albums(self, token):
        """
        Retrieve photo albums
        """
        try:
            graph = facebook.GraphAPI(token) # After receiving it through Facebook
            profile = graph.get_object('me') #Would return error if there is some problem with the token
            albums = graph.get_connections("me", "albums")
            link = albums['data'][0]['link']
            #email = profile['email'] # Get email
            #name = profile['name'] # Get name
            return link
        except Exception, e:
            return str(e)
    
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
