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
  log = open('log', 'a')
  log.write(texttoadd)
  log.close()
  filelines = open('log', 'r').readlines()
  if len(filelines) > 301:
    writelog = open('log', 'w')
    filelines.pop(0)
    writelog.write(''.join(filelines))
    writelog.close()
guildscol = database['guilds']
guilds = {}
for i in guildscol.find():
  guilds[str(i['_id'])] = i
def save():
  for i in mems:
    memscol.update_one({'_id':ObjectId(i)}, {"$set":mems[i]})
  for i in guilds:
    guildscol.update_one({'_id':ObjectId(i)}, {"$set":guilds[i]})
@app.route('/')
def homepager():
  return render_template('start.html', id=request.headers['X-Replit-User-Id'], name=request.headers['X-Replit-User-Name'])

@app.route('/users/<name>')
def getMem(name):
  body = mems[name]['status'] if name in mems else 'User not found.'
  return render_template('user.html', user=name, userstatus=body, userpfp=mems[name]['pfp'])

@app.route('/users')
def getUsers():
  return mems

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
  msgtosend = {'author':form['user'], 'content':form['message'], 'timesent':form['time'], 'id':db['id']}
  db['id'] += 1
  for guild in guilds:
    if guild['id'] == int(form['guildid']):
      guild['messages'].append(msgtosend)
  db['guilds'] = guilds
  addtolog(form['user'] + f' sent a message.({time.ctime(time.time())})\n')
  return str(db['id']-1)

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
  if form['user'] in mems:
    if form['pwd'] == mems[form['user']]['password']:
      addtolog(form['user'] + f' logged in.({time.ctime(time.time())})\n')
      mems[form['user']]['online'] = True
      if '[Bot]' in form['user']:
        return find(bots, 'name', form['user'].replace('[Bot]', ''))
      toret = dict(mems[form['user']]).copy()
      del toret['pfp']
      return toret
    else:
      return 'invalid auth'
  elif form['replit'] != 'undefined':
    return requests.get('https://small-talk.shivankchhaya.repl.co/makeprof?name=' + form['user'] + '&pwd=' + form['pwd'] + '&bot=no&ip=99.99.999.999').text
  return 'Not found user.'

@app.route('/delmsg', methods=['GET'])
def delmsg():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  for guild in guilds:
    if guild['id'] == int(form['guildid']):
      messages = guild['messages']
      if form['purge'] == 'yes':
        messages = []
        guild['messages'] = messages
        continue
      newmess = messages[:]
      for mess in newmess:
        if mess['id'] == int(form['id']):
          messages = [i for i in messages if i['id']!=mess['id']]
      guild['messages'] = messages
  db['guilds'] = guilds
  return ''

@app.route('/makeprof', methods=['GET'])
def makeprof():
  global mems
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  form['bot'] = form['bot'].replace('no', '')
  mems[form['name'].replace('+', ' ')] = {'status':'Click to change status', 'password':form['pwd'], 'id':db['id'], 'bot':form['bot'], 'guilds':[], 'pfp':open('base64default').read(), 'location':{'flag':requests.get('https://api.ipdata.co/'+form['ip']+'?api-key=eef41dccbe52de3cd1cdae1763eea81fb012e36645cbeaab1390e0fc').json()['flag']}}
  db['id'] += 1
  db['mems'] = mems
  mems = json.loads(db.get_raw('mems'))
  if form['bot'] == '[Bot]':
    bots.append({'name':form['name'], 'website':form['botsite'], 'prefix':form['botfix']})
    db['bots'] = bots
  addtolog(form['name'] + f' created their profile.({time.ctime(time.time())})\n')
  if '[Bot]' in form['name']:
    return find(bots, form['name'].replace('[Bot]', ''))
  toret = mems[form['name'].replace('+', ' ')].copy()
  return toret

@app.route('/getBots', methods=['GET'])
def getBots():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  for guild in guilds:
    if guild['id'] == int(form['guildid']):
      return {'bots':guild['bots']}

@app.route('/editmsg', methods=['GET'])
def editmsg():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  for guild in guilds:
    if guild['id'] == int(form['guildid']):
      messages = guild['messages']
      for mess in messages:
        if mess['id'] == int(form['id']):
          mess['content'] = form['new']
      guild['messages'] = messages
  db['guilds'] = guilds
  return ''

@app.route('/guilds/<guildid>', methods=['GET'])
def allguilds(guildid):
  fullguild = find(guilds, 'id', int(guildid))
  guildmems = []
  for i in fullguild['members']:
    for j in mems:
      if i == getid(j):
        retobj = mems[j].copy()
        del retobj['password']
        retobj['name'] = j
        guildmems.append(retobj)
  return render_template('messages.html', fullguild=fullguild, fullguildname=fullguild['name'], guildmems=guildmems)

@app.route('/makeguild')
def makeguild():
  form = urllib.parse.parse_qs(request.query_string)
  for i in form.copy():
    form[str(i)[2:-1]] = str(form[i][0])[2:-1]
    del form[i]
  global guilds
  global mems
  guilds.append({'name':form['name'], 'invite code':form['code'], 'members':[form['owner']], 'id':db['id'], 'messages':[], 'bots':[], 'owner':form['owner']})
  mems[getmemwithid(int(form['owner']))]['guilds'].append(db['id'])
  db['id'] += 1
  db['guilds'] = guilds
  db['mems'] = mems
  return ''

@app.route('/getAGuild/<id>', methods=['GET'])
def getAGuild(id):
  return find(guilds, 'id', int(id))

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
  db['guilds'] = guilds
  return ''
  
@app.route('/botmessage/<guildid>')
def botmessage(guildid):
  for guild in guilds:
    if guild['id'] == int(guildid):
      # suckit.emit('updtmsg', {'guildid':guildid}, broadcast=True)
      pass
  return ''

@app.route('/editprof/<toedit>/<value>/<username>')
def editprof(toedit, value, username):
  toedit = urllib.parse.unquote(toedit).replace('+', ' ')
  value = urllib.parse.unquote(value).replace('+', ' ')
  username = urllib.parse.unquote(username).replace('+', ' ')
  if toedit == 'online':
    value = eval(value)
  mems[username][toedit] = value
  db['mems'] = mems
  return mems[username]

@app.route('/widget/<guildid>')
def widget(guildid):
  return render_template('frame.html', guildID=guildid, messages={'messages':find(guilds, 'id', int(guildid))['messages']})

@app.route('/userframe/<theme>/<userid>')
def userframe(theme, userid):
  for i in mems:
    if mems[i]['id'] == int(userid):
      user = mems[i].copy()
      user['name'] = i
  return render_template('userframe.html', user=user, theme=theme)

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
  db['mems'] = mems
  db['guilds'] = guilds
  guilds = json.loads(db.get_raw('guilds'))
  mems = json.loads(db.get_raw('mems'))
  return 'booooteddd'
        
@suckit.on('updmsg')
def updmsg(data):
  for guild in guilds:
    if guild['id'] == int(data['guildid']):
      emit('updtmsg', {'guildid':data['guildid']}, broadcast=True)

@suckit.on('editpfp')
def editpfp(data):
  mems[data['username']]['pfp'] = data['dataurl']
  db['mems'] = mems

@suckit.on('botmessage')
def botmessagecame(data):
  rq = requests.get(data.botinfo.website+'/event/message?message='+data.message+'&id='+data.msgid+'&time='+data.time+'&guild='+data.guildid)
  print('a bot message arrived', 'data', data)
  
if __name__ == '__main__':
  suckit.run(app)