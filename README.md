# menser
Speiseplan für die Mensen des Studentenwerk Erlangen-Nürnberg

### Woher kommts
- von der infomax api: https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml
- oder auch: https://www.sigfood.de/?do=api.gettagesplan (nur für die Südmensa)
- oder https://openmensa.org/api/v2/canteens/

Teile des Parsers von https://github.com/mswart/openmensa-parsers

### Usage
    python ./menser.py <lmp/sued>

### Requirements
- `rich` for text formatting