#   Copyright:  	B&R Industrial Automation
#   GUI author:		Michal Vavrik
#	Script author:	Michal Vavrik
#   Created:		Feb 04, 2022

#####################################################################################################################################################
# Dependencies
#####################################################################################################################################################
import os, sys, time, pickle, requests
import xml.etree.ElementTree as et

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Detect connection to Google translate
ConnectionStatus = 0
try:
	from deep_translator import (GoogleTranslator, DeepL, LingueeTranslator, MyMemoryTranslator, YandexTranslator, exceptions)
except requests.exceptions.ConnectionError:
	ConnectionStatus = 1
except ModuleNotFoundError:
	ConnectionStatus = 2
except:
	ConnectionStatus = 3

#####################################################################################################################################################
# Global constants and variables
#####################################################################################################################################################
# General
WINDOW_TITLE = "Translate TMX"
SCRIPT_VERSION = "1.0.0"
DEBUG = False

# Window style
WINDOW_COLOR_STYLE = "#4a2c0d"
WIDGETS_DEFAULT_HEIGHT = "50px"
FONT_DEFAULT_SIZE = "24px"

TRANSLATORS = ["Google Translator", "DeepL Translator", "Linguee Translator", "MyMemory Translator", "Yandex Translator"]
TRANSLATORS_API_KEY = {"Google Translator": False, "DeepL Translator": True, "Linguee Translator": False, "MyMemory Translator": False, "Yandex Translator": True}
TRANSLATORS_LINK = {"Google Translator": "", "DeepL Translator": "https://www.deepl.com/pro-api?cta=header-pro-api/", "Linguee Translator": "", "MyMemory Translator": "", "Yandex Translator": "https://yandex.com/dev/translate/"}

NewLanguage = ""

