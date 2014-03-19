#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# CoMFoRT: a COntent Management system FOr Researchers and Teachers!
# 
# Copyright (C) 2008 Projet2-L3IF ENS Lyon.
# 
# Contributors:
#    * Jean-Alexandre Angles d'Auriac
#    * Gabriel Beaulieu
#    * Valentin Blot
#    * Pierre Boutillier
#    * Nicolas Brunie
#    * Aloïs Brunel
#    * Vincent Delaitre
#    * Antoine Frénoy
#    * Mathias Gaunard
#    * Guilhem Jaber
#    * Timo Jolivet
#    * Jonas Lefèvre
#    * Bastien Le Gloannec
#    * Anne-Laure Mouly
#    * Kevin Perrot
#    * Jonathan Protzenko
#    * Gabriel Renault
#    * Philippe Robert
#    * Pierre Roux
#    * Abdallah Saffidine
#    * David Salinas
#    * Félix Sipma
#    * Alexandra Sourisseau
#    * Samuel Vaiter
#    * Guillaume Vors 
#
# Contact us with : comfort@listes.ens-lyon.fr
#
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>."
#

import os, os.path
try:
  import hashlib
except ImportError:
  import md5 as hashlib
import urllib

##localization
gettext_domain = 'comfort'
gettext_localedir = '../locale/'

mode = ""    #local or dynamic
generating = False
build_url = None

def build_url_standard(args):
  args = args.copy()
  s = "handler.py?page="+args["page"]
  del args["page"]
  k = args.keys()
  k.sort()
  for key in k:
    s += "&amp;"+key+"="+args[key]
  return s

def build_url_for_generation(args2):
  args = args2.copy()
  try:
    s = args["page"][:args["page"].rindex(".")]
  except:
    s = args["page"]
  del args["page"]
  try:
    if args["pdf"] == "1":
      ext=".pdf"
      del args["pdf"]
    else:
      ext=".html"
  except:
    ext=".html"
  k = args.keys()
  if len(k) > 0:
    k.sort()
    m = hashlib.md5()
    for key in k:
      m.update(key+args[key])
    return s+m.hexdigest()[:10]+ext
  else:
    return s+ext

config_path = os.path.join(os.path.expanduser("~"), ".comfort")
database_path = os.path.join(config_path, "database")

##Fonction that returns url:  
#Fonction renvoyant l'url:
#### Styles ####
def get_style_url(page_style=None):
  import conf_general
  if page_style != None:
    style = page_style
  else:
    style = conf_general.style
  if generating:
    return "styles/"+style+"/style.css"
  else:
    return "../styles/"+style+"/style.css"
    
def get_favicon_url():
  if generating:
    return "styles/favicon.png"
  else:
    return "../styles/favicon.png"

def get_pictures_url(pict):
  if generating:
    return "perso/pictures/"+urllib.quote(pict)
  else:
    return pictures_url+urllib.quote(pict)

def get_pages_url(page):
  if generating:
    return "perso/pages/"+urllib.quote(page)
  else:
    return pages_url+urllib.quote(page)
    
def get_docs_url(docs):
  if generating:
    return "perso/docs/"+urllib.quote(docs)
  else:
    return docs_url+urllib.quote(docs)

def get_latex_url(page,img):
  if generating:
    return "latex/"+urllib.quote(page)+"/"+img
  else:
    return latex_url+urllib.quote(page)+"/"+img
    
##Modules
#Modules
module_wiki_name = "Wiki"
module_menu_name = "Menu"
module_credits_name = "Credits"
default_active_modules = ["Wiki","Menu"]
default_latex_dpi="200"

