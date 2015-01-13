# -*- coding: utf-8 -*-
#
# jQuery File Upload Plugin GAE Python Example 2.1.1
# https://github.com/blueimp/jQuery-File-Upload
#
# Copyright 2011, Sebastian Tschan
# https://blueimp.net
#
# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT
#

from __future__ import with_statement
from google.appengine.api import files, images
from google.appengine.ext import blobstore, deferred, db
from google.appengine.ext.webapp import blobstore_handlers
from tagalbumlib import photodb
from tagalbumlib import userinfo
import json
import re
import urllib
import webapp2
import time
import logging

WEBSITE = 'http://sbsydiary.appspot.com/'
UPLOADURL = '/upload/uploadimage'
MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 5000000  # bytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMBNAIL_MODIFICATOR = '=s80'  # max width / height
EXPIRATION_TIME = 300  # seconds


def cleanup(blob_keys):
    blobstore.delete(blob_keys)


class UploadImage(webapp2.RequestHandler):

    def initialize(self, request, response):
        super(UploadImage, self).initialize(request, response)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers[
            'Access-Control-Allow-Methods'
        ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
        self.response.headers[
            'Access-Control-Allow-Headers'
        ] = 'Content-Type, Content-Range, Content-Disposition'

    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        elif not ACCEPT_FILE_TYPES.match(file['type']):
            file['error'] = 'Filetype not allowed'
        else:
            return True
        return False

    def get_file_size(self, file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def write_blob(self, data, info):
        blob = files.blobstore.create(
            mime_type=info['type'],
            _blobinfo_uploaded_filename=info['name']
        )
        
#        image = images.Image(image_data=data)
#        image.im_feeling_lucky()
#        image.resize(width=980)
#        image.execute_transforms(output_encoding=images.JPEG)
#        blob = files.blobstore.create(mime_type='image/jpeg')
        with files.open(blob, 'a') as f:
            f.write(data)
        files.finalize(blob)
        return files.blobstore.get_blob_key(blob)

    def handle_upload(self):
        results = []
        blob_keys = []
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = re.sub(
                r'^.*\\',
                '',
                fieldStorage.filename
            )
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                blob_key = str(
                    self.write_blob(fieldStorage.value, result)
                )
                blob_keys.append(blob_key)
                self.insertPhoto(blob_key)
                result['deleteType'] = 'DELETE'
                result['deleteUrl'] = self.request.host_url +\
                    UPLOADURL + '?key=' + urllib.quote(blob_key, '')
                if (IMAGE_TYPES.match(result['type'])):
                    try:
                        result['url'] = images.get_serving_url(
                            blob_key,
                            secure_url=self.request.host_url.startswith(
                                'https'
                            )
                        )
                        result['thumbnailUrl'] = result['url'] +\
                            THUMBNAIL_MODIFICATOR
                    except:  # Could not get an image serving url
                        pass
                if not 'url' in result:
                    result['url'] = self.request.host_url +\
                        '/' + blob_key + '/' + urllib.quote(
                            result['name'].encode('utf-8'), '')
            results.append(result)
        deferred.defer(
            cleanup,
            blob_keys,
            _countdown=EXPIRATION_TIME
        )
        return results

    def options(self):
        pass

    def head(self):
        pass

    def get(self):
        self.redirect(WEBSITE)

    def post(self):
        if self.request.get('prequest') == 'tags':
            #logging.debug("start Tag! -> %s",self.request.get('tags'))
            self.insertTag(self.request.get('tags'))
            self.response.write("insert Done")
        elif self.request.get('request') == 'updatetagcomment':
            tagname = self.request.get('tagname')
            updatedcomment = self.request.get('updatedcomment')
            self.updateTagComment(tagname, updatedcomment)
            #logging.debug("updated tag name : %s"%tagname)
        elif self.request.get('request') == 'deletetag':
            logging.debug("delete tag")
            tagname = self.request.get('tagname')
            self.deleteTag(tagname)
        else:
            if userinfo.UserINFO() != 1:
                return -1
            if (self.request.get('_method') == 'DELETE'):
                return self.delete()
            result = {'files': self.handle_upload()}
            s = json.dumps(result, separators=(',', ':'))
            redirect = self.request.get('redirect')
            if redirect:
                return self.redirect(str(
                    redirect.replace('%s', urllib.quote(s, ''), 1)
                ))
            if 'application/json' in self.request.headers.get('Accept'):
                self.response.headers['Content-Type'] = 'application/json'
            self.response.write(s)

    def delete(self):
        key = self.request.get('key') or ''
        blobstore.delete(key)
        qu = db.GqlQuery("select * from PhotoTag where Imagekey = :1",key)
        db.delete(qu)
        s = json.dumps({key: True}, separators=(',', ':'))
        if 'application/json' in self.request.headers.get('Accept'):
            self.response.headers['Content-Type'] = 'application/json'
        self.response.write(s)

    def insertPhoto(self,file_key):
        photo = photodb.PhotoTag(parent = photodb.getKey())
        photo.author = userinfo.getUserID()
        photo.comment = ''
        taglist = self.splitTag(self.request.get('tags'))
        photo.tag = taglist
        photo.Imagekey = file_key

        key = photo.put()
        
        return key
    def splitTag(self,tags,flag = 1):
        result = []
        if tags != '':
            taglist = tags.split(',');
            for tag in taglist:
                ltag = tag
                if flag == 1:
                    ltag = tag.lower()
                    ltag = "".join(ltag.split())
                result.append(ltag)
        return result
    
    def insertTag(self,tags):
        #logging.debug("insert start")
        if tags != '':
            taglist = self.splitTag(tags)
            nametaglist = self.splitTag(tags,0)
            #logging.debug("name tag list : %s"%len(nametaglist))
            #logging.debug("tag count : %s"%len(taglist))
            
            cnt = 0
            for tag in taglist:
                #logging.debug("tag name : %s"%nametaglist[cnt])
                #logging.debug("tag : %s"%tag)
                tq = db.GqlQuery("select * from TagList where ancestor is :1 and tag = :td",photodb.getKey(),td=tag)
                if tq.count() == 0:
                    t = photodb.TagList(parent = photodb.getKey())
                    t.tag = tag
                    t.tagname = nametaglist[cnt]
                    t.comment = ''
                    t.put()
                else:
                    pass
                cnt = cnt + 1
    def updateTagComment(self, tagname, updatedcomment):
        #logging.debug("update comment : %s"%updatedcomment)
        tq = db.GqlQuery("select * from TagList where ancestor is :1 and tag = :td",photodb.getKey(),td=tagname)
        if tq.count() != 0:
            t = tq.get()
            t.comment = updatedcomment
            t.put()
    def deleteTag(self, tagname):
        #key = self.request.get('key') or ''
        #blobstore.delete(key)
        logging.debug("delete tag : %s"%tagname)
        qu = db.GqlQuery("select * from TagList where ancestor is :1 and tag = :td",photodb.getKey(),td=tagname)
        db.delete(qu)
        
                
app = webapp2.WSGIApplication(
    [
        ('/upload/uploadimage', UploadImage)
    ],
    debug=True
)
