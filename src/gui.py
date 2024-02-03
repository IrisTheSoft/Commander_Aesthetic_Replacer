import csv as CSV
import dataclasses as DC
import json as JSON
import pathlib as PTH
import sys as SYS
import typing as TP

import PySide6.QtCore as QTC
import PySide6.QtGui as QTG
import PySide6.QtWidgets as QTW

from wows_io import WowsIo


title = "Commander Aesthetic Replacer"

_none_sentinel = "(None)"


@DC.dataclass
class RecipientCommander:
    name_id: str
    portrait_path: PTH.Path
    voice_id: str


@DC.dataclass
class Mod:
    name_changes: TP.Dict[str, str]
    portrait_changes: TP.Dict[PTH.Path, PTH.Path]
    voice_changes: TP.Dict[str, str]


class FileSelectorWidget(QTW.QWidget):

    def __init__(self, default_path: PTH.Path, value: str = ""):
        super().__init__()
        self.value = value
        self._default_path = default_path

        layout = QTW.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._button = QTW.QPushButton()
        self._button.setText("Select")
        self._button.clicked.connect(self._select)
        layout.addWidget(self._button, 0)

        self._label = QTW.QLabel()
        self._label.setText("/".join(self.value.rsplit("/", 2)[1:]))
        layout.addWidget(self._label)

        self.setLayout(layout)

    def _select(self) -> None:
        self.value = QTW.QFileDialog.getOpenFileName(self, "Open file",
                                                     self._default_path.as_posix())[0]
        self._label.setText("/".join(self.value.rsplit("/", 2)[1:]))


class ChangesWidget(QTW.QWidget):

    def __init__(self, commanders: TP.Dict[str, RecipientCommander],
                 default_portrait_dir: PTH.Path, voice_overs: TP.List[str]):
        super().__init__()
        layout = QTW.QGridLayout()

        self._commanders = commanders
        self._default_portrait_dir = default_portrait_dir
        self._voice_overs = voice_overs

        for column, text in enumerate(["Commander", "Name", "Portrait", "Voice over"]):
            layout.addWidget(QTW.QLabel(text), 0, column)

        self._add_button = QTW.QPushButton()
        self._add_button.setText("Add")
        self._add_button.clicked.connect(self.add_row)
        layout.addWidget(self._add_button, 0, column+1)

        self.setLayout(layout)

    def add_row(self, commander: str = "", name: str = "", portrait: str = "",
                voice_over: str = "") -> None:
        layout = self.layout()
        row = layout.rowCount()
        commander_input = QTW.QComboBox()
        commander_input.addItems(self._commanders.keys())
        commander_input.setCurrentText(commander)
        name_input = QTW.QLineEdit()
        name_input.setText(name)
        portrait_input = FileSelectorWidget(self._default_portrait_dir, portrait)
        voice_over_input = QTW.QComboBox()
        voice_over_input.addItem(_none_sentinel)
        voice_over_input.addItems(self._voice_overs)
        voice_over_input.setCurrentText(voice_over)
        remove_button = QTW.QPushButton()
        remove_button.setText("Remove")
        remove_button.clicked.connect(lambda: self._remove_row(row))
        layout.addWidget(commander_input, row, 0)
        layout.addWidget(name_input, row, 1)
        layout.addWidget(portrait_input, row, 2)
        layout.addWidget(voice_over_input, row, 3)
        layout.addWidget(remove_button, row, 4)

    def _remove_row(self, row_index: int) -> None:
        layout = self.layout()
        for column_index in range(5):
            widget = layout.itemAtPosition(row_index, column_index).widget()
            layout.removeWidget(widget)
            widget.setParent(None)

    def get_changes(self) -> Mod:
        layout = self.layout()
        name_changes = {}
        portrait_changes = {}
        voice_changes = {}
        for row in range(1, layout.rowCount()):
            if layout.itemAtPosition(row, 0) is not None:
                recipient = self._commanders[
                    layout.itemAtPosition(row, 0).widget().currentText()]
                name = layout.itemAtPosition(row, 1).widget().text()
                portrait = layout.itemAtPosition(row, 2).widget().value
                voice_over = layout.itemAtPosition(row, 3).widget().currentText()
                if name != "":
                    name_changes[recipient.name_id] = name
                if portrait != "":
                    portrait_changes[recipient.portrait_path] = PTH.Path(portrait)
                if voice_over not in [_none_sentinel, ""]:
                    voice_changes[recipient.voice_id] = voice_over
        return Mod(name_changes, portrait_changes, voice_changes)

    def get_changes_as_json(self) -> TP.List[TP.Dict[str, str]]:
        changes = []
        layout = self.layout()
        for row in range(1, layout.rowCount()):
            if layout.itemAtPosition(row, 0) is not None:
                changes.append({
                    "commander": layout.itemAtPosition(row, 0).widget().currentText(),
                    "name": layout.itemAtPosition(row, 1).widget().text(),
                    "portrait": layout.itemAtPosition(row, 2).widget().value,
                    "voice_over": layout.itemAtPosition(row, 3).widget().currentText()
                })
        return changes



