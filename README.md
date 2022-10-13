# RFCView
RFC Viewer - Visualizes RFC updates and obsoletes, performs searches on RFCs. 
Is based on the RFC Index (https://www.rfc-editor.org/in-notes/rfc-index.xml)
> Current file included in the repo: 2022-06-15


Requirements: `pip3 install networkx pyvis xmltodict`



```
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
```

Output:

1) Interactive Network Graph in graphs/<search keyword>.html

![Example graph for IPv6 as keyword](/img/rfcvis.png)

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
## Graphs
  
  All graphs are compiled with -c 0, thus only RFCs are included that have the search term in the Title/Keyword section of the index.
  The chain parameter c should be increased carefully, values of 1 and 2 should be enough, otherwise the graph soon becomes very large.
  
  The graph will load dynamically each time the html file is opened in the browser. Static loading (compile it once and then save node and edge positions) is possible, however to the best of my knowledge there exists no automatic functionality for this yet (Happy to collaborate on automating this).
  
  The manual process to make pyvis static, includes the following steps.

  1) Render Graph in Browser -> F12 Console
  Copy output to clipboard
  ```
  network.storePositions();
  console.log(JSON.stringify(data.nodes.get()))
  ```
  2) Edit html file (Optional: cp html to file_static.html)

  - Comment out loadbar div (not needed anymore)
  - Comment out loadbar js/css (optional)
  - Set physics options to false
    ```
      "physics": {
        "enabled": false,
        "repulsion": {
    ```
  - goto nodes = and copy output from 1) to the vis.DataSet array

Save and done!

  
