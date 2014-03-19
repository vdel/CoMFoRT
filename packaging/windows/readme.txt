Le fichier CoMFoRT.nsi contient un script d'installation a priori fonctionnel.
Il est à compiler avec NSIS.
Le script assure a priori la détection de Python, lxml et Java de façon correcte.
Il a été testé sous XP SP1, XP SP2, Vista, Vista SP1.


ATTENTION : 
Certains fichiers trop lourds pour être envoyés sur le dépôt SVN sont manquants :
 - l'install de Python 2.5 (à mettre dans le dossier Python_files)
	http://www.python.org/ftp/python/2.5.2/python-2.5.2.msi
	http://www.python.org/ftp/python/2.5.2/python-2.5.2.amd64.msi (si flag AMD64)
	http://www.python.org/ftp/python/2.5.2/python-2.5.2.ia64.msi (si flag IA64)
 - l'install de lxml (à mettre dans lxml_files)
	http://pypi.python.org/packages/2.5/l/lxml/lxml-2.0.5.win32-py2.5.exe
 - les fichiers CoMFoRT à envoyer à l'utilisateur (à mettre dans CoMFoRT_files)

Pour la compilation de la version :
 - Win 32 -> pas de flag
 - AMD 64 -> flag AMD64
 - IA 64 -> flag IA64

Problème : lxml ne semble disponible qu'en version Win 32 (?).

Consulter le script pour les détails.


NB concernant la licence :
Contrairement à CeCiLL, la GPL v3 ne dispose pas de version française officielle.
J'ai donc laissé la version anglaise dans l'installeur même si le langage choisi est le français.