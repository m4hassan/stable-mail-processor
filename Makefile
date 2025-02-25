# with command `.SILENT` only echo commands will be printed everything else will be omitted
.SILENT:

clean:
	find . -type f -name '*.py[co]' -o -type f -name ".coverage" -o -type d -name __pycache__ -o -type d -name .pytest_cache  | xargs rm -rf
	echo "Process Completed"
run:
	cd src && python main.py
