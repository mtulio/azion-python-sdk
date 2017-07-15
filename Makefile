
.PHONY: bump
bump:
	@rm dist/*
	python setup.py sdist
	twine upload dist/*
