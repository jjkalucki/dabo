""" 
	dApp.py : The application object for Dabo.

	This object gets instantiated from the client app's main.py,
	and lives through the life of the application.

		-- set up an empty data connections object which holds 
		-- connectInfo objects connected to pretty names. Entries
		-- can be added programatically, but upon initialiazation
		-- it will look for a file called 'dbConnectionDefs.py' which
		-- contains connection definitions.

		-- Set up a DB Connection manager, that is basically a dictionary
		-- of dConnection objects. This allows connections to be shared
		-- application-wide.

		-- decide which ui to use (wx) and gets that ball rolling

		-- make a system menu bar, based on a combination
		-- of dabo defaults and user resource files.

		-- ditto for toolbar(s)

		-- look for a mainFrame ui resource file in an expected 
		-- place, otherwise uses default dabo mainFrame, and 
		-- instantiate that. 

		-- maintain a forms collection and provide interfaces for
		-- opening dForms, closing them, and iterating through them.

		-- start the main app event loop.

		-- clean up and exit gracefully
"""
import sys, os, warnings
import dabo, dabo.ui, dabo.db
import dabo.common, dSecurityManager
from dLocalize import _

class Collection(list):
	""" 
	Collection : Base class for the various collection
					classes used in the app object.
	"""

	def __init__(self):
		list.__init__(self)

	def add(self, objRef):
		""" 
		Collection.add(objRef)
			Add the object reference to the collection.
		"""
		self.append(objRef)

	def remove(self, objRef):
		""" 
		Collection.remove(objRef)
			Delete the object reference from the collection.
		"""
		try:
			index = self.index(objRef)
		except ValueError:
			index = None
		if index is not None:
			del self[index]


class dApp(dabo.common.dObject):
	""" dabo.dApp

		The containing object for the entire application.
		Various UI's will have app objects also, which 
		dabo.App is a wrapper for. 
	"""
	def __init__(self):
		self._uiAlreadySet = False
		dabo.dAppRef = self
		dApp.doDefault()
		self._initProperties()
		
