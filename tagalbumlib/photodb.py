from google.appengine.ext import db
from google.appengine.ext import blobstore

class PhotoTag(db.Model):
    author = db.StringProperty()
    comment = db.StringProperty(multiline=True)
    tag = db.StringListProperty()
    Imagekey = blobstore.BlobReferenceProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class TagList(db.Model):
    tag = db.StringProperty()
    tagname = db.StringProperty()
    comment = db.StringProperty()
    tagcate = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class TagCategory(db.Model):
    tagcate = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

def getKey(keyname = 'sysbdiary'):
    return db.Key.from_path('PhotoTag', keyname)
