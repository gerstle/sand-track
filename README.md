# sand-track

Just a little thing to help us run task competitions at local flying sites.

# local dev

1. `echo "SECRET_KEY='something-super-secret'" > .env`
2. `uv sync`
3. `uv run -- flask --app src db upgrade -d src/migrations`
4. `uv run -- flask --app src run -p 3000`