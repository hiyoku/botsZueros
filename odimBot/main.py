import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '152817682:AAGk6k2Ilt7f1GPwrtcU8S8i5dFfNchgDcE'

BASE_URL = 'https://api.telegram.org/bot'+TOKEN+'/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            else:
                pass
        else:
            pass

        # EDITAR DAQUI
        foods = ['churrasco', 'churros', 'lanche', 'rodizio', 'pizza', 'bacon', 'salgado']
        drogas = ['cannabis', 'maconha', 'crack', 'cocaina', 'cogumelo']
        bigWords = ['porra', 'caralho', 'penis', 'piroca', 'pigoka', 'pig0ka', 'meu ovo', 'fdp', 'vsf', 'ixcroto',
                    'escroto', 'excroto', 'piruzinho']

        text = text.lower()

        if 'melhor aluno' in text:
            reply('Meu melhor aluno Marchezi!')
        elif any(s for s in drogas if s in text):
            reply('Voces nao deveriam usar essas drogas ilicitas')
        elif any(s for s in foods if s in text):
            reply('Voce deveria reeducar sua alimentacao')
        elif 'computador' in text or 'winchester' in text:
            reply('Tive que formatar o Winchester')
        elif 'Odim' in text:
            reply('O Senhor se referiu a minha pessoa?!')
        elif any(s for s in bigWords if s in text):
            reply('Cuidado com seu vocabulario, meu jovem!')

        if text == 'odimVersion': reply('Versao Herbert Richards 1.1')


        # ATE AQUI!!
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
