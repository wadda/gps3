#!/usr/bin/env python
""" banana """ # <-- For scale
import json
import urllib
import dicttoxml

page = urllib.urlopen('http://quandyfactory.com/api/example')
content = page.read()
obj = json.loads(content)
print(obj)
{u'mylist': [u'foo', u'bar', u'baz'], u'mydict': {u'foo': u'bar', u'baz': 1}, u'ok': True}
xml = dicttoxml.dicttoxml(obj)
print(xml)
<?xml version="1.0" encoding="UTF-8" ?><root><mylist><item type="str">foo</item><item type="str">bar</item><item type="str">baz</item></mylist><mydict><foo type="str">bar</foo><baz type="int">1</baz></mydict><ok type="bool">true</ok></root>



if __name__ == '__main__':    # code to execute if called from command-line
    pass    # do nothing, unless code is added to this template
            # this is either a simple example of how to use the module,
            # or when the module can meaningfully be called as a script.
