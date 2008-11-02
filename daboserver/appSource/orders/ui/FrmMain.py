# -*- coding: utf-8 -*-

import dabo.ui
from MenFileOpen import MenFileOpen


class FrmMain(dabo.ui.dFormMain):

	def afterInit(self):
		self.super()
		self.fillFileOpenMenu()


	def initProperties(self):
		self.super()
		self.Icon = "daboIcon.ico"


	def fillFileOpenMenu(self):
		"""Add the File|Open menu, with menu items for opening each form."""
		app = self.Application
		fileMenu = self.MenuBar.getMenu("File")
		fileMenu.prependMenu(MenFileOpen(fileMenu))

