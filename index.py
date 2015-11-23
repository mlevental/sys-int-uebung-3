from bottle import route, run, static_file, template
import boto
from boto.s3.key import Key
from boto.exception import S3ResponseError
import mb


@route('/ping')
def test():
    return "Ping successful!"


@route('/Mandelbrot/generateToS3/<bucketname>')
def generateToS3(bucketname):
    w, h, it = 512, 512, 10
    mb.create_mb(w, h, it)

    s3 = boto.connect_s3()
    try:
        bucket = s3.get_bucket(bucketname)
    except S3ResponseError:
        return "bucket {bucketname} doesn't exist".format(bucketname=bucketname)

    key = Key(bucket)
    key.key = 'mb'
    key.set_contents_from_filename('mb.png')
    key.get_contents_to_filename('mbFromS3.png')

    return template('index.html', mb='/mbFromS3.png', w=w, h=h, it=it)


@route('/Mandelbrot/deleteFromS3/<bucketname>')
def deleteFromS3(bucketname):
    s3 = boto.connect_s3()

    try:
        bucket = s3.get_bucket(bucketname)
    except S3ResponseError:
        return "bucket {bucketname} doesn't exist".format(bucketname=bucketname)

    for key in bucket.list():
        key.delete()

    bucket.delete()
    return "deleted"


@route('/<mb>')
def show_mb(mb):
    return static_file(mb, root=".")


run(host='0.0.0.0', port=8080, debug=True)
