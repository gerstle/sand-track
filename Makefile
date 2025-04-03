db-reset-migrations:
	rm -rf instance && rm src/migrations/versions/* ;  uv run -- flask --app src db migrate -m "initial" -d src/migrations

db-reset:
	rm -rf instance && uv run -- flask --app src db upgrade -d src/migrations

db-clean: db-reset-migrations db-reset

db-seed:
	uv run -- flask --app src setup seed

start:
	uv run -- flask --app src run --debug -p 3000