from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QDateEdit, QMessageBox, QCheckBox
)
from PySide6.QtCore import QDate

class ZahlungEintragenWidget(QWidget):
    def __init__(self, kategorien=None, konten=None, on_save=None, on_update=None, edit_mode=False):
        super().__init__()
        if kategorien is None:
            kategorien = []
        if konten is None:
            konten = []
        self.on_save = on_save
        self.on_update = on_update
        self.edit_mode = edit_mode
        self.zahlung_id = None

        layout = QVBoxLayout()
        # Zeile 1: Betrag, Typ (Einnahme/Ausgabe)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Betrag:"))
        self.input_betrag = QLineEdit()
        self.input_betrag.setPlaceholderText("z.B. 50,00")
        row1.addWidget(self.input_betrag)


        layout.addLayout(row1)

        # Zeile 2: Datum, Kategorie
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Typ:"))
        self.combo_typ = QComboBox()
        self.combo_typ.addItems(["Einnahme", "Ausgabe"])
        row2.addWidget(self.combo_typ)

        row2.addWidget(QLabel("Kategorie:"))
        self.combo_kategorie = QComboBox()
        for k in kategorien:
            self.combo_kategorie.addItem(k["name"], userData=k["id"])
        row2.addWidget(self.combo_kategorie)
        layout.addLayout(row2)

        # Zeile 3: Konto-Auswahl
        row3 = QHBoxLayout()

        row3.addWidget(QLabel("Datum:"))
        self.input_datum = QDateEdit()
        self.input_datum.setDate(QDate.currentDate())
        self.input_datum.setCalendarPopup(True)
        row3.addWidget(self.input_datum)

        row3.addWidget(QLabel("Konto:"))
        self.combo_konto = QComboBox()
        for k in konten:
            self.combo_konto.addItem(k["name"], userData=k["id"])
        row3.addWidget(self.combo_konto)
        layout.addLayout(row3)

        # Zeile 4: Beschreibung
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Beschreibung:"))
        self.input_beschreibung = QLineEdit()
        self.input_beschreibung.setPlaceholderText("optional")
        row4.addWidget(self.input_beschreibung)
        layout.addLayout(row4)

        # Zeile 5: Wiederkehrend Checkbox
        row5 = QHBoxLayout()
        self.checkbox_wiederkehrend = QCheckBox("Wiederkehrende Zahlung")
        row5.addWidget(self.checkbox_wiederkehrend)
        layout.addLayout(row5)

        # Speichern-Button
        self.btn_speichern = QPushButton("Speichern")
        self.btn_speichern.clicked.connect(self.speichern)
        layout.addWidget(self.btn_speichern)

        self.setLayout(layout)

    def speichern(self):
        betrag = self.input_betrag.text().replace(",", ".")
        typ = self.combo_typ.currentText()
        datum = self.input_datum.date().toString("yyyy-MM-dd")
        kategorie_id = self.combo_kategorie.currentData()
        konto_id = self.combo_konto.currentData()
        beschreibung = self.input_beschreibung.text()
        wiederkehrend = self.checkbox_wiederkehrend.isChecked()

        try:
            betrag_float = float(betrag)
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte einen gültigen Betrag eingeben (z.B. 12.50).")
            return

        if kategorie_id is None:
            QMessageBox.warning(self, "Fehler", "Bitte eine Kategorie auswählen.")
            return
        if konto_id is None:
            QMessageBox.warning(self, "Fehler", "Bitte ein Konto auswählen.")
            return

        zahlungsdaten = {
            "betrag": betrag_float,
            "typ": typ,
            "datum": datum,
            "kategorie_id": kategorie_id,
            "konto_id": konto_id,
            "beschreibung": beschreibung,
            "wiederkehrend": wiederkehrend
        }

        if self.edit_mode and self.zahlung_id is not None and self.on_update:
            self.on_update(self.zahlung_id, zahlungsdaten)
        elif not self.edit_mode and self.on_save:
            self.on_save(zahlungsdaten)
        self.clear_fields()

    def set_edit_mode(self, mode, zahlung_id=None, daten=None):
        self.edit_mode = mode
        self.zahlung_id = zahlung_id
        if daten:
            self.input_betrag.setText(str(daten.get("betrag", "")))
            self.combo_typ.setCurrentText(daten.get("typ", "Einnahme"))
            datum_qdate = QDate.fromString(daten.get("datum", ""), "yyyy-MM-dd")
            if datum_qdate.isValid():
                self.input_datum.setDate(datum_qdate)
            if daten.get("kategorie_id") is not None:
                idx = self.combo_kategorie.findData(daten.get("kategorie_id"))
                if idx != -1:
                    self.combo_kategorie.setCurrentIndex(idx)
            if daten.get("konto_id") is not None:
                idx = self.combo_konto.findData(daten.get("konto_id"))
                if idx != -1:
                    self.combo_konto.setCurrentIndex(idx)
            self.input_beschreibung.setText(daten.get("beschreibung", ""))
            self.checkbox_wiederkehrend.setChecked(bool(daten.get("wiederkehrend", False)))
            self.btn_speichern.setText("Änderung speichern")
        else:
            self.clear_fields()
            self.btn_speichern.setText("Speichern")

    def clear_fields(self):
        self.input_betrag.clear()
        self.input_beschreibung.clear()
        self.checkbox_wiederkehrend.setChecked(False)
        self.combo_typ.setCurrentIndex(0)
        self.combo_kategorie.setCurrentIndex(0)
        self.combo_konto.setCurrentIndex(0)
        self.input_datum.setDate(QDate.currentDate())
        self.btn_speichern.setText("Speichern")
        self.edit_mode = False
        self.zahlung_id = None

    def update_kategorien(self, kategorien):
        self.combo_kategorie.clear()
        for k in kategorien:
            self.combo_kategorie.addItem(k["name"], userData=k["id"])

    def update_konten(self, konten):
        self.combo_konto.clear()
        for k in konten:
            self.combo_konto.addItem(k["name"], userData=k["id"])