#####################################################################################################################################################
# Class definitions
#####################################################################################################################################################
# Main GUI window
class MainWindow(QWidget):
	# Initialization of the window
	def __init__(Self):
		super(MainWindow, Self).__init__()

		# Window functions
		Self.CreateGlobalWidgets()
		Self.CreateFormWidgets()
		Self.CreateInfoDialog()
		Self.CreateActions()
		Self.AdjustWindowSize()

		# Show window
		Self.show()

	# Global widgets of the window
	def CreateGlobalWidgets(Self):
		# Set frameless window
		Self.setWindowFlags(Self.windowFlags() | Qt.FramelessWindowHint)
		Self.setWindowTitle(WINDOW_TITLE)

		# Create title bar
		Self.TitleBar = TitleBar(Self)
		Self.setContentsMargins(0, Self.TitleBar.height(), 0, 0)

		# Create bottom button bar
		Self.BottomBar = BottomBar(Self)
		
		# Adjust window size
		Self.resize(800, Self.TitleBar.height())
		Self.setMaximumSize(1920, 1080)

		# Set window styles
		Style = """
		QWidget {
			background-color: qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #141414);
			color: #cccccc;
			font: ReplaceFont \"Bahnschrift SemiLight SemiConde\";
		}

		QGroupBox {
			border: 2px solid;
			border-color: ReplaceColor;
		}

		QToolTip {
			background-color: #eedd22;
			color: #111111;
			font: 16px \"Bahnschrift SemiLight SemiConde\";
			border: solid black 1px;
		}

		QLabel {
			background-color: transparent;
			color: #888888;
		}

		QLineEdit {
			background-color: #3d3d3d;
			color: #cccccc;
			border-radius: 8px;
			padding-left: 10px;
			height: ReplaceHeight;
		}

		QLineEdit:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: #cccccc;
		}

		QPushButton {
			background-color: #3d3d3d;
			color: #cccccc;
			width: 180px;
			height: ReplaceHeight;
			border-style: solid;
			border-radius: 8px;
		}

		QPushButton:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: #cccccc;
		}

		QPushButton:pressed {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #2d2d2d, stop:0.505682 #282828, stop:1 #2d2d2d);
			color: #ffffff;
		}
		
		QPushButton:checked {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #095209, stop:1 #0e780e);
			color:#ffffff;
		}

		QPushButton:checked:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #084209, stop:1 #0c660e);
		}

		QPushButton:checked:pressed {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #083108, stop:1 #0d570d);
		}

		QCheckBox {
			background-color: transparent;
			border-style: none;
		}

		QCheckBox::indicator {
			background-color: #3d3d3d;
			top: 2px;
			width: ReplaceHeight;
			height: ReplaceHeight;
			border-radius: 8px;
			margin-bottom: 4px;
		}

		QCheckBox::indicator:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
		}

		QCheckBox::indicator:pressed {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #2d2d2d, stop:0.505682 #282828, stop:1 #2d2d2d);
		}
		
		QCheckBox::indicator:checked {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #095209, stop:1 #0e780e);
		}

		QCheckBox::indicator:checked:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #084209, stop:1 #0c660e);
		}

		QCheckBox::indicator:checked:pressed {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #083108, stop:1 #0d570d);
		}

		QComboBox {
			background-color: #3d3d3d;
			color: #cccccc;
			height: ReplaceHeight;
			border: none;
			border-radius: 8px;
			padding-left: 10px;
		}

		QComboBox:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: #cccccc;
		}
		
		QComboBox::drop-down {
			background-color: #282828;
			width: 20px;
			border-top-right-radius: 8px;
			border-bottom-right-radius: 8px;
		}

		QComboBox QAbstractItemView {
			background-color: #3d3d3d;
			color: #cccccc;
		}
		"""
		Style = Style.replace("ReplaceColor", WINDOW_COLOR_STYLE)
		Style = Style.replace("ReplaceHeight", WIDGETS_DEFAULT_HEIGHT)
		Style = Style.replace("ReplaceFont", FONT_DEFAULT_SIZE)
		Self.setStyleSheet(Style)

		# Create main group box
		Self.MainGB = QGroupBox(Self)
		Self.MainGB.setGeometry(0, Self.TitleBar.height(), Self.width(), Self.height() - Self.TitleBar.height())

		# Create a form Layout
		Self.LayoutFL = QFormLayout()
		Self.LayoutFL.setHorizontalSpacing(20)

		# Set layout of window
		MainVBL = QVBoxLayout(Self)
		MainVBL.addLayout(Self.LayoutFL)
		MainVBL.addWidget(Self.BottomBar.BottomBarGB)

	# Form widgets
	def CreateFormWidgets(Self):
		# Translator selection
		Self.TranslatorCB = QComboBox()
		Self.TranslatorCB.addItems(TRANSLATORS)
		Self.TranslatorCB.setToolTip("Select translator")
		Self.TranslatorCB.setCurrentText(UserData["Translator"])
		TranslatorL = QLabel("Translator")
		TranslatorL.setToolTip("Select translator")
		Self.LayoutFL.addRow(TranslatorL, Self.TranslatorCB)

		# API key
		ApiKeyHBL = QHBoxLayout()
		ApiKeyHBL.setSpacing(5)
		Self.ApiKeyL = QLabel("API key")
		Self.ApiKeyL.setToolTip("The API key provides access to the translator")
		Self.ApiKeyL.setVisible(False)
		Self.ApiKeyLE = QLineEdit()
		Self.ApiKeyLE.setFixedWidth(450)
		Self.ApiKeyLE.setPlaceholderText("Enter your API key")
		Self.ApiKeyLE.setToolTip("The API key provides access to the translator")
		Self.ApiKeyLE.setVisible(False)
		ApiKeyHBL.addWidget(Self.ApiKeyLE)
		Self.ApiFreePB = QPushButton()
		Self.ApiFreePB.setText("FREE")
		Self.ApiFreePB.setCheckable(True)
		Self.ApiFreePB.setChecked(UserData["DeepLFree"])
		Self.ApiFreePB.setVisible(False)
		Self.ApiFreePB.setToolTip("If checked, FREE DeepL API is used.\nIf unchecked, PRO DeepL API is used.")
		Self.ApiFreePB.setStyleSheet("width: 60px;")
		ApiKeyHBL.addWidget(Self.ApiFreePB)
		Self.ApiLinkL = QLabel()
		Self.ApiLinkL.setToolTip("Click...")
		Self.ApiLinkL.setOpenExternalLinks(True)
		Self.ApiLinkL.setVisible(False)
		ApiKeyHBL.addWidget(Self.ApiLinkL)
		Self.LayoutFL.addRow(Self.ApiKeyL, ApiKeyHBL)

		# Init visibility of API key
		Self.aTranslatorTextChanged()

		# Tmx selection
		Self.TmxCB = QComboBox()
		Self.TmxCB.addItems(TmxCutPaths)
		Self.TmxCB.setToolTip("Select tmx file to translate")
		if (UserData["TmxFile"] != "") and (UserData["TmxFile"] in TmxCutPaths):
			Self.TmxCB.setCurrentText(UserData["TmxFile"])
		TmxL = QLabel("Tmx file")
		TmxL.setToolTip("Select tmx file to translate")
		Self.LayoutFL.addRow(TmxL, Self.TmxCB)

		# Source language selection
		Self.SourceLangCB = QComboBox()
		Self.SourceLangCB.addItems(Languages)
		Self.SourceLangCB.setToolTip("Select the source language from which the texts will be translated")
		if (UserData["SourceLanguage"] != "") and (UserData["SourceLanguage"] in Languages):
			Self.SourceLangCB.setCurrentText(UserData["SourceLanguage"])
		SourceLangL = QLabel("Source language")
		SourceLangL.setToolTip("Select the source language from which the texts will be translated")
		Self.LayoutFL.addRow(SourceLangL, Self.SourceLangCB)

		# Target language selection
		Self.TargetLangCB = QComboBox()
		Self.TargetLangCB.addItems(Languages)
		Self.TargetLangCB.setToolTip("Select the target language to which the texts will be translated")
		if (UserData["TargetLanguage"] != "") and (UserData["TargetLanguage"] in Languages):
			Self.TargetLangCB.setCurrentText(UserData["TargetLanguage"])
		elif len(Languages) > 1:
			Self.TargetLangCB.setCurrentIndex(1)
		TargetLangL = QLabel("Target language")
		TargetLangL.setToolTip("Select the target language to which the texts will be translated")
		Self.LayoutFL.addRow(TargetLangL, Self.TargetLangCB)

		# Waiting label
		WaitingL = QLabel("Translating may take a long time depending on server load, internet connection speed and amount of translated data.")
		WaitingL.setStyleSheet("font: 14px \"Bahnschrift SemiLight SemiConde\"; color:#666666;")
		WaitingL.setMargin(10)
		Self.LayoutFL.addRow(WaitingL)

		# Timer for translate waiting
		Self.TranslatingT = QTimer()

	# Info dialog to inform the user
	def CreateInfoDialog(Self):
		# Info dialog
		Self.InfoD = QDialog()
		Self.InfoD.setObjectName("InfoD")
		Self.InfoD.setWindowFlag(Qt.FramelessWindowHint)
		Self.InfoD.resize(300, 140)
		Self.InfoD.setModal(True)
		Self.InfoD.setStyleSheet("""
			QWidget{
				background-color:qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(20, 20, 20, 255));
				color:#cccccc;
				font: 24px \"Bahnschrift SemiLight SemiConde\";
			}

			QDialog#InfoD{
				border: 2px solid gray;
			}

			QLabel{
				background-color:transparent;
				color:#888888;
				qproperty-alignment: \'AlignVCenter | AlignCenter\';
			}

			QPushButton{
				background-color: #222222;
				width: 180px;
				height: 50px;
				border-style:solid;
				color:#cccccc;
				border-radius:8px;
			}

			QPushButton:hover{
				color:#cccccc;
				background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(55, 55, 55, 255), stop:0.505682 rgba(55, 55, 55, 255), stop:1 rgba(40, 40, 40, 255));
			}

			QPushButton:pressed{
				background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(45, 45, 45, 255), stop:0.505682 rgba(40, 40, 40, 255), stop:1 rgba(45, 45, 45, 255));
				color:#ffffff;
			}
			""")

		InfoVBL = QVBoxLayout(Self.InfoD)

		Self.InfoL = QLabel()
		InfoVBL.addWidget(Self.InfoL)
		
		ButtonBoxHBL = QHBoxLayout()
		Self.InfoContinuePB = QPushButton()
		Self.InfoContinuePB.setText("Continue")
		ButtonBoxHBL.addWidget(Self.InfoContinuePB)

		Self.InfoNoPB = QPushButton()
		Self.InfoNoPB.setText("No")
		Self.InfoNoPB.setVisible(False)
		ButtonBoxHBL.addWidget(Self.InfoNoPB)

		Self.InfoExitPB = QPushButton()
		Self.InfoExitPB.setText("Exit")
		ButtonBoxHBL.addWidget(Self.InfoExitPB)
		
		InfoVBL.addLayout(ButtonBoxHBL)

	# Window actions
	def CreateActions(Self):
		# Actions of global buttons
		Self.TranslatingT.timeout.connect(Self.aGuiAccepted)
		Self.BottomBar.CancelPB.clicked.connect(Self.close)

		# Actions of form widgets
		Self.TranslatorCB.currentTextChanged.connect(Self.aTranslatorTextChanged)
		Self.ApiKeyLE.textChanged.connect(Self.aApiKeyTextChanged)
		Self.SourceLangCB.currentIndexChanged.connect(Self.CheckLanguages)
		Self.TargetLangCB.currentIndexChanged.connect(Self.CheckLanguages)
		Self.BottomBar.OkPB.clicked.connect(Self.StartTimer)
		Self.BottomBar.CancelPB.clicked.connect(Self.close)
		Self.InfoContinuePB.clicked.connect(Self.DialogInfoContinue)
		Self.InfoNoPB.clicked.connect(Self.DialogInfoNo)
		Self.InfoExitPB.clicked.connect(Self.DialogInfoExit)

	# Adjusts window size and moves window to the center
	def AdjustWindowSize(Self):
		# Center window
		Self.adjustSize()
		Rectangle = Self.frameGeometry()
		CenterPoint = QDesktopWidget().availableGeometry().center()
		Rectangle.moveCenter(CenterPoint)
		Self.move(Rectangle.topLeft())

	# Start timer
	def StartTimer(Self):
		Self.BottomBar.OkPB.setText("Translating...")
		Self.TranslatingT.start(100)

	# Translator changed
	def aTranslatorTextChanged(Self):
		Text = Self.TranslatorCB.currentText()
		Self.ApiKeyL.setVisible(TRANSLATORS_API_KEY[Text])
		Self.ApiLinkL.setVisible(TRANSLATORS_API_KEY[Text])
		Self.ApiLinkL.setText("<a style='color:yellow; text-decoration:none' href='" + TRANSLATORS_LINK[Text] + "'>ⓘ</a>")
		Self.ApiKeyLE.setVisible(TRANSLATORS_API_KEY[Text])
		if "DeepL" in Text:
			Self.ApiFreePB.setVisible(True)
			if UserData["APIDeepL"] != "":
				Self.ApiKeyLE.setText(UserData["APIDeepL"])
		else:
			Self.ApiFreePB.setVisible(False)
		if "Yandex" in Text:
			if UserData["APIYandex"] != "":
				Self.ApiKeyLE.setText(UserData["APIYandex"])

	# Set default style of API key
	def aApiKeyTextChanged(Self):
		Self.ApiKeyLE.setStyleSheet("")

	# Check if source and target languages are different
	def CheckLanguages(Self):
		if (Self.SourceLangCB.currentText() == Self.TargetLangCB.currentText()):
			Self.SourceLangCB.setStyleSheet("QComboBox{background:#661111;}")
			Self.TargetLangCB.setStyleSheet("QComboBox{background:#661111;}")
		else:
			Self.SourceLangCB.setStyleSheet("")
			Self.TargetLangCB.setStyleSheet("")

	# GUI was accepted by OK button
	def aGuiAccepted(Self):
		# Stop timer
		Self.TranslatingT.stop()

		# Get GUI data
		Translator = Self.TranslatorCB.currentText()
		ApiKey = Self.ApiKeyLE.text()
		ApiFree = Self.ApiFreePB.isChecked()
		SourceLanguage = Self.SourceLangCB.currentText()
		TargetLanguage = Self.TargetLangCB.currentText()
		TmxFilePath = Self.TmxCB.currentText()

		# API key is empty
		if (ApiKey == "") and TRANSLATORS_API_KEY[Translator]:
			Self.ApiKeyLE.setStyleSheet("background:#661111;")
		# Source and target languages must be different
		elif SourceLanguage == TargetLanguage:
			Self.SourceLangCB.setStyleSheet("background:#661111;")
			Self.TargetLangCB.setStyleSheet("background:#661111;")
		# TMX file path must be specified
		elif TmxFilePath == "":
			Self.TmxCB.setStyleSheet("background:#661111;")
		else:
			if DEBUG: print("\n" + SourceLanguage + " -> " + TargetLanguage)

			# Parse selected tmx
			TmxTree = et.parse(os.path.join(LogicalPath, TmxFilePath))

			# Get texts from file
			TmxTexts = getTextListFromDoc(TmxTree)

			# Get unique list of texts to translate
			SourceLangList = Self.GetTexts(TmxTexts, SourceLanguage, TargetLanguage)

			# Translate texts with selected translator
			TargetLangList = Self.TranslateTexts(Translator, ApiKey, ApiFree, SourceLanguage, TargetLanguage, SourceLangList)
			
			# Add translated texts to the file
			Self.AppendTexts(TmxTree, SourceLanguage, TargetLanguage, SourceLangList, TargetLangList, TmxFilePath)

			# Store user data
			UserData["Translator"] = Translator
			if Translator == TRANSLATORS[1]:
				UserData["APIDeepL"] = ApiKey
			elif Translator == TRANSLATORS[4]:
				UserData["APIYandex"] = ApiKey
			UserData["DeepLFree"] = ApiFree
			UserData["TmxFile"] = TmxFilePath
			UserData["SourceLanguage"] = SourceLanguage
			UserData["TargetLanguage"] = TargetLanguage
			
			with open(UserDataPath, "wb") as TranslateTmxSettings:
				pickle.dump(UserData, TranslateTmxSettings)

			# Set text of Translate button back
			Self.BottomBar.OkPB.setText("Translate")

			# Show info dialog
			Self.InfoD.show()

	# Get unique list of texts to translate
	def GetTexts(Self, TmxTexts, SourceLanguage, TargetLanguage):
		TmxIDTexts = [*TmxTexts]
		SourceLangList = []
		for TmxIDText in TmxIDTexts:
			SourceText = TmxTexts[TmxIDText].get(SourceLanguage)
			TargetText = TmxTexts[TmxIDText].get(TargetLanguage)
			if (SourceText != None) and (TargetText == None):
				SourceLangList.append(SourceText)
		return list(set(SourceLangList))

	# Translate texts with selected translator
	def TranslateTexts(Self, Translator, ApiKey, ApiFree, SourceLanguage, TargetLanguage, SourceLangList):
		DebugPrint("Input", SourceLangList)
		TargetLangList = []
		StartTime = time.time()
		global NewLanguage
		if Self.InfoContinuePB.text() == "Yes":
			Self.InfoContinuePB.setText("Continue")
			Self.InfoNoPB.setVisible(False)
			TargetLanguage = NewLanguage
		if SourceLangList != []:
			try:
				# Set positive label status
				Self.InfoL.setText("Clear")

				# Google
				if Translator == TRANSLATORS[0]:
					TargetLangList = GoogleTranslator(source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)
				# DeepL
				elif Translator == TRANSLATORS[1]:
					TargetLangList = DeepL(api_key = ApiKey, source = SourceLanguage, target = TargetLanguage, use_free_api = ApiFree).translate_batch(SourceLangList)
				# Linguee
				elif Translator == TRANSLATORS[2]:
					TargetLangList = LingueeTranslator(source = SourceLanguage, target = TargetLanguage).translate_words(SourceLangList)
				# MyMemory
				elif Translator == TRANSLATORS[3]:
					TargetLangList = MyMemoryTranslator(source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)
				# Yandex
				elif Translator == TRANSLATORS[4]:
					TargetLangList = YandexTranslator(api_key = ApiKey, source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)

			except exceptions.LanguageNotSupportedException as Exception:
				if str(Exception).find("-->") != -1:
					Language = str(Exception)[:str(Exception).find("-->") - 1]
					if "-" in Language:
						NewLanguage = Language[:Language.find("-")]
						if SourceLanguage != NewLanguage:
							Self.InfoContinuePB.setText("Yes")
							Self.InfoNoPB.setVisible(True)
							Self.InfoL.setText("Language <span style='color:#aa0000;font-weight:bold;'>" + Language + "</span> is not supported.<br/>Do you want to use <span style='color:#eedd22;font-weight:bold;'>" + NewLanguage + "</span> language instead?")
						else:
							Self.InfoL.setText("Language <span style='color:#aa0000;font-weight:bold;'>" + Language + "</span> is not supported.<br/>I would offer you to use <span style='color:#eedd22;font-weight:bold;'>" + NewLanguage + "</span> language, but it is the source language.")
					else:
						Self.InfoL.setText("Language <span style='color:#aa0000;font-weight:bold;'>" + Language + "</span> is not supported.")
				else:
					Self.InfoL.setText(str(Exception))

			except requests.exceptions.ConnectionError:
				Self.InfoL.setText("Connection error")

			except exceptions.AuthorizationException:
				Self.InfoL.setText("Bad API key")

			except exceptions.ServerException:
				Self.InfoL.setText("No or bad API key")

			except exceptions.TooManyRequests as Exception:
				Self.InfoL.setText("You have reached the translation limit of this translator for this day")
				
			except:
				Self.InfoL.setText("Translator error")
			
			DebugPrint("Output", TargetLangList)
		else:
			Self.InfoL.setText("No texts to translate")
		
		# Caculate time of translation
		EndTime = time.time()
		if Self.InfoL.text() == "Clear":
			TotalTime = str(EndTime - StartTime)
			TotalTime = TotalTime[:TotalTime.find(".") + 2]
			Self.InfoL.setText("Texts have been translated\nTotal time: " + TotalTime + " s")

		return TargetLangList

	# Add translated texts to the file
	def AppendTexts(Self, TmxTree, SourceLanguage, TargetLanguage, SourceLangList, TargetLangList, TmxFilePath):
		if TargetLangList != []:
			TmxRoot = TmxTree.getroot()
			Body = TmxRoot.find(".//body")
			for Tu in Body.findall(".//tu"):
				TargetLanguagePresent = False
				for Tuv in Tu.findall(".//tuv"):
					if Tuv.get("{http://www.w3.org/XML/1998/namespace}lang") == TargetLanguage:
						TargetLanguagePresent = True
				if not(TargetLanguagePresent):
					for Tuv in Tu.findall(".//tuv"):
						if Tuv.get("{http://www.w3.org/XML/1998/namespace}lang") == SourceLanguage:
							for Index, SourceText in enumerate(SourceLangList):
								if Tuv.find(".//seg").text == SourceText:
									TuvNew = et.Element("tuv")
									TuvNew.attrib = {"{http://www.w3.org/XML/1998/namespace}lang": TargetLanguage}
									Seg = et.Element("seg")
									Seg.text = TargetLangList[Index]
									TuvNew.append(Seg)
									Tu.insert(0,TuvNew)

			TmxTree.write(os.path.join(LogicalPath, TmxFilePath))

	# Close dialog info and continue in translating
	def DialogInfoContinue(Self):
		if Self.InfoContinuePB.text() == "Yes":
			Self.StartTimer()

		Self.InfoD.close()

	# Close dialog info and continue in translating
	def DialogInfoNo(Self):
		Self.InfoNoPB.setVisible(False)
		Self.InfoContinuePB.setText("Continue")
		Self.InfoD.close()

	# Close dialog info and also main dialog
	def DialogInfoExit(Self):
		Self.InfoD.close()
		Self.close()

	# State of the window changed
	def changeEvent(Self, Event: QEvent):
		if Event.type() == Event.WindowStateChange:
			Self.TitleBar.windowStateChanged(Self.windowState())

	# Size of the window changed
	def resizeEvent(Self, Event: QEvent):
		Self.TitleBar.resize(Self.width(), Self.TitleBar.height())
		Self.MainGB.setGeometry(0, Self.TitleBar.height(), Self.width(), Self.height() - Self.TitleBar.height())

