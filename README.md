# tEDI - an EDI parser

A Python library for parsing X12 EDI documents. Output is XML (sorry, not sorry).

Currently supports 810 (invoice), 850 (purchase order), 855 (acknowledgement), 856 (ship notification), and <i>small</i> 832 (catalog).

## Usage

### Python

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

### Command Line

```bash
cat example/edi/850.txt |PYTHONPATH=. python3 tedi.py
```

```xml
<?xml version="1.0" ?>
<ISA ISA01="00" ISA02="          " ISA03="00" ISA04="          " ISA05="ZZ" ISA06="BUYER          " ISA07="ZZ" ISA08="SUPPLIER       " ISA09="250113" ISA10="0801" ISA11="U" ISA12="00001" ISA13="000000001" ISA14="0" ISA15="P" ISA16="|">
        <GS GS01="PO" GS02="BUYER" GS03="SUPPLIER" GS04="20250113" GS05="080100" GS06="01" GS07="X" GS08="000001">
                <ST ST01="850" ST02="0001">
                        <BEG BEG01="00" BEG02="SA" BEG03="25011308010000" BEG04="" BEG05="20250113" BEG06="" BEG07="" BEG08="" BEG09="" BEG10="" BEG11="" BEG12=""/>
                        <N1 N101="BT" N102="BILLTO" N103="11" N104="RAND00568" N105="" N106=""/>
                        <N1 N101="ST" N102="SHIPTO" N103="11" N104="RAND4444" N105="" N106=""/>
                        <PO1 PO101="1" PO102="5" PO103="EA" PO104="3.14" PO105="" PO106="N4" PO107="60505132101" PO108="VN" PO109="VENDORNUMBER01" PO110="" PO111="" PO112="" PO113="" PO114="" PO115="" PO116="" PO117="" PO118="" PO119="" PO120="" PO121="" PO122="" PO123="" PO124="" PO125="">
                                <PID PID01="F" PID02="" PID03="" PID04="" PID05="Product Description" PID06="" PID07="" PID08="" PID09=""/>
                        </PO1>
                        <CTT CTT01="1" CTT02="" CTT03="" CTT04="" CTT05="" CTT06="" CTT07=""/>
                        <SE SE01="7" SE02="0001"/>
                </ST>
        </GS>
        <GE GE01="1" GE02="01"/>
        <IEA IEA01="1" IEA02="000000001"/>
</ISA>
```
