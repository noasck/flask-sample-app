testpath := src

dev:
	docker compose up api --build

test:
	docker compose run --rm --build tests pytest ${testpath}

test_unit:
	docker compose run --rm --build tests pytest -m "not integrity" ${testpath}

down:
	docker compose down --remove-orphans --volumes

black:
	black src/**/**.py