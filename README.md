# tEDI - an EDI parser

## Usage

```python
import sys
import xml
import tedi

edi = sys.stdin.read()
segment_separator = edi[105]
element_separator = edi[3]
parser = tedi.Parser(segment_separator, element_separator)
parsed = parser.parse(edi)
print(xml.etree.ElementTree.tostring(parsed).decode('utf-8'))
```
