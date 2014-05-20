import os
import jinja2
import webapp2

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import files
from tagalbumlib import photodb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class UploadForm(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload/uploadimage')

        template_values = {
            'upload_url': upload_url,
        }

        template = JINJA_ENVIRONMENT.get_template('templates/uploadform.html')
        self.response.write(template.render(template_values))

class UploadImage(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):        
        upload_files = self.get_uploads('filesToUpload')
        for blob_info in upload_files:
            blob_key = blob_info.key()

            f_key = self.ImageProcessing(blob_key,blob_info)
            
            self.insertPhoto(f_key)

#        self.redirect('/')

    def ImageProcessing(self,blob_key,blob_info):
        # Resize the image
        image = images.Image(blob_key=blob_info.key())
        image.im_feeling_lucky()
        image.execute_transforms(output_encoding=images.JPEG)

        if image.width > 1024:
            image.resize(width=1024)
            thumbnail = image.execute_transforms(output_encoding=images.JPEG)
            # Save Resized Image back to blobstore
            file_name = files.blobstore.create(mime_type='image/jpeg')
            with files.open(file_name, 'a') as f:
                f.write(thumbnail)
            files.finalize(file_name)
            # Remove the original image
            blobstore.delete(blob_info.key())
            # Serve the resized image
            f_key = files.blobstore.get_blob_key(file_name)
            return f_key
        else:
            return blob_key
    def insertPhoto(self,file_key):
        photo = photodb.PhotoTag(parent = photodb.getKey())
        photo.author = 'anomy'
        photo.comment = ''
        photo.tag = self.request.get('taglist')
        photo.Imagekey = file_key

        self.response.out.write("fkey = %s<br/>"%file_key)
        self.response.out.write("photofkey = %s<br/>"%photo.Imagekey.key())
        key = photo.put()
        self.response.out.write("filename = %s<br/>"%key)
        self.insertTag(photo.tag)
    def insertTag(self,tags):
        if tags != '':
            taglist = tags.split(',');
            for tag in taglist:
                tq = db.GqlQuery("select * from TagList where ancestor is :1 and tag = :td",photodb.getKey(),td=tag)

                self.response.out.write("tlist = %s<br/>"%tag)
                if tq.count() == 0:
                    t = photodb.TagList(parent = photodb.getKey())
                    t.tag = tag
                    t.comment = ''
                    t.put()
                else:
                    self.response.out.write("%s is in db data<br/>"%tag)

app = webapp2.WSGIApplication([
    ('/upload/uploadimage', UploadImage),
    ('/upload/uploadform',UploadForm)
], debug=True)
