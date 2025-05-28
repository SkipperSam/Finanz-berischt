import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox, QListWidget, QListWidgetItem, QInputDialog, QMenu
)
from PySide6.QtCore import Qt, QPoint
from db import (
    init_db, get_kategorien, add_kategorie, update_kategorie, delete_kategorie,
    get_konten, add_konto, update_konto, delete_konto,
    add_zahlung, update_zahlung, delete_zahlung,
    get_zahlungen, get_gesamtvermoegen, get_zahlung_by_id
)
from zahlung_eintragen_widget import ZahlungEintragenWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finanzverwaltung")
        self.resize(1100, 700)

        init_db()

        self.kategorien = [dict(row) for row in get_kategorien()]
        self.konten = [dict(row) for row in get_konten()]

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.balance_label = QLabel()
        self.balance_label.setStyleSheet("font-size: 28px; font-weight: bold; margin: 16px;")
        main_layout.addWidget(self.balance_label, alignment=Qt.AlignCenter)

        nav_layout = QHBoxLayout()
        self.btn_zahlung = QPushButton("Zahlung eintragen")
        self.btn_uebersicht = QPushButton("Finanzübersicht")
        self.btn_statistik = QPushButton("Statistik")
        self.btn_vertraege = QPushButton("Verträge")
        self.btn_kategorien = QPushButton("Kategorien verwalten")
        self.btn_konten = QPushButton("Konten verwalten")

        nav_layout.addWidget(self.btn_zahlung)
        nav_layout.addWidget(self.btn_uebersicht)
        nav_layout.addWidget(self.btn_statistik)
        nav_layout.addWidget(self.btn_vertraege)
        nav_layout.addWidget(self.btn_kategorien)
        nav_layout.addWidget(self.btn_konten)
        main_layout.addLayout(nav_layout)

        self.stacked_widget = QStackedWidget()

        # Seite: Zahlung eintragen (auch für Bearbeiten)
        self.page_zahlung = ZahlungEintragenWidget(
            kategorien=self.kategorien,
            konten=self.konten,
            on_save=self.zahlung_speichern,
            on_update=self.zahlung_aktualisieren
        )

        # Seite: Finanzübersicht (Liste mit Kontextmenü)
        self.page_uebersicht = QWidget()
        overview_layout = QVBoxLayout()
        self.list_uebersicht = QListWidget()
        self.list_uebersicht.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_uebersicht.customContextMenuRequested.connect(self.zahlung_context_menu)
        overview_layout.addWidget(self.list_uebersicht)
        self.page_uebersicht.setLayout(overview_layout)

        # Seite: Kategorien verwalten
        self.page_kategorien = QWidget()
        kategorien_layout = QVBoxLayout()
        self.list_kategorien = QListWidget()
        self.list_kategorien.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_kategorien.customContextMenuRequested.connect(self.kategorie_context_menu)
        self.btn_kategorie_hinzufuegen = QPushButton("Kategorie hinzufügen")
        self.btn_kategorie_hinzufuegen.clicked.connect(self.kategorie_hinzufuegen)
        kategorien_layout.addWidget(self.list_kategorien)
        kategorien_layout.addWidget(self.btn_kategorie_hinzufuegen)
        self.page_kategorien.setLayout(kategorien_layout)

        # Seite: Konten verwalten
        self.page_konten = QWidget()
        konten_layout = QVBoxLayout()
        self.list_konten = QListWidget()
        self.list_konten.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_konten.customContextMenuRequested.connect(self.konto_context_menu)
        self.btn_konto_hinzufuegen = QPushButton("Konto hinzufügen")
        self.btn_konto_hinzufuegen.clicked.connect(self.konto_hinzufuegen)
        konten_layout.addWidget(self.list_konten)
        konten_layout.addWidget(self.btn_konto_hinzufuegen)
        self.page_konten.setLayout(konten_layout)

        self.page_statistik = QLabel("Statistik – Diagramme und Auswertungen (später)")
        self.page_vertraege = QLabel("Verträge – Wiederkehrende Zahlungen (später)")

        self.stacked_widget.addWidget(self.page_zahlung)
        self.stacked_widget.addWidget(self.page_uebersicht)
        self.stacked_widget.addWidget(self.page_statistik)
        self.stacked_widget.addWidget(self.page_vertraege)
        self.stacked_widget.addWidget(self.page_kategorien)
        self.stacked_widget.addWidget(self.page_konten)
        main_layout.addWidget(self.stacked_widget)

        self.btn_zahlung.clicked.connect(self.show_zahlung_eintragen)
        self.btn_uebersicht.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_uebersicht))
        self.btn_statistik.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_statistik))
        self.btn_vertraege.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_vertraege))
        self.btn_kategorien.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_kategorien))
        self.btn_konten.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_konten))

        self.stacked_widget.setCurrentWidget(self.page_uebersicht)
        self.update_balance()
        self.update_uebersicht()
        self.update_kategorien()
        self.update_konten()

    # --- Zahlungen ---
    def show_zahlung_eintragen(self):
        self.page_zahlung.set_edit_mode(False)
        self.stacked_widget.setCurrentWidget(self.page_zahlung)

    def zahlung_speichern(self, daten):
        add_zahlung(
            daten["betrag"], daten["typ"], daten["datum"],
            daten["kategorie_id"], daten["konto_id"], daten["beschreibung"], daten["wiederkehrend"]
        )
        QMessageBox.information(self, "Erfolg", "Zahlung gespeichert!")
        self.update_uebersicht()
        self.update_balance()
        self.stacked_widget.setCurrentWidget(self.page_uebersicht)

    def zahlung_aktualisieren(self, zahlung_id, daten):
        update_zahlung(
            zahlung_id,
            daten["betrag"], daten["typ"], daten["datum"],
            daten["kategorie_id"], daten["konto_id"], daten["beschreibung"], daten["wiederkehrend"]
        )
        QMessageBox.information(self, "Erfolg", "Zahlung geändert!")
        self.update_uebersicht()
        self.update_balance()
        self.page_zahlung.set_edit_mode(False)
        self.stacked_widget.setCurrentWidget(self.page_uebersicht)

    def zahlung_context_menu(self, pos: QPoint):
        item = self.list_uebersicht.itemAt(pos)
        if item is None:
            return
        menu = QMenu()
        edit_action = menu.addAction("Bearbeiten")
        delete_action = menu.addAction("Löschen")
        action = menu.exec(self.list_uebersicht.viewport().mapToGlobal(pos))
        zahlung_id = item.data(Qt.UserRole)
        if action == edit_action:
            self.zahlung_bearbeiten(zahlung_id)
        elif action == delete_action:
            self.zahlung_loeschen(zahlung_id)

    def zahlung_bearbeiten(self, zahlung_id):
        eintrag = get_zahlung_by_id(zahlung_id)
        if eintrag:
            daten = dict(eintrag)
            self.page_zahlung.set_edit_mode(True, zahlung_id=zahlung_id, daten=daten)
            self.stacked_widget.setCurrentWidget(self.page_zahlung)

    def zahlung_loeschen(self, zahlung_id):
        confirm = QMessageBox.question(
            self, "Zahlung löschen",
            "Soll diese Zahlung wirklich gelöscht werden?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            delete_zahlung(zahlung_id)
            self.update_uebersicht()
            self.update_balance()
            QMessageBox.information(self, "Erfolg", "Zahlung gelöscht!")

    def update_uebersicht(self):
        self.list_uebersicht.clear()
        for eintrag in get_zahlungen():
            typ = "➕" if eintrag['typ'] == "Einnahme" else "➖"
            wiederk = "🔁" if eintrag["wiederkehrend"] else ""
            betrag = f"{eintrag['betrag']:.2f} €"
            konto = eintrag['konto_name'] if eintrag['konto_name'] else "Kein Konto"
            kategorie = eintrag['kategorie_name'] if eintrag['kategorie_name'] else "Keine Kategorie"
            text = f"{typ} {eintrag['datum']} | {betrag} | Konto: {konto} | Kategorie: {kategorie} | {eintrag['beschreibung']} {wiederk}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, eintrag["id"])
            self.list_uebersicht.addItem(item)

    def update_balance(self):
        saldo = get_gesamtvermoegen()
        self.balance_label.setText(f"Gesamtvermögen: {saldo:.2f} €")

    # --- Kategorien ---
    def update_kategorien(self):
        self.kategorien = [dict(row) for row in get_kategorien()]
        self.list_kategorien.clear()
        for k in self.kategorien:
            item = QListWidgetItem(f"{k['name']}")
            item.setData(Qt.UserRole, k["id"])
            self.list_kategorien.addItem(item)
        self.page_zahlung.update_kategorien(self.kategorien)

    def kategorie_hinzufuegen(self):
        name, ok = QInputDialog.getText(self, "Kategorie hinzufügen", "Name der neuen Kategorie:")
        if ok and name.strip():
            add_kategorie(name.strip())
            self.update_kategorien()
            QMessageBox.information(self, "Erfolg", "Kategorie hinzugefügt!")

    def kategorie_context_menu(self, pos: QPoint):
        item = self.list_kategorien.itemAt(pos)
        if item is None:
            return
        menu = QMenu()
        edit_action = menu.addAction("Bearbeiten")
        delete_action = menu.addAction("Löschen")
        action = menu.exec(self.list_kategorien.viewport().mapToGlobal(pos))
        kategorie_id = item.data(Qt.UserRole)
        kategorie_name = item.text()

        if action == edit_action:
            self.kategorie_bearbeiten(kategorie_id, kategorie_name)
        elif action == delete_action:
            self.kategorie_loeschen(kategorie_id, kategorie_name)

    def kategorie_bearbeiten(self, kategorie_id, alte_name):
        new_name, ok = QInputDialog.getText(self, "Kategorie bearbeiten", "Neuer Name:", text=alte_name)
        if ok and new_name.strip() and new_name.strip() != alte_name:
            update_kategorie(kategorie_id, new_name.strip())
            self.update_kategorien()
            QMessageBox.information(self, "Erfolg", "Kategorie geändert!")

    def kategorie_loeschen(self, kategorie_id, kategorie_name):
        confirm = QMessageBox.question(
            self, "Kategorie löschen",
            f"Soll die Kategorie '{kategorie_name}' wirklich gelöscht werden?\n"
            "Zahlungen mit dieser Kategorie bleiben erhalten, aber ohne Kategorie-Zuordnung.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            delete_kategorie(kategorie_id)
            self.update_kategorien()
            QMessageBox.information(self, "Erfolg", "Kategorie gelöscht!")

    # --- Konten ---
    def update_konten(self):
        self.konten = [dict(row) for row in get_konten()]
        self.list_konten.clear()
        for k in self.konten:
            item = QListWidgetItem(f"{k['name']}")
            item.setData(Qt.UserRole, k["id"])
            self.list_konten.addItem(item)
        self.page_zahlung.update_konten(self.konten)

    def konto_hinzufuegen(self):
        name, ok = QInputDialog.getText(self, "Konto hinzufügen", "Name des neuen Kontos:")
        if ok and name.strip():
            add_konto(name.strip())
            self.update_konten()
            QMessageBox.information(self, "Erfolg", "Konto hinzugefügt!")

    def konto_context_menu(self, pos: QPoint):
        item = self.list_konten.itemAt(pos)
        if item is None:
            return
        menu = QMenu()
        edit_action = menu.addAction("Bearbeiten")
        delete_action = menu.addAction("Löschen")
        action = menu.exec(self.list_konten.viewport().mapToGlobal(pos))
        konto_id = item.data(Qt.UserRole)
        konto_name = item.text()

        if action == edit_action:
            self.konto_bearbeiten(konto_id, konto_name)
        elif action == delete_action:
            self.konto_loeschen(konto_id, konto_name)

    def konto_bearbeiten(self, konto_id, alte_name):
        new_name, ok = QInputDialog.getText(self, "Konto bearbeiten", "Neuer Name:", text=alte_name)
        if ok and new_name.strip() and new_name.strip() != alte_name:
            update_konto(konto_id, new_name.strip())
            self.update_konten()
            QMessageBox.information(self, "Erfolg", "Konto geändert!")

    def konto_loeschen(self, konto_id, konto_name):
        confirm = QMessageBox.question(
            self, "Konto löschen",
            f"Soll das Konto '{konto_name}' wirklich gelöscht werden?\n"
            "Zahlungen mit diesem Konto bleiben erhalten, aber ohne Konto-Zuordnung.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            delete_konto(konto_id)
            self.update_konten()
            QMessageBox.information(self, "Erfolg", "Konto gelöscht!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())