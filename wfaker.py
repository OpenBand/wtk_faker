#!/usr/bin/env python3

_logo = """
  █████▒▄▄▄       ██ ▄█▀▓█████  ██▀███  
▓██   ▒▒████▄     ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒
▒████ ░▒██  ▀█▄  ▓███▄░ ▒███   ▓██ ░▄█ ▒
░▓█▒  ░░██▄▄▄▄██ ▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  
░▒█░    ▓█   ▓██▒▒██▒ █▄░▒████▒░██▓ ▒██▒
 ▒ ░    ▒▒   ▓▒█░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░
 ░       ▒   ▒▒ ░░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░
 ░ ░     ░   ▒   ░ ░░ ░    ░     ░░   ░ 
             ░  ░░  ░      ░  ░   ░     
                                        
        """
# Thx. https://patorjk.com/software/taag/#p=display&f=Bloody&t=Faker

_description = """

It is comprehensive wrapper for faker module.
To obtain human like strings for login, e-mails. etc. or just to create memorizing text.
It could store created string into database file for quick search for uniqueness if it is required.
Result string consists of widely portable charset: -.a-z0-9
"""

from bloom_filter2 import BloomFilter
from optparse import OptionParser
from wlib import *

import faker
import os
import re
import sys
import unidecode


class HumanLikeOptions():

    MAXUSE_LOCALS = 5
    MINLEN = 3
    MAXLEN = 16

    DNOISE_MAXLEN = 1
    DNOISE_COND = 1
    CREATE_ATTEMPTS = 3
    DATABASE_MAXLEN = 10**8


class HumanLike():
    
    def __init__(self, create):
        self._db = None
        if create:
            ls = []
            for _ in range(0, HumanLikeOptions.MAXUSE_LOCALS):
                ls.append(WRand.choice(faker.config.AVAILABLE_LOCALES))
            WGui.debug(f"AVAILABLE_LOCALES = {ls}")
            self.generators = {}
            for l in ls:
                fake = faker.Factory.create(l)
                self.generators[l] = [fake.last_name, 
                                      fake.first_name, 
                                      fake.company]
        else:
            self.generators = None
    
    @staticmethod
    def check(hstr:str):
        if len(hstr) < HumanLikeOptions.MINLEN or len(hstr) > HumanLikeOptions.MAXLEN * 2:
            return False
        if hstr is hstr.lower():
            return False
        if re.match(r'^[a-z]{3,}[-.a-z0-9]+', hstr) is None:
            return False
        if re.match(r'[-.a-z0-9]+[^-.]{1}$', hstr) is None:
            return False
        return True
    
    @staticmethod
    def create_with_db(database_file, create):
        obj = HumanLike(create)
        obj._db = BloomFilter(max_elements=HumanLikeOptions.DATABASE_MAXLEN, 
                              error_rate=0.01, filename=(database_file, -1))
        return obj

    def suggest_string(self):
        if not self.generators:
            raise ValueError("Generator has not been initialized")

        result = ""
        half_len = HumanLikeOptions.MAXLEN // 2 + HumanLikeOptions.MINLEN
        new_len = WRand.get_int(half_len, half_len * 2)
        rest_chunk = WRand.get_int(HumanLikeOptions.MINLEN, half_len)
        generators = self.generators[WRand.choice(list(self.generators.keys()))]
        while len(result) < new_len:
            generator = WRand.choice(generators)
            next_pattern = unidecode.unidecode(generator()).lower()
            next_pattern = re.sub(r'[^-.a-z]+', WRand.choice(['.', '-', '']), next_pattern) 
            if WRand.get_bool():
                next_pattern = next_pattern[0:int(80 * len(next_pattern)/100)]
            if (len(next_pattern) < new_len - len(result)):
                result = result + next_pattern
            else:
                result = result + next_pattern[0: new_len - len(result)]
                if new_len - 4 > 3 and WRand.get_bool():
                    n = WRand.get_int(3, new_len - 4)
                    result = list(result)
                    result[n] = WRand.choice(['.', '-'])
                    result = "".join(result)
            if new_len - len(result) < rest_chunk:
                break
        result = re.sub(r'([.]|[-]){2,}', r'\1', result)
        for i in range(2):
            result = re.sub(r'^([a-z]{,3})(\.|\-)', r'\1', result)
        if len(result) < new_len and new_len % len(result) > HumanLikeOptions.DNOISE_COND:
            dnoise = "0123456789"
            dnoise = list(dnoise)
            c = len(dnoise) - 1
            while c > 0:
                c2 = WRand.get_int(0, c)
                dnoise[c2], dnoise[c] = dnoise[c], dnoise[c2]
                c -= 1
            dnoise = "".join(dnoise)
            rest = WRand.get_int(1, HumanLikeOptions.DNOISE_MAXLEN + 1)
            result = result + dnoise[0: min(new_len - len(result), rest)]
        if result[-1] == '.' or result[-1] == '-':
            result = result[:-1]
        return result
    
    def create_string(self, limit):
        result = ""
        lp = 0
        while True:
            result = self.suggest_string()
            if self.check(result):
                if not self._db or result not in self._db:
                    break
            lp = lp + 1
            if lp > limit:
                raise ValueError("Can't create unique string")
            WGui.warning(f"Attempt #{lp}: '{result}' - failed. {limit - lp} Left")
        if self._db:
            self._db.add(result)
        return result

    def check_uniqueness(self, test):
        if not test or not isinstance(test, str) or not any(test):
            raise  ValueError("Can't test for empty or invalid string")

        if not self._db:
            raise ValueError("Database is required")
        
        return test not in self._db


def main(options):
    try:
        if options.database:
            humanlike = HumanLike.create_with_db(options.database,  options.create)
        else:
            humanlike = HumanLike(options.create)
    
        if options.test:
            if not humanlike.check_uniqueness(options.test):
                WGui.warning(f"'{options.test}' is not unique")
                return 1
            WGui.ok(f"'{options.test}' is unique")
        elif options.create:
            fstr = humanlike.create_string(HumanLikeOptions.CREATE_ATTEMPTS)
            WGui.print(fstr)
        else:
            WGui.print(humanlike.suggest_string())
        
        return 0
    except BaseException as err:
        WGui.error(f"Can't obtain humanlike strings: {err}")
        return 2

if __name__ == '__main__':
    parser = OptionParser(description=_description)
    parser.add_option("-c", "--create", dest="create", default=False, action="store_true",
                      help="Create humanlike string and register created string into database file (if -t option was not set). "
                      "It is trying to create uniq string.")
    parser.add_option("-d", "--database", dest="database",
                      help="Database binary file to control uniqueness", metavar="FILE")
    parser.add_option("-t", "--test", dest="test",
                      help="Check the input string for uniqueness (database is required)", metavar="FILE")
    (options, args) = parser.parse_args()
    
    if len(sys.argv) < 2:
        WGui.Hi(_logo)
        parser.print_help()
    else:
        sys.exit(main(options))