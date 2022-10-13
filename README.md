# RFCView
RFC Viewer - Visualizes RFC updates and obsoletes, performs searches on RFCs

Requirements: pip3 install networkx pyvis xmltodict

Is based on the RFC Index (https://www.rfc-editor.org/in-notes/rfc-index.xml)
Current file included in the repo: 2022-06-15

usage: rfc.py [-h] -f FILE [-s SEARCH] [-i INDEXFIELDS] [-c CHAIN]
              [-o OUTPUTFILE] [-v OUTPUTVALUES] [-l]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to the rfc-index
  -s SEARCH, --search SEARCH
                        Search keyword
  -i INDEXFIELDS, --indexfields INDEXFIELDS
                        Tags to perform search on "title,keywords,abstract"
                        (default: "title,keywords")
  -c CHAIN, --chain CHAIN
                        follow obsoletes/obsoleted-by/updates/updated-by c
                        steps (default: 0)
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        Path to output file (Output will be in csv format)
  -v OUTPUTVALUES, --outputvalues OUTPUTVALUES
                        Output values/fields (display with --list-outputvalues)
  -l, --list-outputvalues
                        Lists output values/fields for outputfile


Output:

1) Interactive Network Graph in graphs/<search keyword>.html

![Example graph for IPv6 as keyword](img/rfcvis.jpg?raw=true "Example for IPv6 Search")

2) CSV with matching RFCs, e.g.
```
RFC0001,April 1969,UNKNOWN,UNKNOWN,Host Software,11
RFC0002,April 1969,UNKNOWN,UNKNOWN,Host software,10
RFC0003,April 1969,UNKNOWN,UNKNOWN,Documentation conventions,2
RFC0004,March 1969,UNKNOWN,UNKNOWN,Network timetable,6
RFC0005,June 1969,UNKNOWN,UNKNOWN,Decode Encode Language (DEL),17
```

3) Basic Stats in stdout
```
# Search complete - found 
rfcs:9043
rfc-chains:760
connected-rfcs:3543
standalone-rfcs:5500
pages:224042
obsoletes:7800
updates:6787
status-changes:318
authors:5910
first-published:1968-02-01
latest-published:2022-06-01
```