# Window title bar
class TitleBar(QWidget):
	ClickPosition = None

	# Initialization of the title bar
	def __init__(Self, Parent):
		super(TitleBar, Self).__init__(Parent)

		# Title bar layout
		Layout = QHBoxLayout(Self)
		Layout.setContentsMargins(8, 8, 8, 8)
		Layout.addStretch()

		# Label title
		Self.Title = QLabel(WINDOW_TITLE, Self, alignment = Qt.AlignCenter)
		Self.Title.setStyleSheet("background-color: ReplaceColor; color: #cccccc; font: 30px \"Bahnschrift SemiLight SemiConde\"; padding-top: 4px;".replace("ReplaceColor", WINDOW_COLOR_STYLE))

		# Appearance definition
		Style = Self.style()
		Self.ReferenceSize = Self.fontMetrics().height() + 4
		Self.ReferenceSize += Style.pixelMetric(Style.PM_ButtonMargin) * 2
		Self.setMaximumHeight(Self.ReferenceSize + 2)
		Self.setMinimumHeight(Self.Title.height() + 12)

		# Tool buttons (Min, Normal, Max, Close)
		ButtonSize = QSize(Self.ReferenceSize, Self.ReferenceSize)
		for Target in ("min", "normal", "max", "close"):
			Button = QToolButton(Self, focusPolicy=Qt.NoFocus)
			Layout.addWidget(Button)
			Button.setFixedSize(ButtonSize)

			IconType = getattr(Style.StandardPixmap, "SP_TitleBar{}Button".format(Target.capitalize()))
			
			Button.setIcon(Style.standardIcon(IconType))

			if Target == "close":
				ColorNormal = "gray"
				ColorHover = "orangered"
			else:
				ColorNormal = "gray"
				ColorHover = "white"

			Button.setStyleSheet("QToolButton {{background-color: {};border: none; border-radius: 4px;}} QToolButton:hover {{background-color: {}}}".format(ColorNormal, ColorHover))

			Signal = getattr(Self, Target + "Clicked")
			Button.clicked.connect(Signal)

			setattr(Self, Target + "Button", Button)

		Self.normalButton.hide()

	# State of the window changed
	def windowStateChanged(Self, State):
		Self.normalButton.setVisible(State == Qt.WindowMaximized)
		Self.maxButton.setVisible(State != Qt.WindowMaximized)

	# Mouse pressed event
	def mousePressEvent(Self, Event: QEvent):
		if Event.button() == Qt.LeftButton:
			Self.ClickPosition = Event.pos()

	# Mouse moved event
	def mouseMoveEvent(Self, Event: QEvent):
		if Self.ClickPosition is not None:
			Self.window().move(Self.window().pos() + Event.pos() - Self.ClickPosition)

	# Mouse released event
	def mouseReleaseEvent(Self, MouseEvent: QMouseEvent):
		Self.ClickPosition = None

	# Button Close clicked
	def closeClicked(Self):
		Self.window().close()

	# Button Maximize clicked
	def maxClicked(Self):
		Self.window().showMaximized()

	# Button Normal clicked
	def normalClicked(Self):
		Self.window().showNormal()

	# Button Minimize clicked
	def minClicked(Self):
		Self.window().showMinimized()

	# Size of the window changed
	def resizeEvent(Self, Event: QEvent):
		Self.Title.resize(Self.minButton.x() + Self.ReferenceSize * 3 + 20, Self.height())

