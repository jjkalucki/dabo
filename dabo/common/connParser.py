import xml.sax
from StringIO import StringIO
import os.path

class connHandler(xml.sax.ContentHandler):
	
	def __init__(self):
		self.connDict = {}
		self.blankConn = {"name": "",
				"dbtype" : "",
				"host" : "",
				"database" : "",
				"user" : "",
				"password" : "",
				"port" : ""		}
		self.currDict = self.blankConn.copy()
		self.element = None
				
	
	def startElement(self, name, attrs):
		self.element = name
		if name == "connection":
			for att in attrs.keys():
				if att == "dbtype":
					self.currDict["dbtype"] = attrs.getValue("dbtype")


	def characters(self, content):
		if self.element:
			if self.currDict.has_key(self.element):
				self.currDict[self.element] += content
			
	
	def endElement(self, name):
		if name == "connection":
			if self.currDict:
				# Save it to the conn dict
				nm = self.currDict["name"]
				if not nm:
					# name not defined: follow the old convention of user@host
					nm = self.currDict["name"] = ("%s@%s" 
						% (self.currDict["user"], self.currDict["host"]))
				self.connDict[nm] = self.currDict.copy()
				self.currDict = self.blankConn.copy()
		self.element = None
		
	
	def getConnectionDict(self):
		return self.connDict
	

def importConnections(file=None):
	if file is None:
		return None
	file = fileRef(file)
	ch = connHandler()
	xml.sax.parse(file, ch)
	ret = ch.getConnectionDict()
	return ret


def createXML(cxns):
	""" Returns the XML for the passed connection info. The info
	can either be a single dict of connection info, or a list/tuple of
	such dicts.
	"""
	ret = getXMLWrapper()
	cxml = ""
	if isinstance(cxns, (list, tuple)):
		for cx in cxns:
			cxml += genConnXML(cx)
	else:
		cxml = genConnXML(cxns)
	return ret % cxml
	
	
def genConnXML(d):
	""" Receive a dict containing connection info, and return
	a 'connection' XML element.
	"""
	try:
		if not d.has_key("name"):
			if not d["user"]:
				d["user"] = "anybody"
			if not d["host"]:
				d["host"] = "local"
			d["name"] = "%s@%s" % (d["user"], d["host"])
		ret = getConnTemplate() % (d["dbtype"], d["name"], d["host"], 
				d["database"], d["user"], d["password"], d["port"])
	except:
		# Not a valid conn info dict
		ret = ""
	return ret
	### pkm: I'm pretty sure we want to remove the above try block and propagate
	###      the exceptions instead of returning "", but am leaving it as-is for
	###      now for lack of time to test the repercussions.


def fileRef(ref=""):
	"""  Handles the passing of file names, file objects, or raw
	XML to the parser. Returns a file-like object, or None.
	"""
	ret = None
	if isinstance(ref, basestring):
		if os.path.exists(ref):
			ret = file(ref)
		else:
			ret = StringIO(ref)
	return ret
	
	
def getXMLWrapper():
	return """<?xml version="1.0"?>
<connectiondefs xmlns="http://www.dabodev.com"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.dabodev.com conn.xsd"
xsi:noNamespaceSchemaLocation = "http://dabodev.com/schema/conn.xsd">

%s

</connectiondefs>
"""


def getConnTemplate():
	return """	<connection dbtype="%s">
		<name>%s</name>
		<host>%s</host>
		<database>%s</database>
		<user>%s</user>
		<password>%s</password>
		<port>%s</port>
	</connection>
"""
				
