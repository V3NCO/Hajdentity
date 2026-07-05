{
  description = "Flake for Hajdentity development";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1";

  outputs =
    { self, ... }@inputs:

    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forEachSupportedSystem =
        f:
        inputs.nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            inherit system;
            pkgs = import inputs.nixpkgs {
              inherit system;
              overlays = [ inputs.self.overlays.default ];
            };
          }
        );

      pyversion = "3.13";
    in
    {
      overlays.default = final: prev: rec {
        nodejs = prev.nodejs;
        yarn = (prev.yarn.override { inherit nodejs; });
      };

      devShells = forEachSupportedSystem (
        { pkgs, system }:
        let
          concatMajorMinor =
            v:
            pkgs.lib.pipe v [
              pkgs.lib.versions.splitVersion
              (pkgs.lib.sublist 0 2)
              pkgs.lib.concatStrings
            ];

          python = pkgs."python${concatMajorMinor pyversion}";

          pgWithExt = pkgs.postgresql.withPackages (p: [ p.pgroonga ]);
        in
        {
          default = pkgs.mkShellNoCC {
            venvDir = ".venv";

            postShellHook = ''
              export MISSKEY_CONFIG_DIR="$PWD/.sharkey"
              export GARAGE_DEFAULT_BUCKET="hajdentity"
              export GARAGE_DATA="$PWD/.garage"
              export GARAGE_CONFIG_FILE="$GARAGE_DATA/garage.toml"
              mkdir -p "$MISSKEY_CONFIG_DIR"
              mkdir -p "$PWD/.files"
              mkdir -p "$PWD/.garage"

              if [ ! -f "$MISSKEY_CONFIG_DIR/default.yml" ]; then
                cat > "$MISSKEY_CONFIG_DIR/default.yml" <<EOF
              url: http://localhost:2456/
              port: 2456
              db:
                host: 127.0.0.1
                port: 5432
                db: hajdentity-sharkey
                user: postgres
                pass: ""
              redis:
                host: 127.0.0.1
                port: 6379
              meilisearch:
                host: 127.0.0.1
                port: 7700
                index: sharkey
              id: aidx
              mediaDirectory: "$PWD/.files"
              EOF
                echo "Generated fresh default.yml config!"
              fi

              # 3. Python venv warning
              venvVersionWarn() {
              	local venvVersion
              	venvVersion="$("$venvDir/bin/python" -c 'import platform; print(platform.python_version())')"

              	[[ "$venvVersion" == "${python.version}" ]] && return

              	cat <<EOF
              Warning: Python version mismatch: [$venvVersion (venv)] != [${python.version}]
                       Delete '$venvDir' and reload to rebuild for version ${python.version}
              EOF
              }

              venvVersionWarn
            '';

            packages =
              (with python.pkgs; [
                venvShellHook
                pip

                pydantic-settings
                piccolo
                uvicorn
                starlette
                fastapi
                fastapi-mail
                pycryptodome
                pyjwt
                pwdlib
                python-multipart
                minio

                (buildPythonPackage rec {
                  pname = "piccolo-api";
                  version = "1.9.0";
                  format = "setuptools";
                  src = pkgs.fetchFromGitHub {
                    owner = "piccolo-orm";
                    repo = "piccolo_api";
                    rev = version;
                    hash = "sha256-Ugi6PsP3MoCaPot6bWdXvYddU1zOwHxDOcI4bsSVmrI=";
                  };
                  doCheck = false;
                })


              ]
              ++ fastapi.optional-dependencies.standard
              ++ piccolo.optional-dependencies.postgres
              )
              ++ [
                pkgs.nodejs
                pkgs.pnpm
                pkgs.yarn
                pkgs.openssl

                pkgs.sharkey
                pkgs.garage_2

                pgWithExt
                pkgs.redis
                pkgs.meilisearch

                (pkgs.writeShellScriptBin "db-setup" ''
                  export PGDATA="$PWD/.pgdata"
                  export PGHOST="$PGDATA"
                  if [ ! -d "$PGDATA" ]; then
                    echo "Initializing PostgreSQL database..."
                    initdb -U postgres -D "$PGDATA" --auth=trust
                    echo "unix_socket_directories = '$PGDATA'" >> "$PGDATA/postgresql.conf"
                    echo "listen_addresses = '127.0.0.1'" >> "$PGDATA/postgresql.conf"
                    pg_ctl -D "$PGDATA" -l "$PGDATA/logfile" start
                    sleep 2
                    createdb -U postgres hajdentity
                    createdb -U postgres hajdentity-sharkey
                    createdb -U postgres hajdentity-garage
                    pg_ctl -D "$PGDATA" stop
                    echo "Database initialized!"
                  else
                    echo "Database already initialized at $PGDATA"
                  fi

                  export GARAGE_DEFAULT_ACCESS_KEY="GK$(openssl rand -hex 16)"
                  export GARAGE_DEFAULT_SECRET_KEY="$(openssl rand -hex 32)"
                  export GARAGE_DEFAULT_BUCKET="hajdentity"
                  export GARAGE_DATA="$PWD/.garage"
                  export GARAGE_CONFIG_FILE="$GARAGE_DATA/garage.toml"

                  cat > $GARAGE_DATA/garage.toml <<EOF
                  metadata_dir = "/tmp/meta"
                  data_dir = "/tmp/data"
                  db_engine = "sqlite"

                  replication_factor = 1

                  rpc_bind_addr = "[::]:3901"
                  rpc_public_addr = "127.0.0.1:3901"
                  rpc_secret = "$(openssl rand -hex 32)"

                  [s3_api]
                  s3_region = "garage"
                  api_bind_addr = "[::]:3900"
                  root_domain = ".s3.garage.localhost"

                  [admin]
                  api_bind_addr = "[::]:3903"
                  admin_token = "$(openssl rand -base64 32)"
                  metrics_token = "$(openssl rand -base64 32)"
                  EOF


                  echo "Garage access key is : $GARAGE_DEFAULT_ACCESS_KEY"
                  echo "Garage secret key is : $GARAGE_DEFAULT_SECRET_KEY"
                  echo "Starting garage server for the first time, press Ctrl+C to stop it once its started"
                  garage server --single-node --default-bucket
                '')

                (pkgs.writeShellScriptBin "dev-start" ''
                  export PGDATA="$PWD/.pgdata"
                  export REDIS_DATA="$PWD/.redis"
                  export MEILI_DATA="$PWD/.meili"
                  export GARAGE_DATA="$PWD/.garage"
                  export GARAGE_CONFIG_FILE="$GARAGE_DATA/garage.toml"

                  mkdir -p "$REDIS_DATA" "$MEILI_DATA" "$GARAGE_DATA"

                  echo "starting postgres"
                  pg_ctl -D "$PGDATA" -l "$PGDATA/logfile" start

                  echo "starting redis"
                  redis-server --dir "$REDIS_DATA" --port 6379 --daemonize yes

                  echo "starting meilisearch"
                  meilisearch --db-path "$MEILI_DATA" > "$MEILI_DATA/logfile" 2>&1 &
                  echo $! > "$MEILI_DATA/pid"
                  echo "starting garage"

                  garage server --single-node --default-bucket > "$GARAGE_DATA/logfile" 2>&1 &
                  echo $! > "$GARAGE_DATA/pid"
                  sleep 1

                  echo "all local services started i think? maybe? idk? just check for errors"
                '')

                (pkgs.writeShellScriptBin "dev-stop" ''
                  export PGDATA="$PWD/.pgdata"
                  export MEILI_DATA="$PWD/.meili"
                  export GARAGE_DATA="$PWD/.garage"

                  echo "stopping postgres"
                  pg_ctl -D "$PGDATA" stop || true

                  echo "stopping redis"
                  redis-cli shutdown || true

                  echo "stopping meilisearch"
                  if [ -f "$MEILI_DATA/pid" ]; then
                    kill $(cat "$MEILI_DATA/pid") 2>/dev/null || true
                    rm "$MEILI_DATA/pid"
                  fi

                  echo "stopping garage"
                  if [ -f "$GARAGE_DATA/pid" ]; then
                    kill $(cat "$GARAGE_DATA/pid") 2>/dev/null || true
                    rm "$GARAGE_DATA/pid"
                  fi

                  echo "all local services stopped i think"
                '')

                self.formatter.${system}
              ];
          };
        }
      );

      formatter = forEachSupportedSystem ({ pkgs, ... }: pkgs.nixfmt);
    };
}