# Window bottom button bar
class BottomBar(QWidget):
	# Initialization of the title bar
	def __init__(Self, Parent):
		super(BottomBar, Self).__init__(Parent)

		# Create bottom button box bar group box
		Self.BottomBarGB = QGroupBox()
		Self.BottomBarGB.setMaximumHeight(100)
		Style = """
		QGroupBox{
			background-color: transparent;
			border-top: 2px solid #222222;
			border-left: none;
			border-right: none;
			border-bottom: none;
			margin-top: 20px;
		}
			
		QToolTip {
			background-color: #eedd22;
		}

		QLabel {
			font: ReplaceFont \"Bahnschrift SemiLight SemiConde\";
			background-color: transparent;
		}

		QPushButton{
			background-color: #222222;
			color: #cccccc;
			width: 150px;
			height: ReplaceHeight;
			border-style: solid;
			border-radius: 8px;
		}

		QPushButton:hover{
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: #cccccc;
		}

		QPushButton:pressed{
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #2d2d2d, stop:0.505682 #282828, stop:1 #2d2d2d);
			color: #ffffff;
		}
		"""
		Style = Style.replace("ReplaceHeight", WIDGETS_DEFAULT_HEIGHT)
		Style = Style.replace("ReplaceFont", FONT_DEFAULT_SIZE)
		Self.BottomBarGB.setStyleSheet(Style)

		# Add buttons OK and Cancel to bottom bar
		BottomBarHBL = QHBoxLayout(Self.BottomBarGB)

		# Version label
		VersionL = QLabel("ⓘ " + SCRIPT_VERSION)
		VersionL.setToolTip("""To get more information about each row, hold the pointer on its label.
		\nSupport contacts
		michal.vavrik@br-automation.com
		\nVersion 1.0.0
		- Script creation
		- Basic functions implemented""")
		BottomBarHBL.addWidget(VersionL, 0, Qt.AlignLeft)

		Self.OkPB = QPushButton("OK")
		BottomBarHBL.addWidget(Self.OkPB, 10, Qt.AlignRight)
		Self.CancelPB = QPushButton("Cancel")
		BottomBarHBL.addSpacing(10)
		BottomBarHBL.addWidget(Self.CancelPB, 0, Qt.AlignRight)

