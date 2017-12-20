import random
import os
import sys

def append_secret_key_if_not_in_file():
    if 'secrets.py' not in os.listdir(os.dirpath(__file__)):
        with open('secrets.py', 'w') as fh:
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            key = ''.join(random.SystemRandom().choices(chars, k=50))
            fh.write("""SECRET_KEY = '{}'""".format(key))
            fh.close()
    else:
        with open('secrets.py', 'r') as fh:
            if 'SECRET_KEY' in fh.read():
                sys.exit('SECRET_KEY exists, exiting')
        with open('secrets.py', 'a') as fh:
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            key = ''.join(random.SystemRandom().choices(chars, k=50))
            fh.write("""SECRET_KEY = '{}'""".format(key))
            fh.close()

if __name__ == '__main__':
    append_secret_key_if_not_in_file()
