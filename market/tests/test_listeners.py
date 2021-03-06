from twisted.trial import unittest
from twisted.python import log
from mock import MagicMock

from market.listeners import MessageListenerImpl
from protos.objects import PlaintextMessage

class MarketListenersTest(unittest.TestCase):

    def setUp(self):
        self.catcher = []
        observer = self.catcher.append
        log.addObserver(observer)
        self.addCleanup(log.removeObserver, observer)
        self.db = MagicMock()
        self.ws = MagicMock()

    @staticmethod
    def _create_valid_plaintext_message(handle):
        p = PlaintextMessage()
        p.sender_guid = 'test_guid'
        p.handle = handle
        p.pubkey = 'test_pubkey'
        p.subject = 'test_subject'
        p.type = 1
        p.message = 'test_message'
        p.timestamp = 10
        p.avatar_hash = 'test_avatar_hash'
        return p

    @staticmethod
    def _create_valid_message_json(handle):
        new_line = '\n'
        tab = '    '
        nlt = new_line + tab
        nldt = nlt + tab
        if handle != '':
            handle = '"handle": "'+handle+'", ' + nldt
        message = '{' + nlt + '"message": {' + nldt + \
            '"public_key": "746573745f7075626b6579", ' + nldt + handle + \
            '"sender": "746573745f67756964", ' + nldt + \
            '"timestamp": 10, ' + nldt + \
            '"avatar_hash": "746573745f6176617461725f68617368", ' + nldt + \
            '"message": "test_message", ' + nldt + \
            '"message_type": "ORDER", ' + nldt + \
            '"subject": "test_subject"' + nlt + '}\n}'
        return message

    def test_MarketListeners_notify_without_handle_success(self):
        p = self._create_valid_plaintext_message('')
        signature = 'test_signature'
        l = MessageListenerImpl(self.ws, self.db)
        l.notify(p, signature)
        self.db.messages.save_message.assert_called_with('746573745f67756964',
                                                         u'', 'test_pubkey',
                                                         u'test_subject',
                                                         'ORDER',
                                                         u'test_message', 10,
                                                         'test_avatar_hash',
                                                         signature, False)
        self.ws.push.assert_called_with(self._create_valid_message_json(''))

    def test_MarketListeners_notify_with_handle_success(self):
        p = self._create_valid_plaintext_message('test_handle')
        signature = 'test_signature'
        l = MessageListenerImpl(self.ws, self.db)
        l.notify(p, signature)
        self.db.messages.save_message.assert_called_with('746573745f67756964',
                                                         u'test_handle',
                                                         'test_pubkey',
                                                         u'test_subject',
                                                         'ORDER',
                                                         u'test_message', 10,
                                                         'test_avatar_hash',
                                                         signature, False)
        self.ws.push.assert_called_with(self._create_valid_message_json('test_handle'))
