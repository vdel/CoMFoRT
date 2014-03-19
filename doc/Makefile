.PHONY: all doc show clean

all: doc

doc:
	mkdir -p api
	cd ../src && ln -s cgi-bin cgibin && epydoc --config ../doc/epydoc.conf && rm -rf cgibin
	pdflatex doc.tex

show: doc
	sensible-browser api/index.html

clean:
	rm -rf api
	rm -f *.aux *.log *.out *.toc
