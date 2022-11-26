#hi

import re

strings = "howdyhowdy\nhowdy"
string2 = re.sub('(.)',r'\1  ',strings)
print(string2)