##Pages
#Pages
overview_path="overview.txt"
wikisyntax_page_name = "WikiSyntax"
wikisyntax_page_wiki = u"""
Voici la syntaxe de base vous permettant de rédiger des pages dans le panneau
d'administration.

== Syntaxe générale ==

=== Paragraphes ===

Un paragraphe occupe plusieurs lignes, on change de paragraphe en sautant une
ligne. Exemple :
<pre>
Ceci est un paragraphe.

Ceci en est un autre.
</pre>

=== Les titres ===

Il existe différents niveaux de titre.

* <nowiki>= Titre niveau 1 =</nowiki>
* <nowiki>== Titre niveau 2 ==</nowiki>
* <nowiki>=== Titre niveau 3 ===</nowiki>
* <nowiki>==== Titre niveau 4 ====</nowiki>
* <nowiki>===== Titre niveau 5 =====</nowiki>
* <nowiki>====== Titre niveau 6 ======</nowiki>

== Faire référence à du contenu ==

=== Les liens ===

* Pour un lien vers une page du site, utilisez <nowiki>[[NomDeLaPage]]</nowiki>,
par exemple <nowiki>[[Accueil]]</nowiki>.
* Pour les liens externes, employez la syntaxe suivante :
<nowiki>[http://graal.ens-lyon.fr/comfort]</nowiki>.

Les deux types de liens sont disponibles sous une forme étendue qui permet de
choisir le titre du lien : ainsi, <nowiki>[http://graal.ens-lyon.fr/comfort|Site
officiel]</nowiki> donne [http://graal.ens-lyon.fr/comfort|Site officiel].

=== Les images ===

Utilisez la syntaxe suivante :
<pre>
<nowiki>[[Image:url|thumb|position|taille|légende]]</nowiki>
</pre>

Les paramètres sont les suivants :
* url : l'adresse de l'image ;
* thumb : équivalent à 180px de taille ;
* position : left, center, ou right, pour positionner l'image ;
* légende : texte alternatif.

La taille peut prendre les formats suivants :
* 300px ou 300 : l'image fera 300 pixels suivant sa plus grande dimension ;
* 640x480px : l'image fera 640 pixels de large et 480 de haut.

=== Liens vers le contenu personnel stocké dans "perso" ===

* <nowiki>[[Page:url|nom du lien]]</nowiki> pour les pages HTML ou autres stockées
dans "perso/pages". L'url est le chemin relatif à partir de perso/pages, ainsi
si votre fichier est "perso/pages/mavie.html" url vaudra "mavie.html"
* <nowiki>[[Picture:url|nom du lien]]</nowiki> pour les images stockées dans
"perso/pictures"

== Mise en forme ==

=== Exposants et indices ===

<nowiki><sup>Votre texte en exposant</sup></nowiki> et <nowiki><sub>Votre texte 
en indice</sub></nowiki>.

=== Taille du texte ===

<nowiki><big>Donne du texte plus gros</big> ou <small>plus 
petit</small></nowiki>.

=== Tableaux ===

Comme un exemple est toujours plus parlant, le code suivant :
<pre>
<nowiki>{|</nowiki>
<nowiki>|+titre du tableau</nowiki>
<nowiki>|-</nowiki>
<nowiki>|première cellule de la ligne</nowiki>
<nowiki>|une autre cellule sur la même ligne</nowiki>
<nowiki>|-</nowiki>
<nowiki>|cellule1</nowiki>
<nowiki>|cellule2</nowiki>
<nowiki>|}</nowiki>
</pre>

donne le résulat suivant :
{|
|+titre du tableau
|-
|première cellule de la ligne
|une autre cellule sur la même ligne
|-
|cellule1
|cellule2
|}

La syntaxe permettant d'ajouter une cellule admet une version étendue :
<pre><nowiki>| options | texte</nowiki></pre> où les options sont les suivantes.

* align=XXX où XXX vaut middle, left, right : pour centrer le texte dans la
cellule
* valign=XXX où XXX vaut top, middle, bottom : pour centrer verticalement le
texte
* colspan = X : la case s'étend sur X colonnes
* rowspan = X : la case s'étend sur X lignes

=== Listes ===

<pre>
<nowiki>* liste</nowiki>
<nowiki>* non</nowiki>
<nowiki>* numérotée</nowiki>
</pre>

Ou bien :
<pre>
<nowiki># liste</nowiki>
<nowiki># numérotée</nowiki>
</pre>

On obtient :
* liste
* non
* numérotée

et :
# liste
# numérotée

=== Texte préformaté ===

Il suffit d'ajouter un espace en début de ligne.

== Balises diverses ==

Diverses balises fonctionnement comment en html :

* <nowiki><math size="XXX" packages="YYY">x^2</math></nowiki> permet d'insérer du code LaTeX dans 
votre document avec XXX la taille en dpi et YYY la liste des paquets séparés par 
des espaces. Taille par défaut : 200.
* <nowiki><nowiki>syntaxe wiki désactivée entre ces balises</nowiki></nowiki>
* <nowiki><h2> jusqu'à <h6></nowiki> fonctionnement comme <nowiki>== jusqu'à 
======</nowiki>
* <nowiki><sup> et <sub> pour les exposants</nowiki>
* <nowiki><ref>note de bas de page</ref></nowiki>
* <nowiki><pre>texte préformaté</pre></nowiki>
* <nowiki><i></i> <b></b> <u></u> <s></s></nowiki> donnent respectivement du texte en italique, 
gras, souligné, barré.
* <nowiki><br /></nowiki> va à la ligne

"""
default_page_name = "Accueil"
default_page_wiki = u"""
Bonjour et bienvenue sur CoMFoRT, un système de gestion de contenu vous
permettant de créer de manière simple et efficace votre site personnel.

Bien que ce logiciel soit principalement destiné aux sites web de chercheurs,
nous espérons qu'il vous donnera entièrement satisfaction, quel que soit votre
domaine d'activité.

== Fonctionnement du logiciel ==

Avec CoMFoRT, vous commencez par travailler sur une ''version locale'' : c'est
le site que vous visualisez actuellement. C'est cette version que vous
modifierez, à laquelle vous ajouterez du contenu.  Vous pouvez à tout moment
avoir un aperçu du site en revenant sur cette page.  Lorsque le site vous semble
satisfaisant, nous en créerons une copie que nous enverrons sur votre espace de
stockage de pages web : c'est la ''version statique'', une version figée, sorte
d'instantané de la version locale.

Les points qui vont suivre vous indiqueront les endroits clé de CoMFoRT
permettant une prise en main la plus rapide possible.

== Prise en main ==

=== Gestion des pages ===

Il faut commencer par définir les pages que vous voulez ajouter à votre site.
Une page existe déjà : c'est cette page d'accueil. Vous pouvez en ajouter
d'autres en cliquant sur le lien ci-dessous "Panneau d'administration", puis en
cliquant sur '''Gestion des pages'''.

Chaque page que vous créez est définie par son identifiant, ainsi que son
titre. L'identifiant servira à générer le nom du fichier. Le titre permet de
vous y retrouver dans l'administration.

==== Les modules ====

Chaque page contient ce qu'on appelle des modules. Chaque module permet de
générer du contenu répondant à un besoin particulier. Par exemple, le module
"News" permet de gérer des nouvelles. Si vous l'activez sur la page MaPage, les
news seront affichées sur la page MaPage. Il en va de même pour les autres
modules.

Chaque module possède sa propre page de configuration, accessible depuis le
panneau d'administration. Ainsi, pour ajouter une news, il vous suffit de
cliquer sur le lien "Panneau d'administration" en bas de page, puis "Configurer
le module news".

==== Le module Wiki ====

Ce module est plus particulier : il vous permet de mettre le texte de votre
choix dans la page. La syntaxe wiki est la même que celle de Wikipedia. Un
bouton spécial "Éditer wiki" vous permet de modifier le contenu de chaque page.
C'est ainsi que nous avons saisi le texte que vous êtes en train de lire. Vous
pouvez le modifier en utilisant le raccourci en bas de page "Modifier cette
page".

Vous pouvez retrouver le détail de la syntaxe Wiki utilisée par ce logiciel sur
la page [[WikiSyntax]].

=== Le menu ===

Un module est plus important que tous les autres : c'est le menu. Allez dans le
panneau de configuration, puis cliquez sur "Configurer le module Menu". Vous
pouvez ajouter des boutons au choix dans le menu : la cible de chaque bouton est
une page du site, et le titre de chaque bouton est personnalisable. Une bonne
idée est d'ajouter un bouton "Accueil" pointant vers la page d'accueil (celle-là
même que vous lisez).

=== La configuration générale ===

Il vous sera ensuite utile d'aller configurer les paramètres généraux de votre
site. Vous pourrez par exemple changer votre style : CoMFoRT est livré avec de
nombreux styles différents. Par exemple, le style "lite" fournit un effet
intéressant pour les News. Vous pouvez essayer la combinaison suivante : page
d'accueil avec les modules Menu, News, Wiki (dans cet ordre) et le style lite.

==== Les paramètres FTP ====

Lorsque nous publierons la version statique de votre site, nous aurons besoin
des informations concernant votre espace de stockage. Exemple typique de
paramètres :
* hôte : perso.ens-lyon.fr
* nom d'utilisateur : votrelogin
* mot de passe : votremotdepasse
* racine : comfort
en supposant que vous avez créé un dossier "comfort" dans votre espace
personnel.

=== La publication du site ===

Une fois que votre site vous convient, il est temps de l'envoyer vers votre
espace personnel : c'est le rôle du bouton "synchroniser" dans l'interface
d'administration.

=== Terminé ? ===

N'oubliez pas d'éteindre le serveur local via le bouton arrêter de l'interface
d'administration.

== Utiliser votre contenu dans CoMFoRT (images, pages...) ==

Vous pouvez ajouter du contenu créé par vous dans votre site : des images, des
pages que vous ne voulez pas que CoMFoRT génère, des documents PDF... Il suffit
de les mettre dans l'un des trois dossiers suivants :

* ~/.comfort/perso/pages pour les pages HTML (ou PHP, peu importe) ;
* ~/.comfort/perso/pictures pour les images ;
* ~/.comfort/perso/docs pour les documents PDF par exemple.

Ces fichiers seront automatiquement envoyés sur le serveur avec votre site
lorsque vous demanderez une synchronisation. Pour faire référence à l'un de ces
fichiers depuis le Wiki, utilisez : <nowiki>[Picture:nomdevotreimage.ext], [Page:votrepage.php], [Doc:votrefichier.pdf]</nowiki>

Pour référencer une image externe, utilisez :
<nowiki>[[Image:http://www.votresite.com/image.jpg]]</nowiki>

== Étendre CoMFoRT ==

CoMFoRT a été dès le départ prévu pour être facilement extensible. Nous serions
heureux d'accueillir tout type de contributions. Voici par où commencer. 

=== Une feuille de style ? Rien de plus simple ! ===

Pour ajouter une feuille de style, il vous suffit de créer un dossier portant
son nom dans "styles", à la racine de votre installation, et un fichier
style.css. Les styles sont largement documentés, comme "blue", et vous trouverez
tous les sélecteurs dont vous pouvez avoir besoin dans "blue" ou "lite".

=== Un module ? Easy too ! ===

Vous pouvez créer un module correspondant à vos besoins en créant un fichier
themodule_NomDeVotreModule.py dans le dossier "modules". Il devra contenir une
classe TheModule héritant de ComfortModule, ainsi que des interfaces
correspondant à ce que fait le module : IModuleAdminPage s'il a une page dans le
panneau d'administration, IModuleContentProvider s'il génère du contenu,
IModuleDB s'il utilise la base de données. Vous devez implémenter les fonctions
définies par l'interface si vous héritez de celle-ci : voir module_interfaces.py

La documentation générée automatiquement est également un excellent point de
départ : elle contient en effet des diagrammes d'héritage permettant de voir
facilement comment penser un module. Elle est livrée dans l'archive que vous
avez téléchargée.

Le module "News" par exemple vous fournira un bon exemple de gestion de
formulaire d'administration et de génération de contenu, le tout grâce à la base
de données.

=== Tenez-nous au courant ! ===

Postez vos modifications sur [http://graal.ens-lyon.fr/comfort/] !

"""
pages_database_prefix = "pages"
##So that menu filters only relevant pages
#Pour que le menu filtre seulement les pages intéressantes
pages_perso_extensions = ["html","xhtml","xml","php","py"]

