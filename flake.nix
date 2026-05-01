{
  description = "Flake for Hajdentity development";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1"; # unstable Nixpkgs

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
        in
        {
          default = pkgs.mkShellNoCC {
            venvDir = ".venv";

            postShellHook = ''
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
                pkgs.postgresql
                pkgs.redis
                pkgs.sharkey
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
                (pkgs.writeShellScriptBin "db-start" ''
                  export PGDATA="$PWD/.pgdata"
                  pg_ctl -D "$PGDATA" -l "$PGDATA/logfile" start
                '')
                (pkgs.writeShellScriptBin "db-stop" ''
                  export PGDATA="$PWD/.pgdata"
                  pg_ctl -D "$PGDATA" stop
                '')
                (pkgs.writeShellScriptBin "redis-start" ''
                  mkdir -p "$PWD/.redis"
                  redis-server --dir "$PWD/.redis" --port 6379 --daemonize yes
                '')
                (pkgs.writeShellScriptBin "redis-stop" ''
                  redis-cli shutdown
                '')
                (pkgs.writeShellScriptBin "sharkey-setup" ''
                  export PGDATA="$PWD/.pgdata"
                  export PGHOST="$PGDATA"

                  echo "Creating Sharkey configuration..."
                  mkdir -p "$PWD/.sharkey"
                  cat <<EOF > "$PWD/.sharkey/default.yml"
                  url: http://localhost:3000
                  port: 3000
                  db:
                    host: 127.0.0.1
                    port: 5432
                    db: sharkey
                    user: postgres
                    pass: ""
                  redis:
                    host: localhost
                    port: 6379
                  EOF

                  echo "Creating Sharkey database..."
                  createdb -U postgres sharkey || true

                  echo "Running Sharkey migrations..."
                  export MISSKEY_CONFIG_YML="$PWD/.sharkey/default.yml"
                  sharkey migrate
                  echo "Sharkey setup complete!"
                '')
                (pkgs.writeShellScriptBin "sharkey-start" ''
                  export MISSKEY_CONFIG_YML="$PWD/.sharkey/default.yml"
                  sharkey start
                '')
                self.formatter.${system}
              ];
          };
        }
      );

      formatter = forEachSupportedSystem ({ pkgs, ... }: pkgs.nixfmt);
    };
}
