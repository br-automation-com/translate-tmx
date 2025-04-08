#   Copyright:  	B&R Industrial Automation
#   GUI author:		Michal Vavrik
#	Script author:	Michal Vavrik
#   Created:		Feb 04, 2022

#####################################################################################################################################################
# Dependencies
#####################################################################################################################################################
import os, sys, time, pickle, requests, re
from typing import List
import xml.etree.ElementTree as et

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Detect connection to Google translate
ConnectionStatus = 0
try:
	from deep_translator import (GoogleTranslator, DeeplTranslator, LingueeTranslator, MyMemoryTranslator, YandexTranslator, exceptions)
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
SCRIPT_VERSION = "1.1.0"
DEBUG = False

# Window style
DEFAULT_GUI_FONT = "Bahnschrift SemiLight SemiConde"
DEFAULT_GUI_SIZE = {"TitleFont": 30, "Font": 24, "TooltipFont": 16, "WidgetHeight": 50, "ButtonWidth": 180}
DEFAULT_GUI_COLOR = {"WindowBorderStandard": "#111111",
					"WindowBorderError": "#6e1010",
					"Background": "#444444",
					"BackgroundInput": "#222222",
					"BackgroundOutput": "transparent",
					"ColorTitle": "#cccccc",
					"ColorInput": "#cccccc",
					"ColorOutput": "#ffffff",
					"ColorCheckBox": "#0e880e",
					"InputError": "#ee0000"}
gSizeRatio = 1
gAdjustedGuiSize = {}