##Internationalization
#Internationalisation
possible_languages=[("fra","français"),("eng","english")]

##Path to FOP
#Chemin pour FOP
if os.name == 'posix':
  fop_path = "templates/fop/fop"
elif os.name == 'mac':
  fop_path = "templates/fop/fop"
elif os.name == 'nt':
  fop_path = "templates\\fop\\fop.bat"

nt_python_path = 'c:\\Python25\\'
nt_has_java = True

def dblatex_path():
  if os.name == 'nt':
    return nt_python_path+"Scripts\\dblatex"
  else:
    dirs = os.getenv("PATH").split(":")
    for d in dirs:
      p = os.path.join(d, "dblatex")
      if os.path.isfile(p):
        return p
    return ""

def scp_path():
  if os.name == 'nt':
    return ""
  else:
    dirs = os.getenv("PATH").split(":")
    for d in dirs:
      p = os.path.join(d, "scp")
      if os.path.isfile(p):
        return p
    return ""

def get_user_server_port():
  if os.name == 'nt':
    # sous windows, y a des uid ou pas ? quelqu'un sait ?
    # à défaut, on fait un expèce de hash md5 du home (oui, c'est nul)
    try:
      import hashlib
    except ImportError:
      import md5 as hashlib
    uid = ord(hashlib.md5(os.path.expanduser("~")).digest()[7]) % 79 + 1  # que quelqu'un fasse plus crade s'il peut ! ! !
  else:
    uid = os.getuid()-999
  return 8000+uid


if os.getenv("SERVER_SOFTWARE") and os.getenv("SERVER_SOFTWARE").startswith("Apache"):
  config_url = "http://localhost/.comfort/"
else:
  config_url = 'http://localhost:'+str(get_user_server_port())+'/'

##Paths
#Chemins
l2p_path=os.path.join("l2p","l2p")
latex_path=os.path.join(config_path,"latex")
latex_url=config_url+"latex/"
perso_path = os.path.join(config_path,"perso")
perso_url=config_url+"perso/"
pages_path=os.path.join(perso_path,"pages")
pages_url=perso_url+"pages/"
docs_path = os.path.join(perso_path, "docs")
docs_url=perso_url+"docs/"
pictures_path = os.path.join(perso_path, "pictures")
pictures_url=perso_url+"pictures/"

##Static pages generation
#Generation statique des pages
generate_path=os.path.join(config_path, "generate")
generate_url=config_url+"generate"
##Pay attention to synchronize.py:     os.chdir('..')
##and to template_manager --> generate_pdf
#attention à synchronize.py:     os.chdir('..')
#et à template_manager --> generate_pdf

