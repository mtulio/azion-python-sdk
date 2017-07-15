
############
## DEV TOOLS

.PHONY: bump
bump:
	@rm dist/*
	python setup.py sdist
	twine upload dist/*

.PHONY: var
var:
		@echo VERSION

.PHONY: tag
tag:
	@if [ "$(git branch -q |grep ^* |awk '{print$2}')" != 'master' ]; then \
		echo "#>> ERR - Your not in a 'master' branch"; \
		exit 1; \
	fi
	git tag `sed "s/__version__ \= //g" azion/version.py |tr -d "'"` -m "Bump. by Makefile"
