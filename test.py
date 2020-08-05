import pynentry
pynentry.show_message('Hello there!')

with pynentry.PynEntry() as p:
    p.description = 'Enter a password.\n Choose Wisely! テ  デ  ト  ド'
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
