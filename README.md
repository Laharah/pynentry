# PynEntry
### A pythonic wrapper for pinentry

Written mostly to practice metaprogramming

credit to [mijikai](https://github.com/mijikai/pynentry) for a working example

***Requires pinentry to be installed***

#### convienience methods:

* to quickly and simply get a password/pin from a user:

`get_pin(description=None, prompt=None, timeout=0, display=None, global_grab=True)`

* to show and get a confirmation from a user:

`get_confirm(description=None, timeout=0, display=None, global_grab=True)`

* to show a message to a user:

`show_message(description=None, timeout=0, display=None, global_grab=True)`

#### PynEntry class
The above methods instance and configure a PynEntry instance wich can be called and configured manually
via attributes


the PynEntry class supports the following attributes:

* `description`: Sets the descriptive text to display
* `prompt`: Sets the text just before the passphrase entry (ex: "PASS:")
* `title`: Sets the window title
* `ok_text`: Sets the text shown in the "OK" button
* `cancel_text`: Sets the text shown in the "Cancel" button
* `error_text`: Sets the text in case of error before reprompt (Cleared after every `get_pin()` call)
* `tty_name`: Chose the tty to use (set automatically)
* `tty_type`: Change the tty type to use.
* `locale`: Sets the locale to use (set automatically to current os locale)

***NOTE: The PynEntry class uses the $PATH variable to find the pinentry executable, you can specify the location of the
executable manually when you initialize like so: `PynEntry(executable='/path/to/pinentry')`***

PynEntry is best used as a context manager to automatically kill the pinentry process when you are done.

#### Example:
```python
import pynentry
pynentry.show_message('Hello there!')

with pynentry.PynEntry() as p:
    p.description = 'Enter a password.\n Choose Wisely!'
    p.prompt = 'PASS>'
    try:
        passwd = p.get_pin()
    except pynentry.PinEntryCancelled:
        print('Cancelled?! Goodbye.')
        exit()
    p.ok_text = 'yep!'
    p.cancel_text = 'nope!'
    p.description = f'CAN YOU CONFIRM YOUR SUPER SECRET PASSWORD IS {passwd}?'
    if p.get_confirm():
            print(f'password {passwd} saved!')
    else:
            print(f'Too bad, so sad')
```
