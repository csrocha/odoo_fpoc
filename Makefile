.PHONY : addons

addons: fp.db
	xmi2oerp -r --dbfile $< --logfile $?.log --loglevel=2 --target $@

fp.db: design/fp.uml
	xmi2oerp --infile $< --dbfile $@

