#!/usr/bin/python2.7 -tt
# Author: Milos Buncic
# Date: 29.06.2014
# Description: Search for specific article on the specific web page and send an email if you found something

import os
import sys
import re
import json
import smtplib
#import urllib2
import requests
from bs4 import BeautifulSoup
from ConfigParser import SafeConfigParser
from random import randint


### Config file location
config_filename = '/etc/malioglasi.conf'

### Web page url
url = 'http://www.mobilnisvet.com/mobilni-malioglasi'

### JSON with all entries
filename = '/tmp/mobilnisvet.json'


def sendmail(text, username, password, sender, recipient, subject):
  """ Mail sender """
  MESSAGE = text

  message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (sender, ', '.join(recipient), subject, MESSAGE)

  try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    #server.login(username, password)
    server.login(username, password[password.find('$')+1:].decode('base64'))
    server.sendmail(sender, recipient, message)
    server.close()
    print 'Mail successfully sent!'
  except:
    print 'Failed to send an email!'


def phoneInfo(url, company, model):
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
    soup = BeautifulSoup(match.group(), "lxml")
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


def readConfig(config_filename, section):
  """ Parse config file and return dictionary """
  parser = SafeConfigParser()
  parser.read(config_filename)

  d = {}
  for k,v in parser.items(section):
    d[k] = v

  return d


def keywordMatch(text, keywords=[]):
  """ Check if keywords are included in the text """
  for keyword in keywords:
    if re.search(keyword, text, re.IGNORECASE):
      return True
  return False


def writeToFile(filename, text):
  """ Write new data to file """
  try:
    with open(filename, 'w') as f:
      f.write(json.dumps(text, indent=4, ensure_ascii=False, sort_keys=True).encode('utf-8'))
    print 'Datastore %s has been updated' % filename
  except IOError:
    print 'Error while writing to file'


def readFromFile(filename):
  """ Read old data from file and return a dictionary """
  try:
    with open(filename, 'r') as f:
      return json.load(f)
  except IOError:
    print 'Error while reading from file'


def main():
  if not os.path.isfile(config_filename):
    print 'Cannot find configuration file ' + config_filename
    sys.exit(1)

  email = readConfig(config_filename, 'Email')
  filters = readConfig(config_filename, 'Filters')
  search = readConfig(config_filename, 'Search')

  username = email['username']
  password = email['password']
  sender = email['sender']
  recipient = email['recipient'].split()

  bkw = filters['blacklisted_keywords'].split()
  wkw = filters['whitelisted_keywords'].split()

  if os.path.isfile(filename):
    updated = False
    d_final = readFromFile(filename)

    # Remove stale keys from datastore if there is any
    for k in d_final.keys():
      if k not in search.keys():
        del d_final[k]
        updated = True
  else:
    d_final = {}

  # Go through every 'model' and 'name' from configuration file
  for m,n in search.items():

    company = n.split()[0]
    model = ' '.join(n.split()[1:])
    subject = 'Mobilnisvet - %s %s' % (company, model)

    d = phoneInfo(url, company, model)

    if not d:
      print 'Cannot find model %s %s' % (company, model)
      continue

    text = ''
    for k,v in sorted(d.items()):
      text += k + ': ' + v + '\n'

    text = text.encode('utf-8')

    # Check if there is any blacklisted or whitelisted keywords in the text
    if filters['black_enabled'] == 'yes' and filters['white_enabled'] == 'no' and keywordMatch(text, bkw):
      continue
    elif filters['white_enabled'] == 'yes' and filters['black_enabled'] == 'no' and not keywordMatch(text, wkw):
      continue
    elif filters['black_enabled'] == 'yes' and filters['white_enabled'] == 'yes' and keywordMatch(text, bkw):
      continue

    # Enable notification if email is enabled and there is none unwanted keywords
    if email['enabled'] == 'yes':
      notify = True
    else:
      notify = False

    if d_final and m in d_final:
      new_id = d['7-ID']
      old_id = d_final[m]['7-ID']
      if new_id != old_id:
        print 'Id %s has changed to %s' % (old_id, new_id)
        updated = True
        d_final[m] = d
        if notify: sendmail(text, username, password, sender, recipient, subject)
      else:
        print 'Same id %s nothing to do' % (new_id)
    else:
      updated = True
      d_final[m] = d
      if notify: sendmail(text, username, password, sender, recipient, subject)

  if updated:
    writeToFile(filename, d_final)

if __name__ == '__main__':
  main()