# Application
TRANSLATORS = ["Google Translator", "DeepL Translator", "Linguee Translator", "MyMemory Translator", "Yandex Translator"]
TRANSLATOR_PRIVACY = [
	"I have read and agree to the terms and conditions of Google Translator (<a style='color:yellow; text-decoration:none' href='https://developers.google.com/terms#d_user_privacy_and_api_clients'>see link</a>).<br>B&R assumes no liability.",
	"I have read and agree to the terms and conditions of DeepL Translator (<a style='color:yellow; text-decoration:none' href='https://www.deepl.com/en/privacy'>see link</a>).<br>B&R assumes no liability.",
	"I have read and agree to the terms and conditions of Linguee Translator (<a style='color:yellow; text-decoration:none' href='https://www.linguee.com/english-czech/page/termsAndConditions.php'>see link</a>).<br>B&R assumes no liability.",
	"I have read and agree to the terms and conditions of MyMemory Translator (<a style='color:yellow; text-decoration:none' href='https://mymemory.translated.net/doc/en/tos.php'>see link</a>).<br>B&R assumes no liability.",
	"I have read and agree to the terms and conditions of Yandex Translator (<a style='color:yellow; text-decoration:none' href='https://yandex.com/legal/termsofservice/'>see link</a>).<br>B&R assumes no liability."
]
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
		Self.TitleBar = TitleBar(Self, WINDOW_TITLE, DEFAULT_GUI_COLOR["WindowBorderStandard"], True, True, True)
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
			background-color: >>Background<<;
			color: >>ColorInput<<;
			font: >>Font<<px ">>StandardFont<<";
		}

		QGroupBox {
			border: 2px solid >>WindowBorderStandard<<;
			border-top: 0px;
		}

		QTabWidget::pane {
			border-top: 2px solid #222222;
			background: rgb(245, 245, 245);
		}

		QTabBar::disabled {
			color: #555555;
		}

		QTabBar::tab::disabled {
			background-color: #3d3d3d;
		}

		QTabBar::tab {
			background-color: #353535;
			padding: 10px;
			margin-right: 4px;
			margin-bottom: 4px;
			border-radius: 12px;
		}

		QTabBar::tab:selected {
			background: #222222;
			color: #dddddd;
			margin-bottom: 0px;
			border-bottom-left-radius: 0px;
			border-bottom-right-radius: 0px;
		}

		QTabBar::tab:last {
			font: ReplaceFontSizepx "Bahnschrift SemiLight SemiConde";
			background-color: transparent;
			border-style: none;
			color: #888888;
		}

		QToolTip {
			background-color: #eedd22;
			color: #111111;
			font: >>TooltipFont<<px ">>StandardFont<<";
			border: solid black 1px;
		}

		QLabel {
			background-color: >>BackgroundOutput<<;
			color: >>ColorOutput<<;
			padding: 5px;
			border-radius: 8px;
		}

		QLineEdit {
			background-color: >>BackgroundInput<<;
			color: >>ColorInput<<;
			border-radius: 8px;
			padding-left: 10px;
			height: >>WidgetHeight<<px;
		}

		QLineEdit:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: >>ColorInput<<;
		}

		QPlainTextEdit {
			background-color: >>BackgroundInput<<;
			color: >>ColorInput<<;
			border-radius: 8px;
			padding-left: 10px;
			padding-top: 10px;
		}

		QPlainTextEdit:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: >>ColorInput<<;
		}

		QPushButton {
			background-color: >>BackgroundInput<<;
			color: >>ColorInput<<;
			width: >>ButtonWidth<<px;
			height: >>WidgetHeight<<px;
			border-style: solid;
			border-radius: 8px;
		}

		QPushButton:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: >>ColorInput<<;
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
			background-color: >>BackgroundInput<<;
			top: 2px;
			width: >>WidgetHeight<<px;
			height: >>WidgetHeight<<px;
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
			background-color: >>ColorCheckBox<<;
		}

		QCheckBox::indicator:checked:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #084209, stop:1 #0c660e);
		}

		QCheckBox::indicator:checked:pressed {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #083108, stop:1 #0d570d);
		}

		QComboBox {
			background-color: >>BackgroundInput<<;
			color: >>ColorInput<<;
			height: >>WidgetHeight<<px;
			border: none;
			border-radius: 8px;
			padding-left: 10px;
		}

		QComboBox:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: >>ColorInput<<;
		}

		QComboBox::drop-down {
			background-color: gray;
			width: 20px;
			border-top-right-radius: 8px;
			border-bottom-right-radius: 8px;
		}

		QComboBox QAbstractItemView {
			background-color: >>BackgroundInput<<;
			color: >>ColorInput<<;
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

		# Tmx selection
		Self.TmxCB = QComboBox()
		Self.TmxCB.addItems(TmxCutPaths)
		Self.TmxCB.setToolTip("Select tmx file to translate")
		if (UserData["TmxFile"] != "") and (UserData["TmxFile"] in TmxCutPaths):
			Self.TmxCB.setCurrentText(UserData["TmxFile"])
		Self.TmxL = QLabel("Tmx file")
		Self.TmxL.setToolTip("Select tmx file to translate")
		Self.LayoutFL.addRow(Self.TmxL, Self.TmxCB)

		# Source language selection
		Self.SourceLangCB = QComboBox()
		Self.SourceLangCB.addItems(Languages)
		Self.SourceLangCB.setToolTip("Select the source language from which the texts will be translated")
		if (UserData["SourceLanguage"] != "") and (UserData["SourceLanguage"] in Languages):
			Self.SourceLangCB.setCurrentText(UserData["SourceLanguage"])
		Self.SourceLangL = QLabel("Source language")
		Self.SourceLangL.setToolTip("Select the source language from which the texts will be translated")
		Self.LayoutFL.addRow(Self.SourceLangL, Self.SourceLangCB)

		# Target language selection
		Self.TargetLangCB = QComboBox()
		Self.TargetLangCB.addItems(Languages)
		Self.TargetLangCB.setToolTip("Select the target language to which the texts will be translated")
		if (UserData["TargetLanguage"] != "") and (UserData["TargetLanguage"] in Languages):
			Self.TargetLangCB.setCurrentText(UserData["TargetLanguage"])
		elif len(Languages) > 1:
			Self.TargetLangCB.setCurrentIndex(1)
		Self.TargetLangL = QLabel("Target language")
		Self.TargetLangL.setToolTip("Select the target language to which the texts will be translated")
		Self.LayoutFL.addRow(Self.TargetLangL, Self.TargetLangCB)

		# Waiting label
		Self.WaitingL = QLabel("Translating may take a long time depending on server load, internet connection speed and amount of translated data.")
		Self.WaitingL.setStyleSheet("font: 14px \"Bahnschrift SemiLight SemiConde\"; color: #666666;")
		Self.WaitingL.setMargin(10)
		Self.LayoutFL.addRow(Self.WaitingL)

		# Timer for translate waiting
		Self.TranslatingT = QTimer()

		# Terms of use
		Self.TermOfUseL = QLabel("I have read and agree to the terms and conditions of DeepL Free Translator (see link).<br>B&R assumes no liability.", alignment = Qt.AlignCenter)
		Self.TermOfUseL.setStyleSheet("font: 20px \"Bahnschrift SemiLight SemiConde\"; color: #cccccc;")
		Self.TermOfUseL.setMargin(10)
		Self.TermOfUseL.setOpenExternalLinks(True)
		Self.LayoutFL.addRow(Self.TermOfUseL)
		Self.TermOfUsePB = QPushButton()
		Self.TermOfUsePB.setText("Agree")
		Self.LayoutFL.addRow(Self.TermOfUsePB)

		# Init visibility of privacy
		Self.aAgreement(Self.TranslatorCB.currentIndex())

		# Init visibility of API key
		Self.aTranslatorTextChanged()

	# Window actions
	def CreateActions(Self):
		# Actions of global buttons
		Self.BottomBar.CancelPB.clicked.connect(Self.close)
		Self.BottomBar.OkPB.clicked.connect(Self.StartTimer)
		Self.InfoD.ContinuePB.clicked.connect(Self.aInfoContinueClicked)
		Self.InfoD.NoPB.clicked.connect(Self.aInfoNoClicked)
		Self.InfoD.ExitPB.clicked.connect(Self.aInfoExitClicked)

		# Actions of form widgets
		Self.TermOfUsePB.clicked.connect(lambda: Self.aAgreement(Self.TranslatorCB.currentIndex(), True))
		Self.TranslatorCB.currentTextChanged.connect(Self.aTranslatorTextChanged)
		Self.ApiKeyLE.textChanged.connect(Self.aApiKeyTextChanged)
		Self.SourceLangCB.currentIndexChanged.connect(Self.CheckLanguages)
		Self.TargetLangCB.currentIndexChanged.connect(Self.CheckLanguages)
		Self.TranslatingT.timeout.connect(Self.aGuiAccepted)

	# Terms of use agreement
	def aAgreement(Self, TranslatorIndex, Confirm = False):
		if Confirm:
			if ("DeepL" in Self.TranslatorCB.itemText(TranslatorIndex)) or ("Yandex" in Self.TranslatorCB.itemText(TranslatorIndex)):
				Self.ApiKeyL.setVisible(True)
				Self.ApiKeyLE.setVisible(True)
				Self.ApiLinkL.setVisible(True)
				if ("DeepL" in Self.TranslatorCB.itemText(TranslatorIndex)):
					Self.ApiFreePB.setVisible(True)
				else:
					Self.ApiFreePB.setVisible(False)
			Self.TmxL.setVisible(True)
			Self.TmxCB.setVisible(True)
			Self.SourceLangL.setVisible(True)
			Self.SourceLangCB.setVisible(True)
			Self.TargetLangL.setVisible(True)
			Self.TargetLangCB.setVisible(True)
			Self.WaitingL.setVisible(True)
			Self.BottomBar.OkPB.setVisible(True)
			Self.TermOfUseL.setVisible(False)
			Self.TermOfUsePB.setVisible(False)
			UserData["TermsOfUse"][TranslatorIndex] = True
		else:
			if not(UserData["TermsOfUse"][TranslatorIndex]):
				Self.ApiKeyL.setVisible(False)
				Self.ApiKeyLE.setVisible(False)
				Self.ApiFreePB.setVisible(False)
				Self.ApiLinkL.setVisible(False)
				Self.TmxL.setVisible(False)
				Self.TmxCB.setVisible(False)
				Self.SourceLangL.setVisible(False)
				Self.SourceLangCB.setVisible(False)
				Self.TargetLangL.setVisible(False)
				Self.TargetLangCB.setVisible(False)
				Self.WaitingL.setVisible(False)
				Self.BottomBar.OkPB.setVisible(False)
				Self.TermOfUseL.setVisible(True)
				Self.TermOfUsePB.setVisible(True)
				Self.TermOfUseL.setText(TRANSLATOR_PRIVACY[TranslatorIndex])
			else:
				if ("DeepL" in Self.TranslatorCB.itemText(TranslatorIndex)) or ("Yandex" in Self.TranslatorCB.itemText(TranslatorIndex)):
					Self.ApiKeyL.setVisible(True)
					Self.ApiKeyLE.setVisible(True)
					Self.ApiLinkL.setVisible(True)
					if ("DeepL" in Self.TranslatorCB.itemText(TranslatorIndex)):
						Self.ApiFreePB.setVisible(True)
					else:
						Self.ApiFreePB.setVisible(False)
				else:
					Self.ApiKeyL.setVisible(False)
					Self.ApiKeyLE.setVisible(False)
					Self.ApiFreePB.setVisible(False)
					Self.ApiLinkL.setVisible(False)
				Self.TmxL.setVisible(True)
				Self.TmxCB.setVisible(True)
				Self.SourceLangL.setVisible(True)
				Self.SourceLangCB.setVisible(True)
				Self.TargetLangL.setVisible(True)
				Self.TargetLangCB.setVisible(True)
				Self.WaitingL.setVisible(True)
				Self.BottomBar.OkPB.setVisible(True)
				Self.TermOfUseL.setVisible(False)
				Self.TermOfUsePB.setVisible(False)

		Self.adjustSize()
		Self.adjustSize()

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
		Self.ApiLinkL.setText("<a style='color:yellow; text-decoration:none' href='" + TRANSLATORS_LINK[Text] + "'>ⓘ</a>")
		if "DeepL" in Text:
			if UserData["APIDeepL"] != "":
				Self.ApiKeyLE.setText(UserData["APIDeepL"])
		if "Yandex" in Text:
			if UserData["APIYandex"] != "":
				Self.ApiKeyLE.setText(UserData["APIYandex"])

		# Agreement of selected translator
		Self.aAgreement(Self.TranslatorCB.currentIndex())

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
		SourceLangList, SourceLangListOrig, SnippetsList = Self.GetTexts(TmxTexts, SourceLanguage, TargetLanguage)

		# Translate texts with selected translator
		TargetLangList:List[str] = Self.TranslateTexts(Translator, ApiKey, ApiFree, SourceLanguage, TargetLanguage, SourceLangList)

		# Insert original snippets to the translated texts
		for Index, Snippets in enumerate(SnippetsList):
			for Snippet in Snippets:
				TargetLangList[Index] = TargetLangList[Index].replace("{}", "{&" + Snippet + "}", 1)
		
		# Add translated texts to the file
		Self.AppendTexts(TmxTree, SourceLanguage, TargetLanguage, SourceLangListOrig, TargetLangList, TmxFilePath)

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
		SourceLangListOrig = []
		SourceLangList = []
		SnippetsList = []
		
		# Get all text with no translation to the target language
		for TmxIDText in TmxIDTexts:
			SourceText:str = TmxTexts[TmxIDText].get(SourceLanguage)
			TargetText:str = TmxTexts[TmxIDText].get(TargetLanguage)
			if (SourceText != None) and (TargetText == None):
				SourceLangListOrig.append(SourceText)
				
		# Create unique set
		SourceLangListOrig = list(set(SourceLangListOrig))

		# Extract snippets
		for SourceText in SourceLangListOrig:
			Snippets = re.findall(r"\{&([^\n\}]*)\}", SourceText)
			SnippetsList.append(Snippets)
			SourceText = re.sub(r"\{&([^\n\}]*)\}", "{}", SourceText)
			SourceLangList.append(SourceText)

		return SourceLangList, SourceLangListOrig, SnippetsList

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
					TargetLangList = DeeplTranslator(api_key = ApiKey, source = SourceLanguage, target = TargetLanguage, use_free_api = ApiFree).translate_batch(SourceLangList)
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
				Self.InfoD.MessageL.setText("Connection error.\n - Verify your internet connection\n - If you are in a corporate network, this feature may be blocked, use an external network")

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
	def AppendTexts(Self, TmxTree: et.ElementTree, SourceLanguage, TargetLanguage, SourceLangListOrig, TargetLangList, TmxFilePath):
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
							for Index, SourceText in enumerate(SourceLangListOrig):
								if Tuv.find(".//seg").text == SourceText:
									TuvNew = et.Element("tuv")
									TuvNew.attrib = {"{http://www.w3.org/XML/1998/namespace}lang": TargetLanguage}
									Seg = et.Element("seg")
									Seg.text = TargetLangList[Index]
									TuvNew.append(Seg)
									Tu.insert(0,TuvNew)

			TmxTree.write(os.path.join(LogicalPath, TmxFilePath),encoding="utf-8")

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
		Style = """
		QLabel {
			background-color: >>TitleBarColor<<;
			color: >>ColorTitle<<;
			font: >>TitleFont<<px ">>StandardFont<<";
			padding-top: 4px;
			border-radius: 0px;
			border-bottom: 2px solid #ff8000;
		}
		"""
		Self.Title.setStyleSheet(FinishStyle(Style.replace(">>TitleBarColor<<", TitleColor)))
		Self.Title.adjustSize()

		# Appearance definition
		Style = Self.style()
		Self.ReferenceSize = Self.Title.height() - int(18 * gSizeRatio)
		Self.ReferenceSize += Style.pixelMetric(Style.PM_ButtonMargin) * 2
		Self.setMaximumHeight(Self.ReferenceSize + 2)
		Self.setMinimumHeight(Self.Title.height() + 12)

		# Tool buttons (Min, Normal, Max, Close)
		ButtonVisibility = {"min": UseMinButton, "normal": False, "max": UseMaxButton, "close": UseCloseButton}
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

			Button.setVisible(ButtonVisibility[Target])

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
		QGroupBox {
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
			background-color: transparent;
			font: >>Font<<px ">>StandardFont<<";
		}

		QPushButton {
			background-color: #222222;
			color: >>ColorInput<<;
			width: >>ButtonWidth<<px;
			height: >>WidgetHeight<<px;
			border-style: solid;
			border-radius: 8px;
		}

		QPushButton:hover {
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #373737, stop:0.505682 #373737, stop:1 #282828);
			color: >>ColorInput<<;
		}

		QPushButton:pressed {
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
		michal.vavrik@br-automation.com
		\nVersion 1.1.0
		- Non-translation of snippets
		\nVersion 1.0.2
		- Confirmation of Terms of Use added
		\nVersion 1.0.1
		- Adjustments for the new version of deep-translator library
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
		Self.TitleBar = TitleBar(Self, "Info", DEFAULT_GUI_COLOR["WindowBorderStandard"], False, False, False)
		Self.setContentsMargins(0, Self.TitleBar.height(), 0, 0)

		# Set dialog styles
		Style = """
			QWidget {
				background-color: >>Background<<;
				color: >>ColorInput<<;
				font: >>Font<<px ">>StandardFont<<";
			}

			QDialog {
				border: 2px solid >>WindowBorderStandard<<;
			}

			QLabel {
				background-color: >>BackgroundOutput<<;
				color: >>ColorOutput<<;
				qproperty-alignment: "AlignVCenter | AlignCenter";
				padding: 5px;
				border-radius: 8px;
			}

			QPushButton {
				background-color: #222222;
				width: >>ButtonWidth<<px;
				height: >>WidgetHeight<<px;
				border-style: solid;
				color: >>ColorInput<<;
				border-radius: 8px;
			}

			QPushButton:hover {
				color: >>ColorInput<<;
				background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(55, 55, 55, 255), stop:0.505682 rgba(55, 55, 55, 255), stop:1 rgba(40, 40, 40, 255));
			}

			QPushButton:pressed {
				background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(45, 45, 45, 255), stop:0.505682 rgba(40, 40, 40, 255), stop:1 rgba(45, 45, 45, 255));
				color: #ffffff;
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
			QWidget {
				background-color: >>Background<<;
				color: >>ColorInput<<;
				font: >>Font<<px ">>StandardFont<<";
			}

			QDialog {
				border: 2px solid >>WindowBorderError<<;
			}

			QLabel {
				background-color: >>BackgroundOutput<<;
				color: >>ColorOutput<<;
				padding: 5px;
				border-radius: 8px;
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
	Style = Style.replace(">>StandardFont<<", DEFAULT_GUI_FONT)
	for DefaultSizeElement in DEFAULT_GUI_SIZE:
		Style = Style.replace(">>" + DefaultSizeElement + "<<", gAdjustedGuiSize[DefaultSizeElement])
	for DefaultColorElement in DEFAULT_GUI_COLOR:
		Style = Style.replace(">>" + DefaultColorElement + "<<", DEFAULT_GUI_COLOR[DefaultColorElement])
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
		UserData = {"Translator": TRANSLATORS[0], "APIDeepL": "", "APIYandex": "", "DeepLFree": True, "TmxFile": "", "SourceLanguage": "", "TargetLanguage": "", "TermsOfUse": [False] * len(TRANSLATORS)}

	if (len(UserData) != 8):
		UserData = {"Translator": TRANSLATORS[0], "APIDeepL": "", "APIYandex": "", "DeepLFree": True, "TmxFile": "", "SourceLanguage": "", "TargetLanguage": "", "TermsOfUse": [False] * len(TRANSLATORS)}

	DebugPrint("UserData", UserData)

	Window = MainWindow()
	
sys.exit(Application.exec())
