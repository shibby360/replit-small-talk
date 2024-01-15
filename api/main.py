import json
import time
import urllib
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from bson.objectid import ObjectId
import pymongo
import os
if os.path.isfile('mongouri.txt'):
  connectionstring = open('mongouri.txt').read().strip()
else:
  connectionstring = os.environ.get('MONGO_URI')
cluster = pymongo.MongoClient(connectionstring)
database = cluster['replit-small-talk']
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.WARNING)
app = Flask('messager', template_folder='ts')
suckit = SocketIO(app)
class bcolors:
  purple = '\033[95m'
  blue = '\033[94m'
  cyan = '\033[96m'
  green = '\033[92m'
  yellow = '\033[93m'
  red = '\033[91m'
  clean = '\033[0m'
  bold = '\033[1m'
  underline = '\033[4m'
memscol = database['mems']
mems = {}
for i in memscol.find():
  mems[str(i['_id'])] = i
def find(list, prop, val):
  for i in list:
    if i[prop] == val:
      return i
def getall(list, name):
  toret = []
  for i in list:
    toret.append(i[name])
  return toret
def getid(mem):
  return mems[mem]['id']
def getmemwithid(id):
  for i in mems:
    if mems[i]['id'] == id:
      return i
def addtolog(texttoadd):
  if __name__ != '__main__':
    return
  log = open('log', 'a')
  log.write(texttoadd)
  log.close()
  filelines = open('log', 'r').readlines()
  if len(filelines) > 301:
    writelog = open('log', 'w')
    filelines.pop(0)
    writelog.write(''.join(filelines))
    writelog.close()
def getidfromusername(username):
  for i in mems:
    if i['username'] == username:
      return i['_id']
def getdocbyusername(username):
  return memscol.find_one({'username':username})
def exclude(dict_, excl):
  end = {}
  for i in dict_:
    if i not in excl:
      end[i] = dict_[i]
  return end
guildscol = database['guilds']
guilds = {}
for i in guildscol.find():
  guilds[str(i['_id'])] = i
def save():
  for i in mems:
    memscol.update_one({'_id':ObjectId(i)}, {"$set":mems[i]})
  for i in guilds:
    guildscol.update_one({'_id':ObjectId(i)}, {"$set":guilds[i]})
  assignidcol.update_one({'actualdoc':True}, {"$inc": {'val':1}})
assignidcol = database['id']
assignid = assignidcol.find_one({'actualdoc':True})['val']
@app.route('/')
def homepager():
  return render_template('start.html')

@app.route('/users/<name>')
def getMem(name):
  body = getdocbyusername(name)['status'] if getdocbyusername(name) else 'User not found.'
  return render_template('user.html', user=name, userstatus=body)#, userpfp=mems[name]['pfp'])

@app.route('/users')
def getUsers():
  toret = mems.copy()
  for i in toret:
    toret = exclude(toret[i], ['_id', 'password'])
  return toret

@app.route('/allusers/<guildid>')
def allusers(guildid):
  return {'mems':find(guilds, 'id', int(guildid))['members']}

@app.route('/sendmessage', methods=['GET'])
def sendmessage_withGET():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  global assignid
  msgtosend = {'author':form['user'], 'content':form['message'], 'timesent':form['time'], 'id':assignid}
  assignid += 1
  for guild in guilds:
    if guilds[guild]['id'] == int(form['guildid']):
      guilds[guild]['messages'].append(msgtosend)
  save()
  addtolog(form['user'] + f' sent a message.({time.ctime(time.time())})\n')
  return str(assignid-1)

@app.route('/getmessages', methods=['GET'])
def getmessages_withGET():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  for guild in guilds:
    if guild['id'] == int(form['guildid']):
      return {'messages':guild['messages']}

@app.route('/loggedin', methods=['GET'])
def loggedin_withGET():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  userdoc = getdocbyusername(form['user'])
  if userdoc:
    if form['pwd'] == userdoc['password']:
      addtolog(form['user'] + f' logged in.({time.ctime(time.time())})\n')
      userdoc['online'] = True
      toret = exclude(dict(userdoc), ['_id'])
      # del toret['pfp']
      return toret
    else:
      return 'invalid auth'
  return 'Not found user.'

@app.route('/delmsg', methods=['GET'])
def delmsg():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  for guild in guilds:
    if guilds[guild]['id'] == int(form['guildid']):
      messages = guilds[guild]['messages']
      if form['purge'] == 'yes':
        messages = []
        guilds[guild]['messages'] = messages
        continue
      newmess = messages[:]
      for mess in newmess:
        if mess['id'] == int(form['id']):
          messages = [i for i in messages if i['id']!=mess['id']]
      guilds[guild]['messages'] = messages
  save()
  return ''

