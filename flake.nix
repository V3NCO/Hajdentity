{
  description = "Flake for Hajdentity development";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1";

  outputs =
    { self, ... }@inputs:

    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
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
              mkdir -p "$MISSKEY_CONFIG_DIR"
              mkdir -p "$PWD/.files"

              if [ ! -f "$MISSKEY_CONFIG_DIR/default.yml" ]; then
                cat > "$MISSKEY_CONFIG_DIR/default.yml" <<EOF
              url: http://localhost:2456/
              port: 2456
              db:
                host: 127.0.0.1
                port: 5432
                db: hajdentity
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

                piccolo
                uvicorn
                starlette
                fastapi

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

                pkgs.sharkey

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
                    pg_ctl -D "$PGDATA" stop
                    echo "Database initialized!"
                  else
                    echo "Database already initialized at $PGDATA"
                  fi
                '')

                (pkgs.writeShellScriptBin "dev-start" ''
                  export PGDATA="$PWD/.pgdata"
                  export REDIS_DATA="$PWD/.redis"
                  export MEILI_DATA="$PWD/.meili"

                  mkdir -p "$REDIS_DATA" "$MEILI_DATA"

                  echo "starting postgres"
                  pg_ctl -D "$PGDATA" -l "$PGDATA/logfile" start

                  echo "starting redis"
                  redis-server --dir "$REDIS_DATA" --port 6379 --daemonize yes

                  echo "starting meilisearch"
                  meilisearch --db-path "$MEILI_DATA" > "$MEILI_DATA/logfile" 2>&1 &
                  echo $! > "$MEILI_DATA/pid"

                  echo "all local services started i think? maybe? idk? just check for errors"
                '')

                (pkgs.writeShellScriptBin "dev-stop" ''
                  export PGDATA="$PWD/.pgdata"
                  export MEILI_DATA="$PWD/.meili"

                  echo "stopping postgres"
                  pg_ctl -D "$PGDATA" stop || true

                  echo "stopping redis"
                  redis-cli shutdown || true

                  echo "stopping meilisearch"
                  if [ -f "$MEILI_DATA/pid" ]; then
                    kill $(cat "$MEILI_DATA/pid") 2>/dev/null || true
                    rm "$MEILI_DATA/pid"
                  fi

                  echo "all local services stopped i think"
                '')

                self.formatter.${system}
              ];
          };
        }
      );

      formatter = forEachSupportedSystem ({ pkgs, ... }: pkgs.nixfmt-rfc-style);
    };
}
