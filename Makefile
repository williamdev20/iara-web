tailwind-watch:
	npm run tailwind:watch
django-runserver:
	python3.11 manage.py runserver
run:
	make -j 2 tailwind-watch django-runserver