# sand-track

Just a little thing to help us run task competitions at local flying sites.

# local dev

1. `echo "SECRET_KEY='something-super-secret'" > .env`
2. `uv sync`
3. `uv run -- flask --app src db upgrade -d src/migrations`
4. `uv run -- flask --app src run -p 3000`

# on fly.io

- create app
- create volume
- create secret `SECRET_KEY`

## seed the DB

```shell
fly ssh console -a sandtrack
.venv/bin/flask --app src db upgrade -d src/migrations
.venv/bin/flask --app src setup seed
```

## To modify the DB...

```shell
fly ssh sftp get '/data/db/sand-track.sqlite' -a sandtrack
sqlite3 ./sand-track.sqlite
<do updates>
fly ssh console
mv /data/db/sand-track.sqlite /data/db/sand-track.sqlite.bak
fly ssh sftp shell
put /Users/caseygerstle/src/sand-track/sand-track.sqlite /data/db/sand-track.sqlite
fly ssh console
chown nonroot:nonroot /data/db/sand-track.sqlite
fly machine restart
```