@app.route('/makeprof', methods=['GET'])
def makeprof():
  global mems
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global assignid
  mems[form['name'].replace('+', ' ')] = {'status':'Click to change status', 'password':form['pwd'], 'id':assignid,'guilds':[], 'pfp':open('base64default').read(), 'location':{'flag':requests.get('https://api.ipdata.co/'+form['ip']+'?api-key=eef41dccbe52de3cd1cdae1763eea81fb012e36645cbeaab1390e0fc').json()['flag']}}
  assignid += 1
  save()
  addtolog(form['name'] + f' created their profile.({time.ctime(time.time())})\n')
  toret = mems[form['name'].replace('+', ' ')].copy()
  return toret

@app.route('/editmsg', methods=['GET'])
def editmsg():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  for guild in guilds:
    if guilds[guild]['id'] == int(form['guildid']):
      messages = guilds[guild]['messages']
      for mess in messages:
        if mess['id'] == int(form['id']):
          mess['content'] = form['new']
      guilds[guild]['messages'] = messages
  save()
  return ''

@app.route('/guilds/<guildid>', methods=['GET'])
def allguilds(guildid):
  fullguild = guildscol.find_one({'id':int(guildid)})
  fullguildret = exclude(fullguild, ['_id'])
  guildmems = []
  for i in fullguild['members']:
    for j in mems:
      if i == getid(j):
        retobj = mems[j].copy()
        retobj = exclude(retobj, ['_id', 'password'])
        retobj['name'] = j
        guildmems.append(retobj)
  return render_template('messages.html', fullguild=fullguildret, fullguildname=fullguild['name'], guildmems=guildmems)

@app.route('/makeguild')
def makeguild():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  global mems
  global assignid
  guilds.append({'name':form['name'], 'invite code':form['code'], 'members':[form['owner']], 'id':assignid, 'messages':[], 'owner':form['owner']})
  mems[getmemwithid(int(form['owner']))]['guilds'].append(assignid)
  assignid += 1
  save()
  return ''

@app.route('/getAGuild/<id>', methods=['GET'])
def getAGuild(id):
  guildtoret = guildscol.find_one({'id':int(id)})
  guildtoret = exclude(guildtoret, ['_id'])
  return guildtoret

@app.route('/invite/<code>')
def invite(code):
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  for guild in guilds:
    if guild['invite code'] == code:
      for mem in mems:
        if mems[mem]['id'] == int(form['userid']):
          data = mems[mem].copy()
          data['role'] = 'user'
          guild['members'].append(int(form['userid']))
          mems[mem]['guilds'].append(guild['id'])
  save()
  return ''

@app.route('/editprof/<toedit>/<value>/<username>')
def editprof(toedit, value, username):
  toedit = urllib.parse.unquote(toedit).replace('+', ' ')
  value = urllib.parse.unquote(value).replace('+', ' ')
  username = urllib.parse.unquote(username).replace('+', ' ')
  if toedit == 'online':
    value = eval(value)
  getdocbyusername(username)[toedit] = value
  save()
  return exclude(getdocbyusername(username), ['_id'])

@app.route('/widget/<guildid>')
def widget(guildid):
  return render_template('frame.html', guildID=guildid, messages={'messages':find(guilds, 'id', int(guildid))['messages']})

@app.route('/userframe/<theme>/<userid>')
def userframe(theme, userid):
  for i in mems:
    if mems[i]['id'] == int(userid):
      user = mems[i].copy()
      user['name'] = i
  return render_template('userframe.html', user=exclude(user, ['_id']), theme=theme)

@app.route('/kick', methods=['GET'])
def kick_withGET():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  global mems
  for guild in guilds:
    if guild['id'] == int(form['guildid']) and int(form['userid']) in guild['members']:
      guild['members'].remove(int(form['userid']))
      mems[form['username']]['guilds'].remove(int(form['guildid']))
  save()
  return 'booooteddd'
        
@suckit.on('updmsg')
def updmsg(data):
  for guild in guilds:
    if guilds[guild]['id'] == int(data['guildid']):
      emit('updtmsg', {'guildid':data['guildid']}, broadcast=True)

# @suckit.on('editpfp')
# def editpfp(data):
#   mems[data['username']]['pfp'] = data['dataurl']
#   db['mems'] = mems

if __name__ == '__main__':
  suckit.run(app)