### PKM: commented this out as I don't understand the need for it		
# 		# Params may need to be sent to the main frame. These two 
# 		# props allow that
# 		self.mainFrameParamList = []
# 		self.mainFrameKeyParamList = {}

	def setup(self):
		""" Set up the app - call this before start()."""

		# dabo is going to want to import various things from the Home Directory
		if self.HomeDirectory not in sys.path:
			sys.path.append(self.HomeDirectory)

		if not self.getAppInfo("appName"):
			self.setAppInfo("appName", "Dabo")
		if not self.getAppInfo("appVersion"):
			self.setAppInfo("appVersion", dabo.version["version"])
		if not self.getAppInfo("vendorName"):
			self.setAppInfo("vendorName", "Dabo")

		self._initDB()
		self._initUI()

		self.uiApp = dabo.ui.uiApp()

		self.actionList.setAction("FileExit", self.uiApp.onFileExit)
		self.actionList.setAction("HelpAbout", self.uiApp.onHelpAbout)
		self.actionList.setAction("EditPreferences", self.uiApp.onEditPreferences)
		self.actionList.setAction("EditCut", self.uiApp.onEditCut)
		self.actionList.setAction("EditCopy", self.uiApp.onEditCopy)
		self.actionList.setAction("EditPaste", self.uiApp.onEditPaste)
		self.actionList.setAction("EditFind", self.uiApp.onEditFind)
		self.actionList.setAction("EditFindAgain", self.uiApp.onEditFindAgain)
		self.actionList.setAction("EditUndo", self.uiApp.onEditUndo)
		self.actionList.setAction("EditRedo", self.uiApp.onEditRedo)

		self.uiApp.setup(self)


	def start(self):
		""" 
		Start the application event loop, which involves
			wrapping the application object for the ui library
			being used.
		"""
		if (not self.SecurityManager or not self.SecurityManager.RequireAppLogin
			or self.SecurityManager.login()):
			
			userName = self.getUserCaption()
			if userName:
				userName = " (%s)" % userName
			else:
				userName = ""
				
			self.uiApp.start(self)
		self.finish()


	def finish(self):
		""" 
		The main event loop has exited and the application
			is about to finish.
		"""
		self.uiApp.finish()
		dabo.infoLog.write(_("Application finished."))
		pass


	def getAppInfo(self, item):
		""" dApp.getAppInfo(self, item) -> value

			Look up the item, and return the value.
		"""
		try:
			retVal = self._appInfo[item]
		except KeyError:
			retVal = None
		return retVal


	def setAppInfo(self, item, value):
		""" dApp.getAppInfo(self, item, value) -> None

			Set item to value in the appinfo table.
		"""
		self._appInfo[item] = value


	def getUserSetting(self, item, user="*", system="*"):
		""" Return the value of the user settings table that 
			corresponds to the item, user, and system id 
			passed. Based on the ctype field in the table, 
			convert the return value into the appropriate
			type first.

			Types:    I: Int
					N: Float
					C: String
					M: String
					D: Date, saved as a string 3-tuple 
						of integers '(year,month,day)'
					T: DateTime, saved as a string 
						9-tuple of integers '(year,month,
						day,hour,minute,second,?,?,?)'

		"""
		import ConfigParser

		configFileName = '%s/.userSettings.ini' % self.HomeDirectory

		cp = ConfigParser.ConfigParser()
		cp.read(configFileName)

		try:
			valueType = cp.get("UserSettingsValueTypes", item)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			valueType = "C"

		try:
			if valueType == "I":
				value = cp.getint("UserSettings", item)
			elif valueType == "N":
				value = cp.getfloat("UserSettings", item)
			elif valueType == "L":
				value = cp.getboolean("UserSettings", item)
			else:
				value = cp.get("UserSettings", item)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			value = None

		return value


	def setUserSetting(self, item, valueType, value, user="*", system="*"):
		""" Set the value of the user settings table that corresponds to the
			item, user, and systemid passed. If it doesn't exist in the table,
			add it. See self.getUserSetting() for the type codes. 
		"""
		# For now, save this info in a plain ini file. Eventually, I'd like
		# to see this get saved in a persistent dabosettings db table.
		import ConfigParser

		configFileName = '%s/.userSettings.ini' % self.HomeDirectory

		cp = ConfigParser.ConfigParser()
		cp.read(configFileName)

		# convert value to string type for saving to db:
		value = str(value)

		if not cp.has_section("UserSettings"):
			cp.add_section("UserSettings")
		cp.set("UserSettings", item, value)

		if not cp.has_section("UserSettingsValueTypes"):
			cp.add_section("UserSettingsValueTypes")
		cp.set("UserSettingsValueTypes", item, valueType)

		configFile = open(configFileName, 'w')
		cp.write(configFile)
		configFile.close()
		
		
	def getUserCaption(self):
		""" Return the full name of the currently logged-on user.
		"""
		if self.SecurityManager:
			return self.SecurityManager.UserCaption
		else:
			return None
			

	def _initProperties(self):
		""" Initialize the public properties of the app object. """

		self.uiType   = None    # ('wx', 'qt', 'curses', 'http', etc.)
		#self.uiModule = None

		# Initialize UI collections
		self.uiForms = Collection()
		self.uiMenus = Collection()
		self.uiToolBars = Collection()
		self.uiResources = {}

		self.actionList = dabo.ui.dActionList()

		# Initialize DB collections
		self.dbConnectionDefs = {} 

		self._appInfo = {}

	def _initDB(self):
		""" Set the available connection definitions for use by the app. """

		dbConnectionDefs = None
		try:
			import dbConnectionDefs
			dbConnectionDefs = dbConnectionDefs.getDefs()
		except (ImportError, NameError, AttributeError):
			dbConnectionDefs = None

		if dbConnectionDefs and type(dbConnectionDefs) == type(dict()):
			# For each connection definition, add an entry to 
			# self.dbConnectionDefs that contains a key on the 
			# name, and a value of a dConnectInfo object.
			for entry in dbConnectionDefs:
				try:             dbType   = dbConnectionDefs[entry]['dbType']
				except KeyError: dbType   = None
				try:             host     = dbConnectionDefs[entry]['host']
				except KeyError: host     = None
				try:             user     = dbConnectionDefs[entry]['user']
				except KeyError: user     = None
				try:             password = dbConnectionDefs[entry]['password']
				except KeyError: password = None
				try:             dbName   = dbConnectionDefs[entry]['dbName']
				except KeyError: dbName   = None
				try:             port     = dbConnectionDefs[entry]['port']
				except KeyError: port     = None

				self.dbConnectionDefs[entry] = dabo.db.dConnectInfo(backendName=dbType,
						host=host, 
						user=user,
						password=password,
						dbName=dbName,
						port=port)

			dabo.infoLog.write(_("%s database connection definition(s) loaded.") % (
												len(self.dbConnectionDefs)))

		else:
			dabo.infoLog.write(_("No database connection definitions loaded (dbConnectionDefs.py)"))


	def _initUI(self):
		""" Set the user-interface library for the application. 
		
		Ignored if the UI was already explicitly set by user code.
		"""
		if self.UI is None and not self._uiAlreadySet:
			# For now, default to wx, but it should be enhanced to read an
			# application config file. Actually, that may not be necessary, as the
			# user's main.py can just set the UI directly now: dApp.UI = "qt".
			self.UI = "wx"
		else:
			# Custom app code or the dabo.ui module already set this: don't touch
			dabo.infoLog.write(_("User interface already set to '%s', so dApp didn't "
				" touch it." % (self.UI,)))


	def _getAutoNegotiateUniqueNames(self):
		try:
			return self._autoNegotiateUniqueNames
		except AttributeError:
			return True
	
	def _setAutoNegotiateUniqueNames(self, value):
		self._autoNegotiateUniqueNames = bool(value)
		
	
	def _getHomeDirectory(self):
		try:
			hd = self._homeDirectory
		except AttributeError:
			# Note: sometimes the runtime distros will alter the path so
			# that the first entry is not a valid directory. Go through the path
			# and use the first valid directory.
			hd = None
			for pth in sys.path:
				if os.path.exists(os.path.join(pth, ".")):
					hd = pth
					break
			if hd is None:
				# punt:
				hd = os.getcwd()
			self._homeDirectory = hd
			
		return hd
		
	def _setHomeDirectory(self, val):
		self._homeDirectory = val

				
	def _getMainForm(self):
		try:
			f = self._mainForm
		except AttributeError:
			f = None
			self._mainForm = None
		return f
			
	def _setMainForm(self, val):
		self._mainForm = val

				
	def _getMainFormClass(self):
		try:
			c = self._mainFormClass
		except AttributeError:
			c = dabo.ui.dFormMain
			self._mainFormClass = c
		return c
			
	def _setMainFormClass(self, val):
		self._mainFormClass = val
		
		
	def _getSecurityManager(self):
		try:
			return self._securityManager
		except AttributeError:
			return None
			
	def _setSecurityManager(self, value):
		if isinstance(value, dSecurityManager.dSecurityManager):
			if self.SecurityManager:
				warnings.warn(Warning, _('SecurityManager previously set'))
			self._securityManager = value
		else:
			raise TypeError, _('SecurityManager must descend from dSecurityManager.')
			
			
	def _getUI(self):
		try:
			return dabo.ui.getUIType()
		except AttributeError:
			return None
			
	def _setUI(self, uiType):
		# Load the appropriate ui module. dabo.ui will now contain
		# the classes of that library, wx for instance.
		if self.UI is None:
			if dabo.ui.loadUI(uiType):
				self._uiAlreadySet = True
				dabo.infoLog.write(_("User interface set to '%s' by dApp.") % (uiType,))
			else:
				dabo.infoLog.write(_("Tried to set UI to '%s', but it failed." % (uiType,)))
		else:
			raise RuntimeError, _("The UI cannot be reset once assigned.")
	
	
	AutoNegotiateUniqueNames = property(_getAutoNegotiateUniqueNames,_setAutoNegotiateUniqueNames,
						None, _("Specifies whether setting an object\'s name to a non-unique "
						"value results in a unique integer being appended, or whether "
						"a NameError is raised. Default is True: negotiate the name."))

	HomeDirectory = property(_getHomeDirectory, _setHomeDirectory, None,
		_("Specifies the home-base directory for the application's program files."))
		
	MainForm = property(_getMainForm, _setMainForm, None,
		_("The object reference to the main form of the application, or None. This gets "
		"set automatically during application setup, based on the MainFormClass."))
		
	MainFormClass = property(_getMainFormClass, _setMainFormClass, None,
		_("Specifies the class to use to instantiate the main form. Defaults to "
		"the dFormMain base class. Set to None if you don't want a main form."))
		
	UI = property(_getUI, _setUI,
						None, _("Specifies the user interface to load, or None. "
						"Once set, it cannot be reassigned."))
	
	SecurityManager = property(_getSecurityManager, _setSecurityManager,
						None, _("Specifies the Security Manager, if any. You "
						"must subclass dSecurityManager, overriding the appropriate hooks "
						"and properties, and then set dApp.SecurityManager to an instance "
						"of your subclass. There is no security manager by default - you "
						"explicitly set this to use Dabo security."))
