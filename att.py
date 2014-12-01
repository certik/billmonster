#!/usr/bin/env python

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium import webdriver

from billmonster import _element_available

from clint.arguments import Args
args = Args()
from clint.textui import colored, puts

import keyring, sys


def att(user=None, quit_when_finished=True, browser=None):

    if not user:
        # Get the username from the command line arguments.
        user = args.get(0)

    # Must supply username.
    if user is None:
        puts(colored.red('You must supply a username like "python att.py nick"'))
        sys.exit()

    # Get the user's password from the password backend.
    key = keyring.get_password('att.com', user)

    # If the key doesn't exist in the password backend.
    if key is None:
        puts(colored.red("You must store the password for {} in your keyring's backend.".format(user)))
        puts('See: http://pypi.python.org/pypi/keyring/#configure-your-keyring-lib')
        sys.exit()

    # Log what we're currently working on.
    puts(colored.blue('\nAT&T ({})'.format(user)))

    if not browser:
        # Init the WebDriver.
        b = webdriver.Firefox()
    else:
        b = browser

    b.get('https://www.att.com/')

    # Find the username field on the page.
    username = b.find_element_by_css_selector('input#userid')
    username.send_keys(user)

    # Find the password field on the page.
    password = b.find_element_by_css_selector('input#password')
    password.send_keys(key)
    password.submit()

    # Wait for an account page.
    try:
        WebDriverWait(b, timeout=15).until(_element_available(b, 'div.mybilldiv span.colorOrange.font30imp'))
    except TimeoutException:
        puts(colored.red("Looks like the system is down."))

        if quit_when_finished:
            b.quit()
        else:
            return b

    amount = b.find_element_by_css_selector('div.mybilldiv span.colorOrange.font30imp')

    print 'AT&T ({}): {}'.format(user, amount.text)

    if quit_when_finished:
        b.quit()

    return b


if __name__ == '__main__':
    att()
