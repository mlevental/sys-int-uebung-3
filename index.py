#!/usr/bin/python
# -*- coding:utf-8 -*-

from bottle import route, run, static_file, template
import boto3
from boto3 import *
import mb

IMG_NAME = "mb.png"


@route('/ping')
def test():
    return "Ping successful!"


@route('/Mandelbrot/generateToS3/<bucketname>')
def generateToS3(bucketname):
    w, h, it = 512, 512, 10
    mb.create_mb(w, h, it)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)

    if not bucket in s3.buckets.all():
        bucket.create()
    bucket.upload_file(IMG_NAME, IMG_NAME)

    imgUrl = s3.meta.client.generate_presigned_url('get_object', Params={'Bucket': bucketname, 'Key': IMG_NAME})
    return template('index.html', w=w, h=h, it=it, imgUrl=imgUrl)


@route('/Mandelbrot/deleteFromS3/<bucketname>')
def deleteFromS3(bucketname):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)

    if not bucket in s3.buckets.all():
        return 'Bucket "{bucketname}" existiert nicht!'.format(bucketname=bucketname)

    for key in bucket.objects.all():
        key.delete()
    bucket.delete()

    return "Bucket und alle Objekte gelöscht!"


run(host='0.0.0.0', port=8080, debug=True)
