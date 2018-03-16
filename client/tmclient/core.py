import asyncio

import urwid

def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')

def sub_menu(caption, choices):
    contents = menu(caption, choices)
    def open_menu(button):
        return TOP.open_box(contents)
    return menu_button([caption, u'...'], open_menu)

def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button):
    response = urwid.Text([u'You chose ', button.label, u'\n'])
    done = menu_button(u'Ok', exit_program)
    TOP.open_box(urwid.Filler(urwid.Pile([response, done])))

def exit_program(button):
    raise urwid.ExitMainLoop()


class Form(urwid.Pile):
    def __init__(self, fields, submit, on_submit):
        super().__init__(fields+[submit])
        self.fields = fields
        self.submit_btn = submit
        self.on_submit = on_submit

        urwid.connect_signal(self.submit_btn, 'click', self.submit)


    def submit(self, _):
        data = {}
        for w in self.fields:
            data[w.name] = w.get_edit_text()

        self.on_submit(data)


class FormField(urwid.Edit):
    def __init__(self, *args, **kwargs):
        name = kwargs.get('name')
        del kwargs['name']
        super().__init__(*args, **kwargs)
        self.name = name

def show_login(_):

    un_field = FormField(caption='username: ', name='username')
    pw_field = FormField(caption='password: ', name='password', mask='~')
    submit_btn = urwid.Button('login! >')
    login_form = Form(fields=[un_field, pw_field],
                      submit=submit_btn,
                      on_submit=handle_login)

    TOP.open_box(urwid.Filler(login_form))

def handle_login(login_data):
    print('HANDLING LOGIN WITH {}'.format(login_data))

def handle_exit(_):
    raise urwid.ExitMainLoop()


# TODO dynamically create the main menu based on authentication state
menu_top = menu('tildemush main menu', [
    menu_button('login', show_login),
    sub_menu('create a new user account', [
        menu_button('TODO', item_chosen),
    ]),
    sub_menu('settings', [
        menu_button('set server domain', item_chosen),
        menu_button('set server port', item_chosen),
        menu_button('set server password', item_chosen)
    ]),
    menu_button('exit', handle_exit)
])


class SplashScreen(urwid.BigText):
    def __init__(self):
        super(SplashScreen, self).__init__('welcome to\ntildemush',
                                           urwid.font.HalfBlockHeavy6x5Font())

class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box, initial):
        super(CascadingBoxes, self).__init__(initial)
        self.box_level = 0
        self.box = box
        self.initial = initial

    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def keypress(self, size, key):
        if self.original_widget is self.initial:
            self.original_widget = urwid.SolidFill('~')
            self.open_box(self.box)
        elif key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(CascadingBoxes, self).keypress(size, key)


bt = urwid.BigText('WELCOME TO TILDEMUSH', urwid.font.HalfBlock7x7Font())
bt = urwid.Padding(bt, 'center', None)
bt = urwid.Filler(bt, 'middle', None, 7)
ftr = urwid.Text('~ press any key to jack in ~', align='center')
f = urwid.Frame(body=bt, footer=ftr)
SPLASH = f

TOP = CascadingBoxes(menu_top, SPLASH)
def start():
    #import ipdb; ipdb.set_trace()

    evl = urwid.AsyncioEventLoop(loop=asyncio.get_event_loop())
    urwid.MainLoop(TOP, event_loop=evl, palette=[('reversed', 'standout', '')]).run()
