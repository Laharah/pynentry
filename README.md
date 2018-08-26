# PynEntry
### A python wrapper for pinentry

Written mostly to practice metaprogramming

credit to [mijikai](https://github.com/mijikai/pynentry) for a working example


convienience methods:

* to quickly and simply get a password/pin from a user
    get_pin(description=None, prompt=None, timeout=0, display=None, global_grab=True)

* to show and get a confirmation from a user
    get_confirm(description=None, timeout=0, display=None, global_grab=True)

* to show a message to a user
    show_message(description=None, timeout=0, display=None, global_grab=True)


The above methods instance and configure a PynEntry instance wich can be called and configured manually
via attributes


the PynEntry class supports the following attributes:

* 'description': Sets the descriptive text to display
* 'prompt': Sets the text just before the passphrase entry (ex: "PASS:")
* 'title': Sets the window title
* 'ok_text': Sets the text shown in the "OK" button
* 'cancel_text': Sets the text shown in the "Cancel" button
* 'error_text': Sets the text in case of error before reprompt
* 'tty_name': Chose the tty to use (set automatically)
* 'tty_type': Change the tty type to use.
* 'locale': Sets the locale to use (set automatically to current os locale)


Example:
```python
import pynentry
pynentry.show_message('Hello there!')

p = pynentry.PynEntry()
p.description = 'Enter a password.\n Choose Wisely!'
p.prompt = 'PASS>'
passwd = p.get_pin()
p.ok_text = 'yep!'
p.cancel_text = 'nope!'
p.description = f'CAN YOU CONFIRM YOUR SUPER SECRET PASSWORD IS {passwd}?'
if p.get_confirm():
	print(f'password {passwd} saved!')
else:
	print(f'Too bad, so sad')
````
