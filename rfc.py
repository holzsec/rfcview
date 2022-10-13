#!/usr/bin/env python3

# RFC Explorer 
# based on the RFC Index (https://www.rfc-editor.org/in-notes/rfc-index.xml)

#Generate & Visualize Graphs
import networkx as nx
from pyvis.network import Network

#General Imports (reading RFC index, parsing args, performing keyword searches,...)
import xmltodict
import argparse
import re
import datetime

# List of  common words used to shorten RFC titles (for an upgraded list look at: nltk.download('stopwords'))
common_words=['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", \
"you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', \
 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', \
 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', \
 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', \
 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', \
 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', \
 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', \
 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', \
 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", \
 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", \
 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

#Output values and their translation to the rfc index
default_values=["rfc","date","publication-status","current-status","title","pages"]
xml_dict={"rfc":"doc-id", \
		  "date":"date", \
		  "publication-status":"publication-status", \
		  "current-status":"current-status", \
		  "title":"title", \
		  "pages":"page-count", \
		 }

#Values that will be enumerated
enum_dict={
		"rfcs":0,\
		"rfc_chains":0,\
		"connected_rfcs":0,\
		"standalone_rfcs":0,\
		"pages":0,\
		"obsoletes":0,\
		"updates":0,\
		"status_changes":0,\
		"authors":0,\
		"first_published":"",\
		"latest_published":"",\
}

def search_string(field,key):
	"""
		Perform case insensitive substring search in given string
	"""
	if re.search(key, field, re.IGNORECASE):
		return True 
	else:
		return False

def search_list(list,key):
	"""
		Look if key is substring of an string element in the list
	"""
	for el in list:
		if isinstance(el,str):
			if search_string(el,key) == True:
				return True
	return False

def search_field(field,key):
	"""
		Iterative function checks subelements of fields for searchable elements (not all the xml elements in the index are formatted correctly)
	"""
	if field != None:
		if isinstance(field,str):
			res=search_string(field,key)
		elif isinstance(field,list):
			res=search_list(field,key)
		elif isinstance(field,dict):
			for el in field:
				res=search_field(field[el],key)
		if res==True:
			return True				
	return False

def add_result(entries,rfc,matching_results,match_dict):
	"""
		Add entry to results if not already in results
	"""
	if rfc not in match_dict:
		for entry in entries["rfc-entry"]:
			if entry["doc-id"]==rfc:
				break
		matching_results.append(entry)
		match_dict[entry["doc-id"]]=entry["doc-id"]
	return matching_results,match_dict

def entry_links(entries,rfc,matching_results,match_dict,path,steps,maxsteps):
	"""
		Recursive function that checks rfc index entries for obsoletes/updates and adds it to results
	"""
	rfc_links=["obsoletes","obsoleted-by","updates","updated-by"]
	if steps <= maxsteps:
		for entry in entries["rfc-entry"]:
			if entry["doc-id"]==rfc:
				break
		for link_type in rfc_links:
				if link_type in entry:
					ids=entry[link_type]["doc-id"]
					#print(ids)
					if isinstance(ids,str):
						#Add single entry
						if ids not in path:
							matching_results,match_dict=add_result(entries,ids,matching_results,match_dict)
							path[ids]=1
							matching_results,match_dict=entry_links(entries,ids,matching_results,match_dict,path,steps+1,maxsteps)
					else:
						#Add entries in a loop
						for id in ids:
							if id not in path:
								matching_results,match_dict=add_result(entries,id,matching_results,match_dict)
								path[id]=1
								matching_results,match_dict=entry_links(entries,id,matching_results,match_dict,path,steps+1,maxsteps)
	return matching_results,match_dict

def search(entries,key="None",fields=["title" , "keywords"],chain=0):
	"""
		Performs a title/keyword search on the xml index and returns matching entries (where at least one of the selected fields matches)
	"""
	print("Starting search with selected fields: [ "+",".join(fields)+" ]")
	if chain > 0:
		print("Following 'Obsoletes','Obsoleted-by','Updates','Updated-by' "+str(chain)+" steps, even when keyword is not present in those RFCs")
	else:
		print("'Default: Obsoletes','Obsoleted-by','Updates','Updated-by' RFCs are only present when they include the keyword (change -c <nr> if wanted)")
	match_dict={}

	#Return all RFCs as result
	if key=="all":
		match_dict={x["doc-id"]:x["doc-id"] for x in entries["rfc-entry"]}
		return [x for x in entries["rfc-entry"]],match_dict
	#Perform search
	else:
		matching_results=[]
		for entry in entries["rfc-entry"]:
			#Check entry
			res=False
			for field in fields:
				if field in entry:
					res=search_field(entry[field],key)
				
				#Add entry
				if res==True:
					add_result(entries,entry["doc-id"],matching_results,match_dict)
					#Check linked RFCs when enabled
					if chain > 0:
						matching_results,match_dict=entry_links(entries,entry["doc-id"],matching_results,match_dict,{entry["doc-id"]:1},1,chain)
					break
		return matching_results,match_dict


def wrap_by_word(s, n):
	"""
		Returns a string where \\n is inserted between every n words
	"""
	a = s.split()
	ret = ''
	for i in range(0, len(a), n):
		ret += ' '.join(a[i:i+n]) + '\n'

	return ret

def build_resultdict(result):
	"""
		For each RFC in results compute a shorter title and choose color based on status (standard track vs others)
	"""
	result_dict={}
	for entry in result:
		rfc=entry["doc-id"]
		result_dict[rfc]={}
		status=entry["current-status"]
		if "standard" in status.lower():
			color="#018786"
		else:
			color="orange"
		title="".join([ch for ch in entry["title"] if ch.isalpha() or ch.isspace() or ch.isnumeric()])
		title_tokens = title.split(" ")#word_tokenize(title)  
		filtered_title = str(rfc)+ "\n"+str(entry["date"]["year"])+"\n"+wrap_by_word(" ".join([w for w in title_tokens if not w.lower() in common_words]),3)
		result_dict[rfc]["title"] = filtered_title
		result_dict[rfc]["color"] = color
	return result_dict

def add_node(net,rfc,result_dict,color=None,overwrite=False):
	"""
		add node to graph (default: do not override if it already exists)
	"""
	new=False
	if overwrite == False:
		if rfc not in net:
			new=True
	else:
		new=True
	if new ==True:
		datatracker_ref="<a target=\'_blank\' href=\'https://datatracker.ietf.org/doc/html/"+rfc.lower()+"\'>"+rfc
		net.add_node(rfc,label=result_dict[rfc]["title"],title=datatracker_ref,color=color)
	return net

def handle_edge(net,result_dict,field,src,target,color_index):
	"""
		Take obsoleted-by, obsoletes, updated-by and udates; create nodes & edges
	"""
	link_dict={"obsoleted-by":"obsoletes","updated-by":"updates"}
	color=["red","red","#018786","#018786"]
	#Only check edges between results
	if target in result_dict:

		# Add target node with original color  
		net=add_node(net,target,result_dict,color=result_dict[target]["color"],overwrite=False)

		if field=="obsoletes":
			#Add/change target color to red (obsoleted)
			net=add_node(net,target,result_dict,color="red",overwrite=True)
		elif field=="obsoleted-by":
			#Change source node color to red (obsoleted)
			net=add_node(net,src,result_dict,color="red",overwrite=True)
			
		#Directed edges based on 
		if field=="obsoletes" or field == "updates":
			net.add_edge(src,target,title=field,color=color[color_index])
		else:
			#Reverse updated-by/obsoleted-by arrows and call them obsoletes/updates for comprehensiveness
			net.add_edge(target,src,title=link_dict[field],color=color[color_index])
	return net

def nx_graph(result,result_dict,search_string):
	"""
		Generate a directed networkx graph and parse it with pyvis for visualization
	"""
	
	#Directed graph for visualization
	net = nx.DiGraph()

	#Undirected graph for connection evaluations
	unet= nx.Graph()

	#Pyvis visualization graph (currently: dark mode)
	g=Network(height="100vh", width="100vw",directed =True,bgcolor="#222222",font_color="lightgrey")
	
	#Define graph window size and distance between nodes and "edge" length
	g.repulsion(node_distance=200, spring_length=100)

	#Add datatracker links for RFCs in title of graph	
	rfc_datatracker="<a href=\'https://datatracker.ietf.org/doc/html/"
	rfc_links=["obsoletes","obsoleted-by","updates","updated-by"]

	#Add result nodes (RFCs)
	for entry in result:
		rfc=entry["doc-id"]
		net=add_node(net,rfc,result_dict,color=result_dict[rfc]["color"],overwrite=False)
		unet=add_node(unet,rfc,result_dict,color=result_dict[rfc]["color"],overwrite=False)
		c=0
		for field in rfc_links:
			if field in entry:
				if entry[field] != None:
					ids=entry[field]["doc-id"]
					if isinstance(ids,str):
						#Add single edge to directed graph
						net=handle_edge(net,result_dict,field,rfc,ids,c)
						#Add single edge to undirected graph
						unet=handle_edge(unet,result_dict,field,rfc,ids,c)
					else:
						#Add edges in a loop
						for id in ids:
							#Add single edge to directed graph
							net=handle_edge(net,result_dict,field,rfc,id,c)
							#Add single edge to undirected graph
							unet=handle_edge(unet,result_dict,field,rfc,id,c)
			c+=1			
		
	
	# Add legend nodes
	step = 60
	x = 0
	y = 0
	num_legend_nodes=3
	legend_labels=["Standards Track","Others","Obsolete"]
	legend_colors=["#018786","orange","red"]
	legend_nodes = [
		(
			legend_node, 
			{
				#'group': legend_node, 
				'label': legend_labels[legend_node],
				'size': 300, 
				'physics': False, 
				'x': x, 
				'y': f'{y + legend_node*step}px',
				'shape': 'box',
				'color': legend_colors[legend_node],  
				'widthConstraint': 80, 
				'font': {'size': 20},
				
			}
		)
		for legend_node in range(num_legend_nodes)
	]
	net.add_nodes_from(legend_nodes)

	#Parse networkx directed graph
	g.from_nx(net)
	
	#Graph to html file
	g.write_html("graphs/"+search_string+".html")
	
	# Return undirected  graph for enumeration
	return unet

def enum(results,unet):
	"""
		Basic evaluation of search results, momentarily returns nr of pages, obsoletes,updates
	"""	
	published=[]
	authors=set()
	for entry in results:
		#Count rfcs
		enum_dict["rfcs"]+=1
		#Count pages
		enum_dict["pages"]+=int(entry["page-count"])		
		#Count obsoletes and updates
		if "obsoletes" in entry:
			for id in entry["obsoletes"]["doc-id"]:
				enum_dict["obsoletes"]+=1
		if "updates" in entry:
			for id in entry["updates"]["doc-id"]:
				enum_dict["updates"]+=1		
		#Count authors
		if isinstance(entry["author"],dict):
			authors.add(entry["author"]["name"])
		else:
			for author in entry["author"]:
				authors.add(author["name"])		
		#Check status changes
		if entry["publication-status"] != entry["current-status"]:
			enum_dict["status_changes"]+=1
		published_date=entry["date"]["month"]+ " " + entry["date"]["year"]
		published_date=datetime.datetime.strptime(published_date,'%B %Y')
		published.append(published_date)
	enum_dict["first_published"]=min(published).date()
	enum_dict["latest_published"]=max(published).date()
	enum_dict["authors"]=len(authors)

	#Graph evaluation
	#Connected RFCs is Total - Standalones
	standalones=len(list(nx.isolates(unet)))
	enum_dict["rfc_chains"]=nx.number_connected_components(unet)-standalones
	enum_dict["connected_rfcs"]=len(unet)-standalones
	enum_dict["standalone_rfcs"]=standalones

	return enum_dict


def numbers(entries,unet):
	"""
		Simple numbers output to stdout
	"""
	enum(entries,unet)
	print("# Search complete - found ")
	for key,val in enum_dict.items():
		print(key.replace("_","-")+":"+str(val))

def list_outputvalues():
	print(",".join(default_values))

def output(result,outfile,outvals=default_values):
	"""
		Output matching RFCs in 
	"""
	with open(outfile,'w') as f_out:
		for entry in result:
			outfields={}
			for field in outvals:
				if field == "date":
					outfields[field]=entry[field]["month"]+ " " + entry[field]["year"]
				elif field == "title":
					outfields[field]=entry[field].replace(",","-")
				else:
					outfields[field]=entry[xml_dict[field]]
			f_out.write(",".join([x for x in outfields.values()])+"\n")

def main():
	"""
		Reads RFC-Index XML File and parses it into a searchable python3 dict, perform search, build graph and visualize it, perform basic evaluation and output resulting RFCs to csv 
	"""
	parser = argparse.ArgumentParser(description='Parse input.')
	parser.add_argument("-f", "--file", type=str, required=True, help='Path to the rfc-index')
	parser.add_argument("-s", "--search", type=str, required=False, default="all", help='Search keyword')
	parser.add_argument("-i", "--indexfields", type=str, required=False, default="title,keywords", help='Tags to perform search on "title,keywords,abstract" (default: "title,keywords")')
	parser.add_argument("-c", "--chain", type=int, required=False, default=0, help="follow obsoletes/obsoleted-by/updates/updated-by c steps (default: 0)")
	parser.add_argument("-o", "--outputfile", type=str, required=False, help='Path to output file (Output will be in csv format)')
	parser.add_argument("-v", "--outputvalues",type=str, required=False, help='Output values/fields (display with --list-outputvalues')
	parser.add_argument("-l", "--list-outputvalues", action='store_true',help='Lists output values/fields for outputfile')
	args = parser.parse_args()
	
	if args.list_outputvalues:
		list_outputvalues()
	else:
		with open(args.file) as f_xml:
			#Build RFC dict
			rfcdict=xmltodict.parse(f_xml.read())
			#Parse entries
			entries=rfcdict[list(rfcdict.keys())[0]]
			#Get fields to perform search on
			indexfields=args.indexfields.split(",")
			#Perform search
			result,result_dict=search(entries,args.search,indexfields,args.chain)
			result_dict=build_resultdict(result)			
			#Build directed graph for visualization and return undirected to number evaluation
			unet=nx_graph(result,result_dict,args.search)
			#Print some basic numbers about the resulting RFCs 
			numbers(result,unet)
			#Output resulting RFCs to file
			if args.outputfile:
				if args.outputvalues:
					output(result,args.outputfile,args.outputvalues)
				else:
					output(result,args.outputfile)


if __name__ == '__main__':
    main()