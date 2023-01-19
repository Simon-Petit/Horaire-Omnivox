from PySide6 import QtWidgets
import time as t

class OmnivoxScraper(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Horaire Omnivox")
        self.setup()

    def setup(self):

        self.grid = QtWidgets.QGridLayout(self)

        self.la_DA = QtWidgets.QLabel(self)
        self.la_DA.setText("Votre DA :")
        self.grid.addWidget(self.la_DA, 0, 0, 1 ,1)

        self.le_DA = QtWidgets.QLineEdit(self)
        self.le_DA.setPlaceholderText("ex: 2200000")
        self.grid.addWidget(self.le_DA, 0, 1, 1 ,2)

        self.la_MDP = QtWidgets.QLabel(self)
        self.la_MDP.setText("Mot de passe :")
        self.grid.addWidget(self.la_MDP, 1, 0, 1 ,1)

        self.le_MDP = QtWidgets.QLineEdit(self)
        self.le_MDP.setPlaceholderText("ex: motdepasse69")
        self.le_MDP.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.grid.addWidget(self.le_MDP, 1, 1, 1 ,2)

        self.la_URL = QtWidgets.QLabel(self)
        self.la_URL.setText("L'url de votre cégep* :")
        self.grid.addWidget(self.la_URL, 2, 0, 1 ,1)

        self.le_URL = QtWidgets.QLineEdit(self)
        self.le_URL.setPlaceholderText("ex: https://cegepsth.omnivox.ca/...")
        self.grid.addWidget(self.le_URL, 2, 1, 1 ,2)

        self.la_couleur = QtWidgets.QLabel(self)
        self.la_couleur.setText("Couleur des évènements :")
        self.grid.addWidget(self.la_couleur, 3, 0, 1 ,1)

        self.cb_couleur = QtWidgets.QComboBox(self)
        self.cb_couleur.addItems(["Gris graphite", "Rouge tomate", "Flamant rose", "Orange mandarine", "Jaune banane", "Vert sauge", "Vert basilic", "Bleu paon", "Bleu myrtille", "Bleu lavande", "Violet raisin", "Couleur St-Hyacinthe"])
        self.grid.addWidget(self.cb_couleur, 3, 1, 1, 2)

        self.btn_start = QtWidgets.QPushButton("Créer mon horaire**", self)
        self.btn_start.clicked.connect(self.start)
        self.grid.addWidget(self.btn_start, 4, 0, 1 ,3)

        self.la_note_URL = QtWidgets.QLabel(self)
        self.la_note_URL.setText("*Ouvrez Omnivox dans un browser et copier le lien en haut\n**Cela va prendre environ 1 minutes")
        self.grid.addWidget(self.la_note_URL, 5, 0, 1 ,2)

    def start(self):
        self.prg_dialog = QtWidgets.QProgressDialog("Création de l'horaire...", "Annuler", 0, 100, self)
        self.prg_dialog.exec_()
        da = self.le_DA.text()
        mdp = self.le_MDP.text()
        url = self.le_URL.text()
        couleur = self.cb_couleur.currentText()
        dic_info = {"DA": da, "MDP": mdp, "URL": url, "Couleur": couleur}
        # le dict info sert pour les para du scraper scraper

app = QtWidgets.QApplication([])
fenetre = OmnivoxScraper()
fenetre.show()
app.exec_()