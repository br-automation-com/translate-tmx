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
DEFAULT_GUI_SIZE = {"TitleFontSize": 30, "FontSize": 24, "TooltipFontSize": 16, "WidgetHeight": 50, "ButtonWidth": 180}
gSizeRatio = 1
gAdjustedGuiSize = {}

# Application
TRANSLATORS = ["Google Translator", "DeepL Translator", "Linguee Translator", "MyMemory Translator", "Yandex Translator"]
TRANSLATORS_API_KEY = {"Google Translator": False, "DeepL Translator": True, "Linguee Translator": False, "MyMemory Translator": False, "Yandex Translator": True}
TRANSLATORS_LINK = {"Google Translator": "", "DeepL Translator": "https://www.deepl.com/pro-api?cta=header-pro-api/", "Linguee Translator": "", "MyMemory Translator": "", "Yandex Translator": "https://yandex.com/dev/translate/"}

NewLanguage = {"Source": "", "Target": ""}

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
		Self.CreateActions()

		# Show window
		ShowAdjusted(Self)

	# Global widgets of the window
	def CreateGlobalWidgets(Self):
		# Set frameless window
		Self.setWindowFlags(Self.windowFlags() | Qt.FramelessWindowHint)
		Self.setWindowTitle(WINDOW_TITLE)

		# Create title bar
		Self.TitleBar = TitleBar(Self, WINDOW_TITLE, WINDOW_COLOR_STYLE, True, True, True)
		Self.setContentsMargins(0, Self.TitleBar.height(), 0, 0)

		# Create bottom button bar
		Self.BottomBar = BottomBar(Self)
		
		# Create info dialog to inform the user
		Self.InfoD = InfoDialog()

		# Adjust window size
		Self.resize(800, Self.TitleBar.height())
		Self.setMaximumSize(1920, 1080)

		# Set window styles
		Style = """
		QWidget {
			background-color: qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #141414);
			color: #cccccc;
			font: ReplaceFontSizepx \"Bahnschrift SemiLight SemiConde\";
		}

		QGroupBox {
			border: 2px solid;
			border-color: ReplaceColor;
		}

		QToolTip {
			background-color: #eedd22;
			color: #111111;
			font: ReplaceTooltipFontSizepx \"Bahnschrift SemiLight SemiConde\";
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
			height: ReplaceWidgetHeightpx;
		}

		QLineEdit:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: #cccccc;
		}

		QPushButton {
			background-color: #3d3d3d;
			color: #cccccc;
			width: ReplaceButtonWidthpx;
			height: ReplaceWidgetHeightpx;
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
			width: ReplaceWidgetHeightpx;
			height: ReplaceWidgetHeightpx;
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
			height: ReplaceWidgetHeightpx;
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
		Self.setStyleSheet(FinishStyle(Style))

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
		Self.ApiKeyLE.setMinimumWidth(450)
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

	# Window actions
	def CreateActions(Self):
		# Actions of global buttons
		Self.BottomBar.CancelPB.clicked.connect(Self.close)
		Self.BottomBar.OkPB.clicked.connect(Self.StartTimer)
		Self.InfoD.ContinuePB.clicked.connect(Self.aInfoContinueClicked)
		Self.InfoD.NoPB.clicked.connect(Self.aInfoNoClicked)
		Self.InfoD.ExitPB.clicked.connect(Self.aInfoExitClicked)

		# Actions of form widgets
		Self.TranslatorCB.currentTextChanged.connect(Self.aTranslatorTextChanged)
		Self.ApiKeyLE.textChanged.connect(Self.aApiKeyTextChanged)
		Self.SourceLangCB.currentIndexChanged.connect(Self.CheckLanguages)
		Self.TargetLangCB.currentIndexChanged.connect(Self.CheckLanguages)
		Self.TranslatingT.timeout.connect(Self.aGuiAccepted)

	# Start timer
	def StartTimer(Self):
		# Get GUI data
		Translator = Self.TranslatorCB.currentText()
		ApiKey = Self.ApiKeyLE.text()
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
			Self.BottomBar.OkPB.setText("Translating...")
			Self.TranslatingT.start(100)

	# Close dialog info and continue in translating
	def aInfoContinueClicked(Self):
		if Self.InfoD.ContinuePB.text() == "Yes":
			Self.StartTimer()

		Self.InfoD.close()

	# Close dialog info and continue in translating
	def aInfoNoClicked(Self):
		Self.InfoD.NoPB.setVisible(False)
		Self.InfoD.ContinuePB.setText("Continue")
		Self.InfoD.close()

	# Close dialog info and also main dialog
	def aInfoExitClicked(Self):
		Self.InfoD.close()
		Self.close()

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

		# Parse selected tmx
		TmxTree = et.parse(os.path.join(LogicalPath, TmxFilePath))

		# Get texts from file
		TmxTexts = GetTextListFromDoc(TmxTree)

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
		ShowAdjusted(Self.InfoD)

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
		if Self.InfoD.ContinuePB.text() == "Yes":
			Self.InfoD.ContinuePB.setText("Continue")
			Self.InfoD.NoPB.setVisible(False)
			SourceLanguage = NewLanguage["Source"]
			TargetLanguage = NewLanguage["Target"]
		if SourceLangList != []:
			try:
				# Set positive label status
				Self.InfoD.MessageL.setText("Clear")
				
				if DEBUG: print("\n" + SourceLanguage + " -> " + TargetLanguage)

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
						if Language.lower() == TargetLanguage.lower():
							NewLanguage["Source"] = SourceLanguage
							NewLanguage["Target"] = Language[:Language.find("-")]
							ReplaceLanguage = "Target"
						else:
							NewLanguage["Source"] = Language[:Language.find("-")]
							NewLanguage["Target"] = TargetLanguage
							ReplaceLanguage = "Source"
						if NewLanguage["Source"] != NewLanguage["Target"]:
							Self.InfoD.ContinuePB.setText("Yes")
							Self.InfoD.NoPB.setVisible(True)
							Self.InfoD.MessageL.setText("Language <span style='color:#aa0000;font-weight:bold;'>" + Language + "</span> is not supported.<br/>Do you want to use <span style='color:#eedd22;font-weight:bold;'>" + NewLanguage[ReplaceLanguage] + "</span> language instead?")
						else:
							Self.InfoD.MessageL.setText("Language <span style='color:#aa0000;font-weight:bold;'>" + Language + "</span> is not supported.<br/>I would offer you to use <span style='color:#eedd22;font-weight:bold;'>" + NewLanguage[ReplaceLanguage] + "</span> language, but it is the source language.")
					else:
						Self.InfoD.MessageL.setText("Language <span style='color:#aa0000;font-weight:bold;'>" + Language + "</span> is not supported by the selected translator.")
				else:
					Self.InfoD.MessageL.setText(str(Exception))

			except requests.exceptions.ConnectionError:
				Self.InfoD.MessageL.setText("Connection error.")

			except exceptions.AuthorizationException:
				Self.InfoD.MessageL.setText("Bad API key.")

			except exceptions.ServerException:
				Self.InfoD.MessageL.setText("No or bad API key.")

			except exceptions.TooManyRequests as Exception:
				Self.InfoD.MessageL.setText("You have reached the translation limit of this translator for this day.")
				
			except:
				Self.InfoD.MessageL.setText("Translator error.")
			
			DebugPrint("Output", TargetLangList)
		else:
			Self.InfoD.MessageL.setText("No texts to translate.")
		
		# Caculate time of translation
		EndTime = time.time()
		if Self.InfoD.MessageL.text() == "Clear":
			TotalTime = str(EndTime - StartTime)
			TotalTime = TotalTime[:TotalTime.find(".") + 2]
			Self.InfoD.MessageL.setText("Texts have been translated.\nTotal time: " + TotalTime + " s")

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
	def __init__(Self, Parent, WindowTitle, TitleColor, UseMinButton, UseMaxButton, UseCloseButton):
		super(TitleBar, Self).__init__(Parent)

		# Title bar layout
		Layout = QHBoxLayout(Self)
		Layout.setContentsMargins(int(8 * gSizeRatio), int(8 * gSizeRatio),int(8 * gSizeRatio),int(8 * gSizeRatio))
		Layout.addStretch()

		# Label title
		Self.Title = QLabel(WindowTitle, Self, alignment = Qt.AlignCenter)
		Style = "background-color: ReplaceColor; color: #cccccc; font: ReplaceTitleFontSizepx \"Bahnschrift SemiLight SemiConde\"; padding-top: 4px;".replace("ReplaceColor", TitleColor)
		Self.Title.setStyleSheet(FinishStyle(Style))
		Self.Title.adjustSize()

		# Appearance definition
		Style = Self.style()
		Self.ReferenceSize = Self.Title.height() - int(18 * gSizeRatio)
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

		if not(UseMinButton): Self.minButton.hide()
		if not(UseMaxButton): Self.maxButton.hide()
		if not(UseCloseButton): Self.closeButton.hide()

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
		Self.Title.resize(Self.minButton.x() + Self.ReferenceSize * 3 + int(40 * gSizeRatio), Self.height())

# Window bottom button bar
class BottomBar(QWidget):
	# Initialization of the title bar
	def __init__(Self, Parent):
		super(BottomBar, Self).__init__(Parent)

		# Create bottom button box bar group box
		Self.BottomBarGB = QGroupBox()
		Self.BottomBarGB.setMaximumHeight(int(gAdjustedGuiSize["WidgetHeight"]) * 2)
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
			font: ReplaceFontSizepx \"Bahnschrift SemiLight SemiConde\";
			background-color: transparent;
		}

		QPushButton{
			background-color: #222222;
			color: #cccccc;
			width: ReplaceButtonWidthpx;
			height: ReplaceWidgetHeightpx;
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
		Self.BottomBarGB.setStyleSheet(FinishStyle(Style))

		# Add buttons OK and Cancel to bottom bar
		BottomBarHBL = QHBoxLayout(Self.BottomBarGB)

		# Version label
		VersionL = QLabel("ⓘ " + SCRIPT_VERSION)
		VersionL.setToolTip("""To get more information about each row, hold the pointer on its label.
		\nSupport contacts
		FirstName.LastName@br-automation.com
		\nVersion 1.0.0
		- Script creation
		- Basic functions implemented""")
		BottomBarHBL.addWidget(VersionL, 0, Qt.AlignLeft)

		Self.OkPB = QPushButton("Translate")
		BottomBarHBL.addWidget(Self.OkPB, 10, Qt.AlignRight)
		Self.CancelPB = QPushButton("Cancel")
		BottomBarHBL.addSpacing(10)
		BottomBarHBL.addWidget(Self.CancelPB, 0, Qt.AlignRight)

# Dialog for displaying info messages
class InfoDialog(QDialog):
	# Initialization of the dialog
	def __init__(Self):
		super(InfoDialog, Self).__init__()

		# Create title bar
		Self.TitleBar = TitleBar(Self, "Info", WINDOW_COLOR_STYLE, False, False, False)
		Self.setContentsMargins(0, Self.TitleBar.height(), 0, 0)

		# Set dialog styles
		Style = """
			QWidget{
				background-color:qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(20, 20, 20, 255));
				color:#cccccc;
				font: ReplaceFontSizepx \"Bahnschrift SemiLight SemiConde\";
			}

			QDialog{
				border: 2px solid ReplaceColor;
			}

			QLabel{
				background-color:transparent;
				color:#888888;
				qproperty-alignment: \'AlignVCenter | AlignCenter\';
				padding: 10px;
			}

			QPushButton{
				background-color: #222222;
				width: ReplaceButtonWidthpx;
				height: ReplaceWidgetHeightpx;
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
			"""
		Self.setStyleSheet(FinishStyle(Style))

		# Set general dialog settings
		Self.setWindowTitle("Info")
		Self.setWindowFlag(Qt.FramelessWindowHint)
		Self.setGeometry(0, 0, 100, 100)
		Self.setModal(True)

		# Create widgets
		MainVBL = QVBoxLayout(Self)

		Self.MessageL = QLabel()
		MainVBL.addWidget(Self.MessageL)
		
		ButtonBoxHBL = QHBoxLayout()
		Self.ContinuePB = QPushButton()
		Self.ContinuePB.setText("Continue")
		ButtonBoxHBL.addWidget(Self.ContinuePB)

		Self.NoPB = QPushButton()
		Self.NoPB.setText("No")
		Self.NoPB.setVisible(False)
		ButtonBoxHBL.addWidget(Self.NoPB)

		Self.ExitPB = QPushButton()
		Self.ExitPB.setText("Exit")
		ButtonBoxHBL.addWidget(Self.ExitPB)
		
		MainVBL.addLayout(ButtonBoxHBL)

	# Size of the window changed
	def resizeEvent(Self, Event: QEvent):
		Self.TitleBar.resize(Self.width(), Self.TitleBar.height())
		Self.TitleBar.Title.setMinimumWidth(Self.width())

# Dialog for displaying error messages
class ErrorDialog(QDialog):
	# Initialization of the dialog
	def __init__(Self, Messages):
		super(ErrorDialog, Self).__init__()

		# Create title bar
		Self.TitleBar = TitleBar(Self, "Error", "#6e1010", False, False, True)
		Self.setContentsMargins(0, Self.TitleBar.height(), 0, 0)

		# Set dialog styles
		Style = """
			QWidget{
				background-color:qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(20, 20, 20, 255));
				color:#cccccc;
				font: ReplaceFontSizepx \"Bahnschrift SemiLight SemiConde\";
			}

			QDialog{
				border: 2px solid #6e1010;
			}

			QLabel{
				background-color:transparent;
				color:#888888;
				padding: 5px;
			}
			"""
		Self.setStyleSheet(FinishStyle(Style))

		# Set general dialog settings
		Self.setWindowTitle("Error")
		Self.setWindowFlag(Qt.FramelessWindowHint)
		Self.setGeometry(0, 0, 100, 100)

		# Create widgets
		DialogVBL = QVBoxLayout(Self)

		for Message in Messages:
			ErrorL = QLabel(Message)
			ErrorL.setOpenExternalLinks(True)
			DialogVBL.addWidget(ErrorL)
	
		# Show dialog
		ShowAdjusted(Self)

	# Size of the window changed
	def resizeEvent(Self, Event: QEvent):
		Self.TitleBar.resize(Self.width(), Self.TitleBar.height())
		Self.TitleBar.Title.setMinimumWidth(Self.width())

#####################################################################################################################################################
# Global functions
#####################################################################################################################################################
# Show widget with adjusted size
def ShowAdjusted(Widget: QWidget):
	# Adjust window size and position (must be twice to really adjust the size)
	Widget.adjustSize()
	Widget.adjustSize()
	Rectangle = Widget.frameGeometry()
	CenterPoint = QDesktopWidget().availableGeometry().center()
	Rectangle.moveCenter(CenterPoint)
	Widget.move(Rectangle.topLeft())
	Widget.show()

def FinishStyle(Style: str):
	Style = Style.replace("ReplaceColor", WINDOW_COLOR_STYLE)
	for DefaultSizeElement in DEFAULT_GUI_SIZE:
		Style = Style.replace("Replace" + DefaultSizeElement, gAdjustedGuiSize[DefaultSizeElement])
	return Style

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
		DebugPrint("Error: File does not exist", FileName)
		sys.exit()
	return FilePath

# Get project info (project name, project path, path to logical)
def GetProjectInfo():
	CurrentPath = os.path.dirname(os.path.abspath(__file__))
	if (CurrentPath.find("Logical") == -1):
		DebugPrint("Error: Directory does not exist", "Logical")
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
def GetTextListFromDoc(Document: et.ElementTree):
	"""Function is used to return whole text  list from TMX document.

	Args:
		document (object): etree object

	Returns:
		dict: TMX content parsed into dictionary. [textName][langN] = text
	"""
	Root = Document.getroot()
	TextDict = {}

	for Tu in Root.iter('tu'):
		if 'tuid' in Tu.attrib:
			if not Tu.attrib['tuid'] in TextDict:
				TextDict[Tu.attrib['tuid']] = {}
				Note = Tu.find("note")
				if Note:
					TextDict[Tu.attrib['tuid']]["note"] = Note.text 
			for Tuv in Tu.iter('tuv'):
				if 'xml:lang' in Tuv.attrib:
					Lang = Tuv.attrib['xml:lang']
				elif '{http://www.w3.org/XML/1998/namespace}lang' in Tuv.attrib:
					Lang = Tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
				else:
					DebugPrint("Error: Cannot extract language while getting list from document.", "")
					return {}

				if not Lang in TextDict[Tu.attrib['tuid']]:
					TextDict[Tu.attrib['tuid']][Lang] = Tuv.find("seg").text

	return TextDict

#####################################################################################################################################################
# Main
#####################################################################################################################################################

# Get project info
ProjectName, ProjectPath, LogicalPath = GetProjectInfo()

# Create application
Application = QApplication(sys.argv)

# Get size ratio (get the width of the screen and divide it by 1920, because that's the size for which this GUI was designed)
gSizeRatio = Application.primaryScreen().availableGeometry().width() / 1920
# Calculate adjusted sizes
for DefaultSizeElement in DEFAULT_GUI_SIZE:
	gAdjustedGuiSize[DefaultSizeElement] = str(DEFAULT_GUI_SIZE[DefaultSizeElement] * gSizeRatio)[:str(DEFAULT_GUI_SIZE[DefaultSizeElement] * gSizeRatio).find(".")]

if ProjectName == "":
	Window = ErrorDialog(["Directory Logical not found. Please copy this script to the LogicalView of your project."])
elif (ConnectionStatus == 1) or (ConnectionStatus == 3):
	Window = ErrorDialog(["Unable to connect to the translate service.", "  - Verify your internet connection", "  - If you are in a corporate network, this feature may be blocked, use an external network"])
elif ConnectionStatus == 2:
	Window = ErrorDialog(["Module deep_translator not found. Please use pip to install the module.", "<a style='color:yellow; text-decoration:none' href='https://pip.pypa.io/en/stable/cli/pip_install/'>How to use PIP</a>", "<a style='color:yellow; text-decoration:none' href='https://pypi.org/project/deep-translator/#installation'>Installation of deep_translator</a>"])
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

	Window = MainWindow()
	
sys.exit(Application.exec())
