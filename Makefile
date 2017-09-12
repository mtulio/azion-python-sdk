
############
## DEV TOOLS

.PHONY: bump
bump:
	@rm dist/*
	python setup.py sdist
	twine upload --skip-existing dist/*


.PHONY: tag
tag:
	@if [ "`git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'`" != "master" ]; then \
		echo "#>> ERR - Your not in a 'master' branch: `git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'`"; \
		exit 1; \
	fi
	git tag `sed "s/__version__ \= //g" azion/version.py |tr -d "'"` -m "Bump to `sed "s/__version__ \= //g" azion/version.py |tr -d "'"` by Makefile" && \
		git push --tags origin