#####################################################################################################################################################
# Global functions
#####################################################################################################################################################
# Debug printing
def DebugPrint(Message, Data):
	if DEBUG: print(">> " + Message + " >> " + str(Data))

# Finds file in directory and subdirectories, returns path to the FIRST found file and terminates script if file does not found and termination is required
# If *.extension FileName input (i.e. *.var) is specified, returns list of all occurrences of this extension
def FindFilePath(SourcePath, FileName, Terminate):
	if "*" in FileName: FilePath = []
	else: FilePath = ""
	EndLoop = False
	for DirPath, DirNames, FileNames in os.walk(SourcePath):
		if "*" in FileName:
			for File in FileNames:
				if File.endswith(FileName[1:]):
					FilePath.append(os.path.join(DirPath, File))
		else:
			for File in FileNames:
				if File == FileName:
					FilePath = os.path.join(DirPath, File)
					EndLoop = True
			if EndLoop:
				break
	if (FilePath == "" or FilePath == []) and Terminate:
		print("Error: File " + FileName + " does not exist.")
		sys.exit()
	return FilePath

# Get project info (project name, project path, path to logical)
def GetProjectInfo():
	CurrentPath = os.path.dirname(os.path.abspath(__file__))
	if (CurrentPath.find("Logical") == -1):
		print("Error: Directory 'Logical' does not exist.")
		ProjectName = ProjectPath = LogicalPath = ""
	else:
		# Get project path
		ProjectPath = CurrentPath[:CurrentPath.find("Logical") - 1]

		# Get project name
		ProjectName = os.path.basename(ProjectPath)

		# Get logical path
		LogicalPath = CurrentPath[:CurrentPath.find("Logical") + 7]

	return ProjectName, ProjectPath, LogicalPath

