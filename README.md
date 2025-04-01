# run

```shell
SECRET_KEY=A3BA7347-DD8D-466C-AE4A-192E340FADFA \
DB_URI='sqlite:///sand-track.sqlite' \
uv run -- flask --app src --debug run -p 3000
```

# DB

## init migrations

```shell
SECRET_KEY=A3BA7347-DD8D-466C-AE4A-192E340FADFA \
DB_URI='sqlite:///sand-track.sqlite' \
uv run -- flask --app src db init -d src/migrations
```

## create migration

```shell
SECRET_KEY=A3BA7347-DD8D-466C-AE4A-192E340FADFA \
DB_URI='sqlite:///sand-track.sqlite' \
uv run -- flask --app src db migrate -m "init" -d src/migrations
```

## upgrade

```shell
SECRET_KEY=A3BA7347-DD8D-466C-AE4A-192E340FADFA \
DB_URI='sqlite:///sand-track.sqlite' \
uv run -- flask --app src db upgrade -d src/migrations
```