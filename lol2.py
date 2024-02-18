import re

file = open("pixelEngine.py", "r", encoding="UTF-8")
data = file.read()
file.close()

hc = re.findall(r'"#.{6}"', data)

hc = set(hc)

print(hc)
print(len(hc))