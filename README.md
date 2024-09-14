# AlphaESS ModbusTCP (14405)

## Beschreibung 

Der Baustein liest von einem AlphaESS Wechselrichter / Batteriespeicher via ModbusTCP einige bestimmte Register aus.

### Vorbereitung


## Eingänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | --- | --- | --- |
| 1 | Nibe UDP GW IP | | IP des UDP-Gateways |

## Ausgänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | --- | --- | --- |
| 1 | Werte (json) | | Json Objekt der Form *{'48043': {'value': 0.0, 'Title': 'Holiday - Activated'}, ...*. Die weite Auswertung kann dann z.B. mit dem Baustein 11087 erfolgen. |


## Beispielwerte

| Eingang | Ausgang |
| --- | --- |
| - | - |


## Sonstiges

- Neuberechnug beim Start: Nein
- Baustein ist remanent: nein
- Interne Bezeichnung: 14405
- Kategorie: Datenaustausch

### Change Log

Siehe [github Changelog](https://github.com/En3rGy/14405_AlphaESS_ModbusTCP/releases) zum jew. Release. 

### Open Issues / Know Bugs

Bekannte Fehler werden auf [github](https://github.com/En3rGy/14107_NibeWP) verfolgt.

### Support

Please use [github issue feature](https://github.com/En3rGy/14405_AlphaESS_ModbusTCP/issues) to report bugs or rise feature requests.
Questions can be addressed as new threads at the [knx-user-forum.de](https://knx-user-forum.de) also. There might be discussions and solutions already.


### Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14405_AlphaESS_ModbusTCP).

### Devleopment Environment

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python markdown module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)


## Anforderungen

-

## Software Design Description

-

## Validierung & Verifikation

- Teilweise Abdeckung durch Unit Tests 

## Licence

Copyright 2024 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.