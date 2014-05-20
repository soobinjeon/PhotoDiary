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
import os
import webapp2
import urllib
import jinja2
import json
import logging

from google.appengine.ext import db
from google.appengine.api import users
from tagalbumlib import photodb
from tagalbumlib import userinfo
from google.appengine.ext.webapp.util import run_wsgi_app

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
class album:
    photo = None
    tag = None
    cnt = None

    def __init__(self, _photo, _tag, _cnt):
        self.photo = _photo
        self.tag = _tag
        self.cnt = _cnt
        
    def __lt__(self, other):
        return self.cnt > other.cnt

class MainHandler(webapp2.RequestHandler):
    def post(self):
        if self.request.get('request') == 'photos':
            results = []
            plist = self.viewPhotosbyTag(self.request.get('photo_tag'))
            logging.debug("plist = %s"%len(plist))
#            for num in range(photosp,photoep):
            for ph in plist:
                result = {"imagekey" : str(ph.photo.Imagekey.key()),
                          "imagecomment" : ph.photo.comment,
                          "tag" : ph.tag.tag,
                          "tagname" : ph.tag.tagname,
                          "tagcomment" : ph.tag.comment,
                          "isadmin" : userinfo.UserINFO()}

                results.append(result)
            self.response.write(json.dumps(results))
        
    def get(self):
        tags = self.viewTaglist()

        template_values = {
            'tags': tags,
            'uinfo': userinfo.UserINFO(),
            'feduri': users.create_login_url(federated_identity=userinfo.PROVIDERMAINURI),
            'logout': users.create_logout_url('/'),
        }
        template = JINJA_ENVIRONMENT.get_template('/templates/index.html')
        self.response.write(template.render(template_values))

    def viewTaglist(self):
        tqs = db.GqlQuery("select * from TagList where ancestor is :1 order by date desc",photodb.getKey())
        return tqs
    
    def findTag(self, tag):
        tqs = db.GqlQuery("select * from TagList where ancestor is :1 and tag = :td",photodb.getKey(),td=tag)
        if tqs.count() != 0:
            return tqs[0]
        else:
            return None
        
    def viewPhotosbyTag(self, tag = ''):
#        photos = db.GqlQuery("select * from PhotoTag "
#                             "where ancestor is:1 order by date desc",
#                             photodb.getKey())
        photolist = []
        if tag != '':
            photos = db.GqlQuery("select * from PhotoTag "
                                 "where ancestor is:1 and tag = :td order by date asc",
                                 photodb.getKey(),td=tag)
            tagdb = self.findTag(tag)
            pcnt = 0
            for photo in photos:
                photolist.append(album(photo,tagdb,pcnt))
                pcnt = pcnt + 1
        else:
            tlist = self.viewTaglist()
            for t1 in tlist:
                logging.debug("tname : %s"%t1.tag)
                photos = db.GqlQuery("select * from PhotoTag "
                                     "where ancestor is:1 and tag = :td order by date desc",
                                     photodb.getKey(),td=t1.tag).fetch(1)
                pcnt = 0
                for photo in photos:
                    photolist.append(album(photo,t1,photo.date))
                    pcnt = pcnt + 1
                    
        photolist.sort()
#        if tag != '':
#            pcnt = 0
#            for photo in photos:
#                if photo.tag.find(tag) != -1:
#                    photolist.append(album(photo,self.findTag(tag),pcnt))
#                pcnt = pcnt + 1
#        else:
#            tlist = self.viewTaglist()
#            for tl in tlist:
#                pcnt = 0
#                for photo in photos:
#                    if photo.tag.find(tl.tag) != -1:
#                        photolist.append(album(photo,tl,pcnt))
#                        break;
#                    pcnt = pcnt + 1
#        photolist.sort()
        return photolist

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
