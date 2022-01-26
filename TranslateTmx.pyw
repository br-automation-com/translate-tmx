#   Copyright:  B&R Industrial Automation
#   Authors:    Michal Vavrik
#   Created:	Dec 13, 2021 2:13 PM

ScriptVersion = "v1.0.0"

# TODO
# Maybe offer language code if code-country is not supported

DEBUG = False

import os, re, sys
import xml.etree.ElementTree as et
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import requests

# Detect connection to Google translate
ConnectionOk = True
try:
	from deep_translator import (GoogleTranslator,
                             DeepL,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             MicrosoftTranslator,
							 exceptions)
except:
	ConnectionOk = False


#####################################################################################################################################################
# Global variables and constants
#####################################################################################################################################################
TRANSLATORS = ["Google Translator", "DeepL Translator", "Linguee Translator", "MyMemory Translator", "Yandex Translator"]
TRANSLATORS_API_KEY = {"Google Translator": False, "DeepL Translator": True, "Linguee Translator": False, "MyMemory Translator": False, "Yandex Translator": True}
TRANSLATORS_LINK = {"Google Translator": "", "DeepL Translator": "https://www.deepl.com/pro-api?cta=header-pro-api/", "Linguee Translator": "", "MyMemory Translator": "", "Yandex Translator": "https://yandex.com/dev/translate/"}

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
	LanguagePath = FindFilePath(LogicalPath, "Project.language", True)
	LanguageTree = et.parse(LanguagePath)
	LanguageRoot = LanguageTree.getroot()
	Languages = []
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

