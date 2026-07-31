# Hajdentity

> [!WARNING]
> This project is incredibly messy, unstable, and unfinished:
> this is not a result of low effort or vibecoding, 
> this is a result of me being horrible at coding and managing my time
> Some stuff is as polished as i could make it, some stuff is incredibly rushed.

## Description

Hajdentity is a platform to make a profile for your beloved plushies (BLÅHAJ is love, BLÅHAJ is life), you get a profile page; giving a bunch of information such as:
- Name
- Gender/Pronouns
- Size
- When the plush was adopted and last time it got a wash
- Fluffiness and squishiness ratings
- Friends
- Description
- Location

As well as a federated social media page using Sharkey!
Your plushie will then have posts, and friends on there!

## NFC?

Yes! This project uses NTAG424DNA NFC tags that you can put anywhere on your hajs; 
See it like putting a microchip on animals, except for your haj!
The NTAG424DNA is a secure tag that lets us have a different URL every time its tapped;
Basically it has a tag UID along with a counter, and then with the keys we provide it encrypts the whole thing and cryptographically signs it!
We then check that against our database to make sure the tap actually happened and isn't just someone reusing an old URL
And once that's done we can do our authenticated action! In this case I give the user a token that lasts ~10 minutes where they can interact with the haj in the following ways:
- Making a new post
- Seeing the haj's profile
- Creating or using a friend code to- well- add a friend.

## Features

- Creating a plushie (/dashboard/plushies/new)
- Editing a plushie (/dashboard/plushies/{id})
- Adding an NFC tag! (/dashboard/plushies/nfc?haj={id})
- Profile page (/plush/{id})
- Adding friends (/plush/{id}/friend)
- Making memories (/plush/{id}/post)
- Everything being synced with sharkey, and therefore being federated!

## Development

Use the nix direnv with either `nix develop` or `direnv allow` depending on your nix install

The frontend uses npm
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
cd frontend && NUXT_API_PROXY_TARGET="http://127.0.0.1:8000" NUXT_PUBLIC_API_URL="http://127.0.0.1:8000" npm run dev
```


## Deployment

### Garage (On nixos at least based on my config)
- `garage status` Will let you get your node id
- `garage layout assign -z garage -c 10G nodeid`
- `garage layout apply --version 1`
- `garage key create hajdentity`
- `garage bucket create hajdentity`
- `garage bucket allow hajdentity --read --write --owner --key hajdentity`

## Credit
Thanks to IsabelleDotJpeg for the [blahaj model](https://www.reddit.com/r/BLAHAJ/comments/rkul4y/bl%C3%A5haj_now_on_ps1/)! (used for the loading screen gif)

IKEA for uh making the BLÅHAJ I guess, plz dont sue this is fair use frfr
