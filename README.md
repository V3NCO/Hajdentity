## Development

Use the nix direnv with either `nix develop` or `direnv allow` depending on your nix install

The frontend uses yarn
The python env will be built by the direnv

Setup postgres and sharkey for dev:
```
db-setup
db-start

redis-start
sharkey-setup

db-stop
```

Then to start the dev environment

```
# Postgres
db-start

# Redis
redis-start

# Sharkey
sharkey-start

# API server/FastAPI
python api/main.py

# Frontend/Nuxt
cd frontend && yarn dev
```