# GUI
def GUI():
	# Create DialogInfo gui
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
			color:#888888;
		}

		QLineEdit{
			background-color:#3d3d3d;
			color:#cccccc;
			border:6;
			padding-left:10px;
			height: 50px;
			border-radius:8px;
		}

		QLineEdit:hover{
			color:#cccccc;
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(55, 55, 55, 255), stop:0.505682 rgba(55, 55, 55, 255), stop:1 rgba(40, 40, 40, 255));
		}

		QComboBox{
			background-color: #3d3d3d;
			color: #cccccc;
			border: none;
			border-radius: 8px;
			padding: 10px;
			position: center;
		}

		QComboBox:hover{
			color:#cccccc;
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(55, 55, 55, 255), stop:0.505682 rgba(55, 55, 55, 255), stop:1 rgba(40, 40, 40, 255));
		}

		QComboBox::drop-down {
			background-color: transparent;
		}

		QComboBox QAbstractItemView {
			color: #cccccc;
			background-color: #3d3d3d;
		}

		QCheckBox{
			border-style:none;
			background-color:transparent;
		}

		QCheckBox::indicator{
			top: 2px;
			width: 50px;
			height: 50px;
			background-color: #3d3d3d;
			border-radius:8px;
			margin-bottom: 4px;
		}

		QCheckBox::indicator:hover{
			background-color: qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(55, 55, 55, 255), stop:0.505682 rgba(55, 55, 55, 255), stop:1 rgba(40, 40, 40, 255));
		}

		QCheckBox::indicator:checked{
			background-color:qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #095209, stop:1 #0e780e);
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
			background-color:qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 rgba(45, 45, 45, 255), stop:0.505682 rgba(40, 40, 40, 255), stop:1 rgba(45, 45, 45, 255));
			color:#ffffff;
		}

		QPushButton:checked{
			background-color:qlineargradient(spread:pad, x1:0.517, y1:0, x2:0.517, y2:1, stop:0 #095209, stop:1 #0e780e);
			color:#ffffff;
		}

		QToolTip{
			font: 16px \"Bahnschrift SemiLight SemiConde\";
			background-color:#eedd22;
			color:#111111;
			border: solid black 1px;
		}

		QGroupBox{
			border-left: 2px solid;
			border-right: 2px solid;
			border-bottom: 2px solid;
			border-color: #362412;
			margin-top: 38px;
			border-radius: 0px;
		}

		QGroupBox::title{
			subcontrol-origin: margin;
			subcontrol-position: top center;
			padding: 5px 8000px;
			background-color: #362412;
		}
		""")

	# Dialog.setWindowFlag(Qt.FramelessWindowHint) # Borderless window
	Dialog.setWindowTitle(" ")
	Dialog.setGeometry(0, 0, 700, 300)

	# Center window
	Rectangle = Dialog.frameGeometry()
	CenterPoint = QDesktopWidget().availableGeometry().center()
	Rectangle.moveCenter(CenterPoint)
	Dialog.move(Rectangle.topLeft())

	# Creating a group box
	FormGroupBox = QGroupBox("Welcome to TranslateTmx wizard", parent=Dialog)

	# Creating a form layout
	Layout = QFormLayout(parent=FormGroupBox)
	Layout.setHorizontalSpacing(20)

	# Translator selection
	TranslatorComboBox = QComboBox()
	TranslatorComboBox.addItems(TRANSLATORS)
	TranslatorComboBox.setToolTip("Select translator")
	TranslatorLabel = QLabel("Translator")
	TranslatorLabel.setToolTip("Select translator")
	Layout.addRow(TranslatorLabel, TranslatorComboBox)

	# Api key
	ApiKeyHBL = QHBoxLayout()
	ApiKeyHBL.setSpacing(5)
	ApiKeyLabel = QLabel("Api key")
	ApiKeyLabel.setToolTip("Enter your api key")
	ApiKeyLabel.setVisible(False)
	ApiKeyLineEdit = QLineEdit()
	ApiKeyLineEdit.setPlaceholderText("Enter your api key")
	ApiKeyLineEdit.setToolTip("Enter your api key")
	ApiKeyLineEdit.setVisible(False)
	ApiKeyHBL.addWidget(ApiKeyLineEdit)
	ApiLinkLabel = QLabel()
	ApiLinkLabel.setOpenExternalLinks(True)
	ApiLinkLabel.setVisible(False)
	ApiKeyHBL.addWidget(ApiLinkLabel)
	Layout.addRow(ApiKeyLabel, ApiKeyHBL)

	# Tmx selection
	TmxComboBox = QComboBox()
	TmxComboBox.addItems(TmxCutPaths)
	TmxComboBox.setToolTip("Select tmx file to translate")
	TmxLabel = QLabel("Tmx file")
	TmxLabel.setToolTip("Select tmx file to translate")
	Layout.addRow(TmxLabel, TmxComboBox)

	# Source language selection
	SourceLangComboBox = QComboBox()
	SourceLangComboBox.addItems(Languages)
	SourceLangComboBox.setToolTip("Select the source language from which the texts will be translated")
	SourceLangLabel = QLabel("Source language")
	SourceLangLabel.setToolTip("Select the source language from which the texts will be translated")
	Layout.addRow(SourceLangLabel, SourceLangComboBox)

	# Target language selection
	TargetLangComboBox = QComboBox()
	TargetLangComboBox.addItems(Languages)
	TargetLangComboBox.setToolTip("Select the target language to which the texts will be translated")
	TargetLangComboBox.setCurrentIndex(1)
	TargetLangLabel = QLabel("Target language")
	TargetLangLabel.setToolTip("Select the target language to which the texts will be translated")
	Layout.addRow(TargetLangLabel, TargetLangComboBox)

	# Creating a DialogInfo button for ok and cancel
	FormButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
	FormButtonBox.button(QDialogButtonBox.Ok).setText("Translate")

	# Timer for translate waiting
	TranslatingTimer = QtCore.QTimer()

	# Version label
	VersionLabel = QLabel("ⓘ " + ScriptVersion, parent=FormButtonBox)
	VersionLabel.move(0, 10)
	VersionLabel.setStyleSheet("QLabel{font: 20px \"Bahnschrift SemiLight SemiConde\"; background-color: transparent;} QToolTip{background-color:#eedd22;}")
	VersionLabel.setToolTip("""To get more information about each row, hold the pointer on its label.
	\nSupport contacts
	michal.vavrik@br-automation.com
	\nVersion 1.0.0
	- Script creation
	- Basic functions implemented""")

	# Info dialog
	DialogInfo = QDialog()
	DialogInfo.setObjectName("DialogInfo")
	DialogInfo.setWindowFlag(Qt.FramelessWindowHint)
	DialogInfo.resize(300, 140)
	DialogInfo.setModal(True)
	DialogInfo.setStyleSheet("""
		QWidget{
			background-color:qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(20, 20, 20, 255));
			color:#cccccc;
			font: 24px \"Bahnschrift SemiLight SemiConde\";
		}

		QDialog#DialogInfo{
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

	DialogInfoVBL = QVBoxLayout(DialogInfo)

	LabelInfo = QLabel()
	DialogInfoVBL.addWidget(LabelInfo)
	
	ButtonBoxHBL = QHBoxLayout()
	DialogInfoPushButtonContinue = QPushButton()
	DialogInfoPushButtonContinue.setText("Continue")
	ButtonBoxHBL.addWidget(DialogInfoPushButtonContinue)

	DialogInfoPushButtonEnd = QPushButton()
	DialogInfoPushButtonEnd.setText("End")
	ButtonBoxHBL.addWidget(DialogInfoPushButtonEnd)
	
	DialogInfoVBL.addLayout(ButtonBoxHBL)

	# Adding actions for form
	TranslatorComboBox.currentTextChanged.connect(lambda Text: TranslatorChanged(Text, ApiKeyLabel, ApiLinkLabel, ApiKeyLineEdit))
	ApiKeyLineEdit.textChanged.connect(lambda: ApiKeyTextChanged(ApiKeyLineEdit))
	SourceLangComboBox.currentIndexChanged.connect(lambda: CheckLanguages(SourceLangComboBox, TargetLangComboBox))
	TargetLangComboBox.currentIndexChanged.connect(lambda: CheckLanguages(SourceLangComboBox, TargetLangComboBox))
	FormButtonBox.accepted.connect(lambda: TranslateTmx(TranslatorComboBox.currentText(), ApiKeyLineEdit, SourceLangComboBox.currentText(), TargetLangComboBox.currentText(), TmxComboBox.currentText(), DialogInfo, LabelInfo))
	FormButtonBox.rejected.connect(Dialog.reject)
	DialogInfoPushButtonContinue.clicked.connect(lambda: DialogInfoContinue(DialogInfo))
	DialogInfoPushButtonEnd.clicked.connect(lambda: DialogInfoEnd(Dialog, DialogInfo))
	TranslatingTimer.timeout.connect(lambda: ChangeTranslateText(FormButtonBox.button(QDialogButtonBox.Ok)))

	# Creating a vertical layout
	MainLayout = QVBoxLayout()

	# Adding form group box to the layout
	MainLayout.addWidget(FormGroupBox)

	# Adding button box to the layout
	MainLayout.addWidget(FormButtonBox)
	
	# Setting lay out
	Dialog.setLayout(MainLayout)

	# Show DialogInfo
	Dialog.show()

	Gui.exec()