# Get project languages
def GetProjectLanguages():
	LanguagePath = FindFilePath(LogicalPath, "Project.language", False)
	Languages = []
	if LanguagePath != "":
		LanguageTree = et.parse(LanguagePath)
		LanguageRoot = LanguageTree.getroot()
		for TmxItem in LanguageRoot.findall(".//Element"):
			Languages.append(TmxItem.attrib["ID"])

	return Languages

# Get all paths to valid tmx files
def GetTmxPaths():
	TmxPaths = FindFilePath(LogicalPath, "*.tmx", False)

	# Remove undesirable Extension files
	PathsToRemove = []
	for TmxPath in TmxPaths:
		# Remove all "Libraries" files
		if "Libraries" in TmxPath:
			PathsToRemove.append(TmxPath)

	TmxPaths = list(set(TmxPaths) - set(PathsToRemove))

	TmxCutPaths = []
	for TmxPath in TmxPaths:
		TmxCutPaths.append(TmxPath[TmxPath.find("Logical") + 8:])

	return TmxPaths, TmxCutPaths

# Get tmx texts from file
def getTextListFromDoc(document):
    """Function is used to return whole text  list from TMX document.

    Args:
        document (object): etree object

    Returns:
        dict: TMX content parsed into dictionary. [textName][langN] = text
    """
    root = document.getroot()
    textDict = {}

    for tu in root.iter('tu'):
        if 'tuid' in tu.attrib:
            if not tu.attrib['tuid'] in textDict:
                textDict[tu.attrib['tuid']] = {}
                note = tu.find("note")
                if note:
                    textDict[tu.attrib['tuid']]["note"] = note.text 
            for tuv in tu.iter('tuv'):
                if 'xml:lang' in tuv.attrib:
                    lang = tuv.attrib['xml:lang']
                elif '{http://www.w3.org/XML/1998/namespace}lang' in tuv.attrib:
                    lang = tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                else:
                    print(f'Error: Cannot extract language language while getting list from document.')
                    return {}

                if not lang in textDict[tu.attrib['tuid']]:
                    textDict[tu.attrib['tuid']][lang] = tuv.find("seg").text

    return textDict 

