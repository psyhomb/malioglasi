#!/usr/bin/python2.7 -tt
# Author: Milos Buncic
# Date: 29.06.2014
# Description: Search for specific article on the specific web page and send an email if you found something

from bs4 import BeautifulSoup
from random import randint
import os
import re
#import urllib2
import requests
import smtplib


### Search for specific article
#company = 'Samsung'
#model = 'Galaxy K zoom'
company = 'LG'
model = 'Nexus 5 16GB'
#company = 'Apple'
#model = 'iPhone 5s 16GB'
#company = 'Samsung'
#model = 'I8190 S3 mini'
#company = 'Apple'
#model = 'iPhone 4'
#company = 'HTC'
#model = 'Desire Z'
#company = 'Samsung'
#model = 'I9505 Galaxy S4'

### Gmail username and password
gmail_user = ''
gmail_pass = ''  # fsd4fsd32$cGFzc3dvcmQK everything after $ sign is base64 encoded password and everything before is just a random string

### Where to send an email notification (RCPT_TO must be a list data type)
FROM = 'noreply@gmail.com'
RCPT_TO = ['test@gmail.com'] # RCPT_TO = ['email1@gmail.com', 'email2@yahoo.com', 'email3@outlook.com']
SUBJECT = 'Mobilnisvet - %s %s' % (company, model)

### Web page url
url = 'http://www.mobilnisvet.com/mobilni-malioglasi'

### Where to save results (absolute path)
filename = '/tmp/malioglasi.txt'


def sendmail(text):
  """ Mail sender """
  global gmail_user
  global gmail_pass
  global FROM
  global RCPT_TO
  global SUBJECT

  MESSAGE = text

  message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (FROM, ', '.join(RCPT_TO), SUBJECT, MESSAGE)

  try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    #server.login(gmail_user, gmail_pass)
    server.login(gmail_user, gmail_pass[gmail_pass.find('$')+1:].decode('base64'))
    server.sendmail(FROM, RCPT_TO, message)
    server.close()
    print 'Mail successfully sent!'
  except:
    print 'Failed to send mail!'


def phoneInfo(url):
  """ Return a dictionary with phone properties """
  headers = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"}
  ]

  random_headers = headers[randint(0,len(headers)-1)]

  r = requests.get(url, headers=random_headers)
  r.encoding = 'utf-8'
  html = r.text

  #r = urllib2.Request(url, None, random_headers)
  #html = urllib2.urlopen(r).read()

  reg = company + r'<br\s/>' + model + r'.*?\d{3}-\d\d-\d\d\s\d\d:\d\d:\d\d'
  match = re.search(reg, html, re.DOTALL)

  if match:
    soup = BeautifulSoup(match.group())
    text = soup.get_text()

    list = [ e  for e in text.split('\n')  if e ]
    del list[:-3]

    price = list[0]
    text = list[1]
    phone = list[-1][:list[-1].index('#')]
    id = list[-1][list[-1].index('#')+1:list[-1].index('|')].strip()
    date = list[-1][list[-1].index('|')+1:].strip()

    d = {}

    d['1-Company'] = company
    d['2-Model'] = model
    d['3-Price'] = price
    d['4-Text'] = text
    d['5-Phone'] = phone
    d['6-Date'] = date
    d['7-ID'] = id

    return d


def writeToFile(filename, text):
  """ Write new data to file """
  try:
    with open(filename, 'w') as f:
      f.write(text)
  except IOError:
    print 'Error while writing to file'


def readFromFile(filename):
  """ Read old data from file and return a list """
  try:
    with open(filename, 'r') as f:
      properties_string = f.read()
      properties_list = properties_string.split('\n')
      return properties_list
  except IOError:
    print 'Error while reading from file'


def main():
  d = phoneInfo(url)

  text = ''
  for k,v in sorted(d.items()):
    text += k + ': ' + v + '\n'

  text = text.encode('utf-8')

  if os.path.isfile(filename):
    new_id = d['7-ID']
    old_id = readFromFile(filename)[-2][6:]
    if new_id != old_id:
      print 'Id %s has changed to %s, sending email about this...' % (old_id, new_id)
      sendmail(text)
      writeToFile(filename, text)
    else:
      print 'Same id %s nothing to do' % (new_id)
  else:
    sendmail(text)
    writeToFile(filename, text)


if __name__ == '__main__':
  main()