# Translating status text
def ChangeTranslateText(Button: QPushButton):
	if "..." in Button.text():
		Button.setText("Translating.")
	elif ".." in Button.text():
		Button.setText("Translating...")
	else:
		Button.setText("Translating..")

# Translator changed
def TranslatorChanged(Text, ApiKeyLabel: QLabel, ApiLinkLabel: QLabel, ApiKeyLineEdit: QLineEdit):
	ApiKeyLabel.setVisible(TRANSLATORS_API_KEY[Text])
	ApiLinkLabel.setVisible(TRANSLATORS_API_KEY[Text])
	ApiLinkLabel.setText("<a style='color:yellow; text-decoration:none' href='" + TRANSLATORS_LINK[Text] + "'>ⓘ</a>")
	ApiKeyLineEdit.setVisible(TRANSLATORS_API_KEY[Text])

# Set default style of api key
def ApiKeyTextChanged(ApiKeyLineEdit: QLineEdit):
	ApiKeyLineEdit.setStyleSheet("")

# Check if source and target languages are different
def CheckLanguages(SourceLang: QComboBox, TargetLang: QComboBox):
	if (SourceLang.currentText() == TargetLang.currentText()):
		SourceLang.setStyleSheet("QComboBox{background:#661111;}")
		TargetLang.setStyleSheet("QComboBox{background:#661111;}")
	else:
		SourceLang.setStyleSheet("")
		TargetLang.setStyleSheet("")