# Logical folder not found -> show error message
def ErrorDialog(Message1, Message2 = "", Message3 = ""):
	# Create Self.InfoD gui
	Gui = QApplication([])
	Dialog = QDialog()
	Dialog.setStyleSheet("""
		QWidget{
			background-color:qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(20, 20, 20, 255));
			color:#cccccc;
			font: 24px \"Bahnschrift SemiLight SemiConde\";
		}
		
		QLabel{
			background-color:transparent;
			color:#bb2222;
			padding: 5px;
		}""")
	Dialog.setWindowTitle("Error")
	Dialog.setGeometry(0, 0, 600, 120)

	# Center window
	Rectangle = Dialog.frameGeometry()
	CenterPoint = QDesktopWidget().availableGeometry().center()
	Rectangle.moveCenter(CenterPoint)
	Dialog.move(Rectangle.topLeft())

	# Creating a group box
	DialogVBL = QVBoxLayout(Dialog)
	ErrorLabel1 = QLabel(Message1)
	ErrorLabel1.setOpenExternalLinks(True)
	DialogVBL.addWidget(ErrorLabel1)
	ErrorLabel2 = QLabel(Message2)
	ErrorLabel2.setOpenExternalLinks(True)
	DialogVBL.addWidget(ErrorLabel2)
	ErrorLabel3 = QLabel(Message3)
	ErrorLabel3.setOpenExternalLinks(True)
	DialogVBL.addWidget(ErrorLabel3)
	
	# Show Self.InfoD
	Dialog.show()
	Gui.exec()

