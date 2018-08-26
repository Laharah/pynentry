"""practice with metaprogramming"""

import subprocess
import os
import sys
import re
import locale


class PinEntryError(Exception):
    def __init__(self, code, message, last_cmd):
        self.code = code
        self.message = message
        self.last_cmd = last_cmd

    def __str__(self):
        s = f'call "{self.last_cmd}" failed with error "{self.code} {self.message}"'
        return s


class PinOption:
    '''descriptor that calls the correct command to adjust pinentry behavior
    when the class attribute is set'''

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)  # manip dict directly to stop recursion

    def __set__(self, instance, value):
        if value is None:
            return
        instance.__dict__[self.name] = value
        resp = instance.call('{}{}'.format(
            instance.__class__.__dict__['_attribs'][self.name], value))


class PinMeta(type):
    '''metaclass that uses the attribute list to create descriptors for each one.'''

    def __new__(cls, name, bases, namespace):
        for a in namespace['_attribs']:
            namespace[a] = PinOption()
        return super().__new__(cls, name, bases, namespace)


class PynEntry(metaclass=PinMeta):
    '''
    Wrapper for pythonic interaction with pinentry, credit to mijikai
    '''
    '''_attribs: a list of attributes and their commands, used by the descriptors'''
    _attribs = {
        'description': 'SETDESC ',
        'prompt': 'SETPROMPT ',
        'title': 'SETTITLE ',
        'ok_text': 'SETOK ',
        'cancel_text': 'SETCANCEL ',
        'not_ok_text': 'SETNOTOK ',
        'error_text': 'SETERROR ',
        'tty_name': 'OPTION ttyname=',
        'tty_type': 'OPTION ttytype=',
        'locale': 'OPTION lc-ctype=',
    }

    def __init__(self, executable='pinentry', timeout=0, display=None, global_grab=True):
        args = [executable]
        if not global_grab:
            args.append('--no-global-grab')
        if display:
            args.append('--display')
            args.append(display)
        if timeout:
            args.append('--timeout')
            args.append(timeout)

        self._process = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

        self._out = self._process.stdout
        self._in = self._process.stdin
        resp = self._out.readline()  # check that pinentry is ready
        assert resp == 'OK Your orders please\n'

        self.tty_name = os.ttyname(sys.stdout.fileno())
        self.locale = '{}.{}'.format(*locale.getlocale())
        self.last_cmd = ''

    def call(self, line):
        if line.startswith('SET'):  # escape special characters for prompts
            cmd, arg = line.split(' ', 1)
            arg = ['%{:02x}'.format(ord(c)) for c in arg]
            line = ' '.join([cmd, ''.join(arg)])
        line = line + '\n'
        self._in.write(line)
        self._in.flush()
        self.last_cmd = line
        resp = []
        for line in self._out:
            resp.append(line)  # stop reading on response from pinentry
            if re.match(r'^(OK|ERR).*', line):
                break
        self.check_response(resp)
        return resp

    def check_response(self, resp):
        for line in resp:
            m = re.match(r'ERR\s+(\d+)\s+(.*)', line)
            if m:
                raise PinEntryError(m.group(1), m.group(2), self.last_cmd)
        return

    def get_pin(self):
        for line in self.call('GETPIN'):
            m = re.match(r'^D (.*)', line)
            if m:
                return re.sub(r'%25', '%', m.group(1))  #pinentry will escape % sign

    def get_confirm(self):
        try:
            self.call('CONFIRM')
        except PinEntryError as e:
            if e.message == 'canceled':
                return False
            else:
                raise
        return True

    def show_message(self):
        self.call('MESSAGE')

    def kill(self):
        self._process.terminate()

    def __del__(self):
        self.kill()


'''Some convienience methods:'''


def get_pin(description=None, prompt=None, timeout=0, display=None, global_grab=True):
    pinentry = PynEntry(timeout=timeout, display=display, global_grab=global_grab)
    pinentry.description = description
    pinentry.prompt = prompt
    return pinentry.get_pin()


def get_confirm(description=None, timeout=0, display=None, global_grab=True):
    pinentry = PynEntry(timeout=timeout, display=display, global_grab=global_grab)
    pinentry.description = description
    pinentry.show_message()


def show_message(description=None, timeout=0, display=None, global_grab=True):
    pinentry = PynEntry(timeout=timeout, display=display, global_grab=global_grab)
    pinentry.description = description
    pinentry.show_message()