class MainWidget(QTW.QWidget):

    def __init__(self, commanders: TP.Dict[str, RecipientCommander],
                 languages: TP.List[str], default_portrait_dir: PTH.Path,
                 voice_overs: TP.List[str], io: WowsIo,
                 session: TP.Optional[dict] = None):
        super().__init__()
        self._io = io
        main_layout = QTW.QVBoxLayout()

        self._changes_widget = ChangesWidget(commanders, default_portrait_dir,
                                             voice_overs)
        main_layout.addWidget(self._changes_widget)

        form_layout = QTW.QFormLayout()
        form_layout.setLabelAlignment(QTC.Qt.AlignmentFlag.AlignRight)

        self._language_widget = QTW.QComboBox()
        self._language_widget.addItems(languages)
        form_layout.addRow("Language:", self._language_widget)

        self._voice_mod_name_widget = QTW.QLineEdit()
        form_layout.addRow("Voice mod name:", self._voice_mod_name_widget)

        self._voice_mod_id_widget = QTW.QLineEdit()
        form_layout.addRow("Voice mod ID:", self._voice_mod_id_widget)

        if session is None:
            self._language_widget.setCurrentText("en")
            self._voice_mod_name_widget.setText("My Voice Mod")
            self._voice_mod_id_widget.setText("wcar")
        else:
            self._language_widget.setCurrentText(session["language"])
            self._voice_mod_name_widget.setText(session["voice_mod_name"])
            self._voice_mod_id_widget.setText(session["voice_mod_id"])
            for change in session["changes"]:
                self._changes_widget.add_row(change["commander"], change["name"],
                                             change["portrait"], change["voice_over"])

        main_layout.addLayout(form_layout)

        self._install_button = QTW.QPushButton()
        self._install_button.setText("Install")
        self._install_button.clicked.connect(self._install)
        main_layout.addWidget(self._install_button)

        self.setLayout(main_layout)

    def _install(self) -> None:
        self._install_button.setEnabled(False)
        changes = self._changes_widget.get_changes()
        language = self._language_widget.currentText()
        io = self._io
        io.install_names(changes.name_changes, language)
        io.install_portraits(changes.portrait_changes)
        io.install_voice_overs(changes.voice_changes,
                               self._voice_mod_name_widget.text(),
                               self._voice_mod_id_widget.text())
        self._install_button.setText("Success!")
        print("Success!")

    def _save_session(self) -> None:
        print("Saving session.")
        with open("session.json", "w") as session_file:
            session_file.write(JSON.dumps({
                "language": self._language_widget.currentText(),
                "voice_mod_name": self._voice_mod_name_widget.text(),
                "voice_mod_id": self._voice_mod_id_widget.text(),
                "changes": self._changes_widget.get_changes_as_json()
            }, indent=2))

    def closeEvent(self, event: QTG.QCloseEvent) -> None:
        self._save_session()
        super().closeEvent(event)


def main() -> None:
    app = QTW.QApplication(SYS.argv)
    with open("commanders.csv") as csv_file:
        commanders = {row[0]: RecipientCommander(row[1], PTH.Path(row[2]), row[3])
                      for row in CSV.reader(csv_file)}

    wows_dir = QTW.QFileDialog.getExistingDirectory(None, "Choose WoWs folder")
    if not wows_dir:
        raise RuntimeError("Invalid WoWs folder.")
    wows_dir = PTH.Path(wows_dir)
    output_dir = wows_dir/"res_mods"
    working_dir = PTH.Path("working")
    io = WowsIo(wows_dir, output_dir, working_dir)

    try:
        with open("session.json") as session_file:
            session = JSON.load(session_file)
    except FileNotFoundError:
        session = None

    with io:
        window = MainWidget(commanders, io.list_languages(),
                            working_dir/"gui"/"crew_commander"/"base",
                            io.list_voice_overs(), io, session)
        window.setWindowTitle(title)
        window.show()
        app.exec()


if __name__ == "__main__":
    main()