#####################################################################################################################################################
# Main
#####################################################################################################################################################

# Get project info
ProjectName, ProjectPath, LogicalPath = GetProjectInfo()

if ProjectName == "":
	ErrorDialog("Directory Logical not found. Please copy this script to the LogicalView of your project.")

elif (ConnectionStatus == 1) or (ConnectionStatus == 3):
	ErrorDialog("Unable to connect to the translate service.", "  - Verify your internet connection", "  - If you are in a corporate network, this feature may be blocked, use an external network")
elif ConnectionStatus == 2:
	ErrorDialog("Module deep_translator not found. Please use pip to install the module.", "<a style='color:yellow; text-decoration:none' href='https://pip.pypa.io/en/stable/cli/pip_install/'>How to use PIP</a>", "<a style='color:yellow; text-decoration:none' href='https://pypi.org/project/deep-translator/#installation'>Installation of deep_translator</a>")
else:
	# Get project languages
	Languages = GetProjectLanguages()
	DebugPrint("Project languages", Languages)

	# Get all paths to valid tmx files
	TmxPaths, TmxCutPaths = GetTmxPaths()
	DebugPrint("TmxPaths", TmxCutPaths)

	# Get path to user data
	UserDataPath = os.path.join(os.getenv("APPDATA"), "BR", "Scripts", "TranslateTmx", ProjectName)
	if not os.path.isdir(os.path.dirname(UserDataPath)):
		os.makedirs(os.path.dirname(UserDataPath))

	# Load user data
	try:
		with open(UserDataPath, "rb") as TranslateTmxSettings:
			UserData = pickle.load(TranslateTmxSettings)
	except:
		UserData = {"Translator": TRANSLATORS[0], "APIDeepL": "", "APIYandex": "", "DeepLFree": True, "TmxFile": "", "SourceLanguage": "", "TargetLanguage": ""}

	if (len(UserData) != 7):
		UserData = {"Translator": TRANSLATORS[0], "APIDeepL": "", "APIYandex": "", "DeepLFree": True, "TmxFile": "", "SourceLanguage": "", "TargetLanguage": ""}

	DebugPrint("UserData", UserData)

	Application = QApplication(sys.argv)
	Window = MainWindow()
	sys.exit(Application.exec())