# Translate selected file from source to target language
def TranslateTmx(Translator, ApiKeyLineEdit: QLineEdit, SourceLanguage, TargetLanguage, TmxFilePath, DialogInfo: QDialog, LabelInfo: QLabel):
	# Source and target languages must be different
	if (SourceLanguage != TargetLanguage) and ((ApiKeyLineEdit.text() != "") or not(TRANSLATORS_API_KEY[Translator])):
		if DEBUG: print("\n" + SourceLanguage + " -> " + TargetLanguage)

		# Parse selected tmx
		TmxTree = et.parse(os.path.join(LogicalPath, TmxFilePath))

		# Get texts from file
		TmxTexts = getTextListFromDoc(TmxTree)

		# Get unique list of texts to translate
		TmxIDTexts = [*TmxTexts]
		SourceLangList = []
		for TmxIDText in TmxIDTexts:
			SourceText = TmxTexts[TmxIDText].get(SourceLanguage)
			TargetText = TmxTexts[TmxIDText].get(TargetLanguage)
			if (SourceText != None) and (TargetText == None):
				SourceLangList.append(SourceText)
		SourceLangList = list(set(SourceLangList))

		# Translate texts with selected translator
		DebugPrint("Input", SourceLangList)
		TargetLangList = []
		if SourceLangList != []:
			try:
				# Google
				if Translator == TRANSLATORS[0]:
					TargetLangList = GoogleTranslator(source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)
				# DeepL
				elif Translator == TRANSLATORS[1]:
					TargetLangList = DeepL(api_key = ApiKeyLineEdit.text(), source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)
				# Linguee
				elif Translator == TRANSLATORS[2]:
					TargetLangList = LingueeTranslator(source = SourceLanguage, target = TargetLanguage).translate_words(SourceLangList)
				# MyMemory
				elif Translator == TRANSLATORS[3]:
					TargetLangList = MyMemoryTranslator(source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)
				# Yandex
				elif Translator == TRANSLATORS[4]:
					TargetLangList = YandexTranslator(api_key = ApiKeyLineEdit.text(), source = SourceLanguage, target = TargetLanguage).translate_batch(SourceLangList)
			except exceptions.LanguageNotSupportedException as Exception:
				LabelInfo.setText(str(Exception))
			except requests.exceptions.ConnectionError:
				LabelInfo.setText("Connection error")
			except exceptions.AuthorizationException:
				LabelInfo.setText("Bad Api key")
			except exceptions.ServerException:
				LabelInfo.setText("No or bad Api key")
			except:
				LabelInfo.setText("Translator error")
			
			DebugPrint("Output", TargetLangList)
		else:
			LabelInfo.setText("No texts to translate")

		# Add translated texts to read texts from file
		if TargetLangList != []:
			LabelInfo.setText("Texts have been translated")
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

		# Show info dialog
		DialogInfo.show()

	# Api key is empty
	elif (ApiKeyLineEdit.text() == "") and TRANSLATORS_API_KEY[Translator]:
		ApiKeyLineEdit.setStyleSheet("background:#661111;")

# Close dialog info and continue in translating
def DialogInfoContinue(DialogInfo: QDialog):
	DialogInfo.close()

# Close dialog info and also main dialog
def DialogInfoEnd(Dialog: QDialog, DialogInfo: QDialog):
	DialogInfo.close()
	Dialog.close()

# Logical folder not found -> show error message
def ErrorDialog(Message):
	# Create DialogInfo gui
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
			padding: 10px;
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
	ErrorLabel = QLabel(Message)
	DialogVBL.addWidget(ErrorLabel)
	
	# Show DialogInfo
	Dialog.show()
	Gui.exec()

#####################################################################################################################################################
# Main
#####################################################################################################################################################

# Get project info
ProjectName, ProjectPath, LogicalPath = GetProjectInfo()

if ProjectName == "":
	ErrorDialog("Directory Logical not found. Please copy this script to the LogicalView of your project.")

elif not(ConnectionOk):
	ErrorDialog("Unable to connect to the translate service.\n    1. Verify your internet connection\n    2. If you are in a corporate network, this feature may be blocked, use an external network")
else:
	# Get project languages
	Languages = GetProjectLanguages()
	DebugPrint("Project languages", Languages)

	# Get all paths to valid tmx files
	TmxPaths, TmxCutPaths = GetTmxPaths()
	DebugPrint("TmxPaths", TmxCutPaths)

	GUI()
