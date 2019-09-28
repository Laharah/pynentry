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
