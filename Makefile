dev:
	docker compose --profile development up --build

test:
	docker compose --profile testing up --build --abort-on-container-exit

down:
	docker compose down --remove-orphans --volumes
