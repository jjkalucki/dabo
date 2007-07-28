# -*- coding: utf-8 -*-
import sys, os, time
from dabo.dObject import dObject

class Log(dObject):
	""" Generic logger object for Dabo. 
	
	The main dabo module will instantiate singleton instances of this, which
	custom code can override to redirect the writing of informational and error
	messages.
	
	So, to display general informational messages, call:
		dabo.infoLog.write("message")
		
	For error messages, call:
		dabo.errorLog.write("message")
		
	By default, infoLog writes to stdout and errorLog to stderr. But your code
	can redirect these messages however you please. Just set the LogObject property
	to an instance that has a write() method that will receive and act on the 
	message. For example, you can redirect to a file:
	
		dabo.errorLog.LogObject = open("/tmp/error.log", "w")
		dabo.infoLog.LogObject = open("/dev/null", "w")
			
	You can set the logs to arbitrary objects. As long as the object has a write()
	method that receives a message parameter, it will work.
	"""
	
	def write(self, message):
		"""Writes the passed message to the log."""
		if self.LogObject is None:
			# Send messages to the bit bucket...
			return
		if self.LogTimeStamp:
			timestamp = "%s: " % time.asctime()
		else:
			timestamp = ""
		if len(self.Caption) > 0:
			caption = "%s: " % self.Caption
		else:
			caption = ""
		self.LogObject.write("%s%s%s%s" % (caption, timestamp, message, os.linesep))
		# Flush the log entry to the file
		try:
			self.LogObject.flush()
		except (AttributeError, IOError):
			pass
			
	
	def _getCaption(self):
		try:
			return self._caption
		except AttributeError:
			return ""
			
	def _setCaption(self, val):
		self._caption = str(val)
	
	
	def _getLogObject(self):
		try:
			return self._logObject
		except AttributeError:
			return sys.stdout
			
	def _setLogObject(self, logObject):
		# assume that logObject is an object with a write() method...
		self._logObject = logObject
				
	
	def _getLogTimeStamp(self):
		try:
			return self._logTimeStamp
		except AttributeError:
			return True
			
	def _setLogTimeStamp(self, val):
		self._logTimeStamp = bool(val)
		

	Caption = property(_getCaption, _setCaption, None,
		_("The log's label: will get prepended to the log entry"))
				
	LogObject = property(_getLogObject, _setLogObject, None, 
		_("The object that is to receive the log messages."))
	
	LogTimeStamp = property(_getLogTimeStamp, _setLogTimeStamp, None,
		_("Specifies whether a timestamp is logged with the message. Default: True"))
		
