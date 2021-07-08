import hat.gui.vt
import io
import json


with open("net.svg", "r") as file:
    xml = file.read()

stripped = "".join(line.lstrip() for line in xml.split("\n"))
stream = io.StringIO(stripped)
parsed = hat.gui.vt.parse(stream)
print(parsed)
