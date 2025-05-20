.PHONY: test

db-reset-migrations:
	rm -rf instance && rm src/migrations/versions/* ;  uv run -- flask --app src db migrate -m "initial" -d src/migrations

db-reset:
	rm -rf instance && uv run -- flask --app src db upgrade -d src/migrations

db-clean: db-reset-migrations db-reset

db-seed:
	uv run -- flask --app src setup seed

db-history:
	uv run -- flask --app src db history -d src/migrations

db-upgrade:
	uv run -- flask --app src db upgrade -d src/migrations

start:
	uv run -- flask --app src run --debug -p 3000

test:
	source .venv/bin/activate; \
	python -m unittest discover; \
	deactivate

docker-up:
	mkdir ${HOME}/tmp/database \
	; mkdir ${HOME}/tmp/upload \
	; COMPOSE_BAKE=true docker compose up --build

docker-clean:
	docker compose down -v \
	  && rm -rf ${HOME}/tmp/database \
	  && rm -rf ${HOME}/tmp/upload
