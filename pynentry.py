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
        self.last_cmd = last_cmd.strip()

    def __str__(self):
        m = 'call "{s.last_cmd}" failed with error "{s.code} {s.message}"'.format(s=self)
        return m


class PinEntryCancelled(PinEntryError):
    def __str__(self):
        return 'call "{}" was cancelled by user'.format(self.last_cmd)


class PinOption:
    '''descriptor that calls the correct command to adjust pinentry behavior
    when the class attribute is set'''

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            msg = 'PynEntry must be instanced before accessing {}'.format(self.name)
            raise TypeError(msg)
        return instance.__dict__.get(self.name)  # manip dict directly to stop recursion

    def __set__(self, instance, value):
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
    Wrapper for pythonic interaction with pinentry, best used as a context manager
    credit to mijikai
    '''
    # _attribs: a list of attributes and their commands, used by the descriptors
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

    def __init__(self,
                 *,
                 executable='pinentry',
                 timeout=0,
                 display=None,
                 global_grab=True):

        args = [executable]
        if not global_grab:
            args.append('--no-global-grab')
        if display:
            args.append('--display')
            args.append(display)
        if timeout:
            args.append('--timeout')
            args.append(timeout)

        self._process = subprocess.Popen(args,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         universal_newlines=True)

        self._out = self._process.stdout
        self._in = self._process.stdin
        resp = self._out.readline()  # check that pinentry is ready
        valid = ["OK Your orders please\n", "OK Pleased to meet you\n"]
        assert resp in valid

        self.tty_name = None
        try:
            if sys.stdout.isatty():
                self.tty_name = os.ttyname(sys.stdout.fileno())
        except AttributeError:  # We are on windows
            pass
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
        self._check_response(resp)
        return resp

    def _check_response(self, resp):
        for line in resp:
            m = re.match(r'ERR\s+(\d+)\s+(.*)', line)
            if m:
                raise PinEntryError(m.group(1), m.group(2), self.last_cmd)
        return

    def get_pin(self):
        'Get a pin from the user, raises PinEntryCancelled on cancel'
        try:
            for line in self.call('GETPIN'):
                m = re.match(r'^D (.*)', line)
                if m:
                    return m.group(1)
        except PinEntryError as e:
            if 'cancel' in e.message.lower():
                raise PinEntryCancelled(e.code, e.message, e.last_cmd) from e
        finally:
            self.error_test = None

    def get_confirm(self, one_button=False):
        'Get confirmation from a user, returns True/False'
        cmd = 'CONFIRM'
        if one_button:
            cmd += ' --one-button'
        try:
            self.call(cmd)
        except PinEntryError as e:
            if re.search(r'(cancell?ed|not confirmed)', e.message, re.I):
                return False
            else:
                raise
        return True

    def show_message(self):
        self.call('MESSAGE')

    def kill(self):
        try:
            self._process.terminate()
        except AttributeError:
            pass

    def close(self):
        'synonym for kill'
        self.kill()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.kill()

    def __del__(self):
        self.kill()


# Some convienience methods:


def get_pin(description=None, prompt=None, timeout=0, display=None, global_grab=True):
    with PynEntry(timeout=timeout, display=display, global_grab=global_grab) as pinentry:
        pinentry.description = description
        pinentry.prompt = prompt
        return pinentry.get_pin()


def get_confirm(description=None, timeout=0, display=None, global_grab=True):
    with PynEntry(timeout=timeout, display=display, global_grab=global_grab) as pinentry:
        pinentry.description = description
        pinentry.show_message()


def show_message(description=None, timeout=0, display=None, global_grab=True):
    with PynEntry(timeout=timeout, display=display, global_grab=global_grab) as pinentry:
        pinentry.description = description
        pinentry.show_message()
