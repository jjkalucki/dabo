""" Grid.py

This is a grid designed to browse records of a bizobj. It is part of the 
dabo.lib.datanav subframework. It does not descend from dControlMixin at this 
time, but is self-contained. There is a dGridDataTable definition here as 
well, that defines the 'data' that gets displayed in the grid.
"""
import dabo
import dabo.ui
import dabo.dException as dException
dabo.ui.loadUI("wx")
from dabo.dLocalize import _, n_
import dabo.dEvents as dEvents

class Grid(dabo.ui.dGrid):
	def _initProperties(self):
		super(Grid, self)._initProperties()
		self.bindEvent(dEvents.GridMouseLeftDoubleClick, self.onGridLeftDClick)


	def _afterInit(self):
		super(Grid, self)._afterInit()
		##pkm self.bizobj = None
		self._fldSpecs = None
		self.skipFields = []
		self.fieldCaptions = {}
		self.colOrders = {}
		self.built = False
		self.customSort = True

	
	def getDataSet_old_pkm(self, requery=False):
		# Normally, getDataSet() just returns the object reference to the list
		# previously generated, but if we just requeried, we need to ask the 
		# bizobj for the new dataSet.
		if requery:
			ret = self.dataSet = None
		ret = self.dataSet
		if not ret:
			if not self.inAutoSizeCalc:
				if self.bizobj:
					ret = self.dataSet = self.bizobj.getDataSet()
		return ret
	

	def populate(self):
		##pkm ds = self.getDataSet(requery=True)
		ds = self.DataSet
		if not self.built and ds:
			self.buildFromDataSet(ds, 
					keyCaption=self.fieldCaptions, 
					columnsToSkip=self.skipFields, 
					colOrder=self.colOrders,
					colWidths=self.colWidths,
					autoSizeCols=False)
			self.built = True
		else:
			## pkm: this call appears to be redundant, as the grid as already been 
			##      filled in dGrid:
			#self.fillGrid(True)
			pass
		self.Form.refresh()
		

	def sort(self):
		# The superclass will have already set the sort properties.
		# We want to send those to the bizobj for sorting.
		bizobj = self.Form.getBizobj(self.DataSource)
		bizobj.sort(self.sortedColumn, self.sortOrder, self.caseSensitiveSorting)
		
	
	def setBizobj(self, biz):
		self.DataSource = biz.DataSource


	def onGridLeftDClick(self, evt): 
		""" Occurs when the user double-clicks a cell in the grid. 
		By default, this is interpreted as a request to edit the record.
		"""
		if self.Form.FormType == "PickList":
			self.pickRecord()
		else:
			self.editRecord()


	def processKeyPress(self, keyCode): 
		""" This is called when a key that the grid doesn't already handle
		gets pressed. We want to trap F2 and sort the column when it is
		pressed.
		"""
		if keyCode == 343:    # F2
			self.processSort()
			return True
		else:
			return super(Grid, self).processKeyPress(keyCode)


	def onEnterKeyAction(self):
		if self.Form.FormType == "PickList":
			self.pickRecord()
		else:
			self.editRecord()
	

	def onDeleteKeyAction(self):
		if self.Form.FormType != "PickList":
			self.deleteRecord()
	

	def onEscapeAction(self):
		if self.Form.FormType == "PickList":
			self.Form.close()


	def newRecord(self, evt=None):
		""" Request that a new row be added."""
		self.Parent.newRecord(self.DataSource)


	def editRecord(self, evt=None):
		""" Request that the current row be edited."""
		self.Parent.editRecord(self.DataSource)


	def deleteRecord(self, evt=None):
		""" Request that the current row be deleted."""
		self.Parent.deleteRecord(self.DataSource)
		self.setFocus()  ## required or assertion happens on Gtk


	def pickRecord(self, evt=None):
		""" The form is a picklist, and the user picked a record."""
		self.Form.pickRecord()
		
		
	def fillContextMenu(self, menu):
		""" Display a context menu of relevant choices.
	
		By default, the choices are 'New', 'Edit', and 'Delete'.
		"""
		if self.Form.FormType == 'PickList':
			menu.append(_("&Pick"), bindfunc=self.pickRecord, bmp="edit",
			            help=_("Pick this record"))
		else:
			menu.append(_("&New"), bindfunc=self.newRecord, bmp="blank",
			            help=_("Add a new record"))
			menu.append("&Edit", bindfunc=self.editRecord, bmp="edit",
			            help=_("Edit this record"))
			menu.append("&Delete", bindfunc=self.deleteRecord, bmp="delete",
			            help=_("Delete this record"))
		return menu


	def _getFldSpecs(self):
		return self._fldSpecs
	def _setFldSpecs(self, val):
		self._fldSpecs = val
		# Update the props
		self.skipFields = [kk for kk in val
				if val[kk]["listInclude"] == "0" ]
		self.fieldCaptions = {}
		for kk in val.keys():
			if kk in self.skipFields:
				continue
			self.fieldCaptions[kk] = val[kk]["caption"]

		self.colOrders = {}
		for kk in val.keys():
			if kk in self.skipFields:
				continue
			self.colOrders[kk] = int(val[kk]["listOrder"])

		self.colWidths = {}
		for kk in val.keys():
			if kk in self.skipFields:
				continue
			self.colWidths[kk] = int(val[kk]["listColWidth"])

	FieldSpecs = property(_getFldSpecs, _setFldSpecs, None, 
			_("Holds the fields specs for this form  (dict)") )

