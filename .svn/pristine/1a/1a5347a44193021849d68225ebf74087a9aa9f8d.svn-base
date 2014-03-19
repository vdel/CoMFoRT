inherit eutils

DESCRIPTION="A CMS designed for researchers and teatchers"
HOMEPAGE="http://graal.ens-lyon.fr/comfort"
SRC_URI="http://perso.ens-lyon.fr/antoine.frenoy/comfort-${PV}.tar.gz"
LICENSE="CeCILL-2"
SLOT="0"
KEYWORDS="~x86 ~amd64"
IUSE=""

RDEPEND="dev-python/lxml
	 dev-python/pysqlite"


src_compile() {
	emake all || die "Erreur lors du make"
}

src_install() {
	dodoc README doc/*
	insinto /var/www/comfort
	insopts -m0644
	diropts -m0755
	doins -r locale/
	insopts -m0755
	doins -r src/
	insinto /usr/share/pixmaps
	doins logo/comfort_icone.png
	touch running
	insopts -m0666
	insinto /var/www/comfort/src/server
	doins running
	insopts -m0644
	dosym /var/www/comfort/src/server/launch.py /usr/bin/comfort
	make_desktop_entry comfort CoMFoRT comfort_icone.png Network /var/www/comfort/src/server/
}

pkg_postinst() {
	einfo "CoMFoRT est installé dans /var/www/comfort"
	einfo "Un raccourci a été créé dans le menu Internet"
}
