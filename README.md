## Development

Use the nix direnv with either `nix develop` or `direnv allow` depending on your nix install

The frontend uses yarn
The python env will be built by the direnv

Setup postgres and sharkey for dev:
```
db-setup
```

Then to start the dev environment

```
# Postgres
dev-start

# Sharkey
sharkey migrateandstart

# API server/FastAPI
python api/main.py

# Frontend/Nuxt
cd frontend && yarn dev
```


# Deployment

## Garage (On nixos at least based on my config)
`garage status` Will let you get your node id
`garage layout assign -z garage -c 10G nodeid`
`garage layout apply --version 1`
`garage key create hajdentity`
`garage bucket create hajdentity`
`garage bucket allow hajdentity --read --write --owner --key hajdentity`

## Credit
Thanks to IsabelleDotJpeg for the [blahaj model](https://www.reddit.com/r/BLAHAJ/comments/rkul4y/bl%C3%A5haj_now_on_ps1/)! (used for the loading screen gif)
