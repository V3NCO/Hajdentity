{
  description = "Flake for Hajdentity";

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

      getPython = pkgs:
        let
          concatMajorMinor =
            v:
            pkgs.lib.pipe v [
              pkgs.lib.versions.splitVersion
              (pkgs.lib.sublist 0 2)
              pkgs.lib.concatStrings
            ];
        in pkgs."python${concatMajorMinor pyversion}";

      hajdentityPythonPackages = pkgs: python:
        with python.pkgs; [
          venvShellHook
          pip
          pydantic-settings
          emoji
          piccolo
          uvicorn
          starlette
          fastapi
          fastapi-mail
          (scalar-fastapi.overridePythonAttrs { doCheck = false; })
          pycryptodome
          pyjwt
          pwdlib
          python-multipart
          minio
          pillow
          slowapi
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
        ++ piccolo.optional-dependencies.postgres;

    in
    {
      overlays.default = final: prev: {
        nodejs = prev.nodejs;
      };

      packages = forEachSupportedSystem (
        { pkgs, system }:
        let
          python = getPython pkgs;
          pythonEnv = python.withPackages (p: hajdentityPythonPackages pkgs python);
        in
        {
          backend = pkgs.stdenv.mkDerivation {
            pname = "hajdentity-backend";
            version = "0.1.0";
            src = ./api;

            nativeBuildInputs = [ pkgs.makeWrapper ];
            buildInputs = [ pythonEnv ];

            installPhase = ''
              mkdir -p $out/share/hajdentity
              cp -r . $out/share/hajdentity/

              mkdir -p $out/bin
              makeWrapper ${pythonEnv}/bin/uvicorn $out/bin/hajdentity-backend \
                --add-flags "app:app" \
                --set PYTHONPATH "$out/share/hajdentity" \
                --chdir "$out/share/hajdentity"
            '';
          };

          frontend = pkgs.buildNpmPackage {
            pname = "hajdentity-frontend";
            version = "0.1.0";
            src = ./frontend;

            npmDepsHash = "sha256-c40qRe4ykn9cAfUOMASJ32+6WS+3w9XmUN84OhfAtHI=";

            env = {
              NUXT_TELEMETRY_DISABLED = "1";
            };

            nativeBuildInputs = [ pkgs.makeWrapper ];

            installPhase = ''
              runHook preInstall
              mkdir -p $out/share/hajdentity-frontend
              cp -r .output/* $out/share/hajdentity-frontend/

              mkdir -p $out/bin
              makeWrapper ${pkgs.nodejs}/bin/node $out/bin/hajdentity-frontend \
                --add-flags "$out/share/hajdentity-frontend/server/index.mjs"
              runHook postInstall
            '';
          };

          default = self.packages.${system}.backend;
        }
      );

      devShells = forEachSupportedSystem (
        { pkgs, system }:
        let
          python = getPython pkgs;
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
              (hajdentityPythonPackages pkgs python)
              ++ [
                pkgs.nodejs
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

                  garage server > "$GARAGE_DATA/logfile" 2>&1 &
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

      nixosModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.hajdentity;
          isPostgresUnixSocket = lib.hasPrefix "/" cfg.db.host;
          boolToStr = b: if b then "True" else "False";
        in {
          options.services.hajdentity = {
            enable = lib.mkEnableOption "Hajdentity Backend API Service";

            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${pkgs.system}.backend;
              defaultText = lib.literalExpression "self.packages.\${pkgs.system}.backend";
              description = "The Hajdentity backend package derivation to run.";
            };

            environmentFile = lib.mkOption {
              type = lib.types.nullOr lib.types.path;
              default = null;
              description = "Path to a secure env file containing extra credentials (e.g., S3 secrets).";
            };

            host = lib.mkOption {
              type = lib.types.str;
              default = "127.0.0.1";
              description = "Host IP to bind the backend server to.";
            };

            port = lib.mkOption {
              type = lib.types.port;
              default = 8000;
              description = "Port to bind the backend server to.";
            };

            user = lib.mkOption {
              type = lib.types.str;
              default = "hajdentity";
              description = "The user Hajdentity services should run as.";
            };

            group = lib.mkOption {
              type = lib.types.str;
              default = "hajdentity";
              description = "The group Hajdentity services should run as.";
            };

            frontend = {
              enable = lib.mkEnableOption "Hajdentity Frontend Nuxt Server";

              package = lib.mkOption {
                type = lib.types.package;
                default = self.packages.${pkgs.system}.frontend;
                defaultText = lib.literalExpression "self.packages.\${pkgs.system}.frontend";
                description = "The Hajdentity frontend package derivation to run.";
              };

              host = lib.mkOption {
                type = lib.types.str;
                default = "127.0.0.1";
                description = "Host IP to bind the frontend server to.";
              };

              port = lib.mkOption {
                type = lib.types.port;
                default = 3000;
                description = "Port to bind the frontend server to.";
              };
            };

            adminEmail = lib.mkOption { type = lib.types.str; };
            systemId = lib.mkOption { type = lib.types.str; default = "YOUR_SERVER_NAME"; };
            baseUrl = lib.mkOption { type = lib.types.str; default = "http://localhost:3000/"; };
            sessionIdleMinutes = lib.mkOption { type = lib.types.int; default = 43200; };
            sessionAbsoluteDays = lib.mkOption { type = lib.types.int; default = 90; };
            nfcSessionMinutes = lib.mkOption { type = lib.types.int; default = 10; };
            verificationTokenExpireMinutes = lib.mkOption { type = lib.types.int; default = 60; };
            maxImageSize = lib.mkOption { type = lib.types.int; default = 10; };

            db = {
              enable = lib.mkEnableOption "local PostgreSQL database managed by Hajdentity" // {
                default = true;
              };
              createDB = lib.mkEnableOption "automatic creation of the database and matching role" // {
                default = true;
              };
              database = lib.mkOption {
                type = lib.types.str;
                default = "hajdentity";
                description = "Database name.";
              };
              user = lib.mkOption {
                type = lib.types.str;
                default = "hajdentity";
                description = "Database user matching the system service account.";
              };
              host = lib.mkOption {
                type = lib.types.str;
                default = "/run/postgresql";
                description = "Database host address. Set to a directory path starting with '/' for Unix socket.";
              };
              port = lib.mkOption {
                type = lib.types.port;
                default = 5432;
                description = "Database port.";
              };
            };

            mail = {
              username = lib.mkOption { type = lib.types.str; };
              fromAddress = lib.mkOption { type = lib.types.str; };
              fromName = lib.mkOption { type = lib.types.str; default = "Hajdentity"; };
              port = lib.mkOption { type = lib.types.port; default = 465; };
              server = lib.mkOption { type = lib.types.str; };
              startTls = lib.mkOption { type = lib.types.bool; default = false; };
              sslTls = lib.mkOption { type = lib.types.bool; default = true; };
              useCreds = lib.mkOption { type = lib.types.bool; default = true; };
              validateCerts = lib.mkOption { type = lib.types.bool; default = true; };
            };

            s3 = {
              endpoint = lib.mkOption { type = lib.types.str; default = "localhost:3900"; };
              bucket = lib.mkOption { type = lib.types.str; default = "hajdentity"; };
              secure = lib.mkOption { type = lib.types.bool; default = false; };
              region = lib.mkOption { type = lib.types.str; default = "garage"; };
            };

            sharkey = {
              baseUrl = lib.mkOption {
                type = lib.types.str;
                description = "Internal loopback URL used by the backend to talk to Sharkey.";
              };
              publicUrl = lib.mkOption {
                type = lib.types.str;
                description = "Public external URL sent to clients/browsers.";
              };
            };
          };

          config = lib.mkIf cfg.enable {
            assertions = [
              {
                assertion = !isPostgresUnixSocket -> cfg.environmentFile != null;
                message = "An environmentFile containing at least the database password must be provided when postgres unix sockets are not used.";
              }
            ];

            # 1. Handle Declarative Postgres Integration
            services.postgresql = lib.mkIf cfg.db.enable {
              enable = true;
              ensureDatabases = lib.mkIf cfg.db.createDB [ cfg.db.database ];
              ensureUsers = lib.mkIf cfg.db.createDB [
                {
                  name = cfg.db.user;
                  ensureDBOwnership = true;
                  ensureClauses.login = true;
                }
              ];
            };

            # 2. Provision Native System accounts
            users.users = lib.mkIf (cfg.user == "hajdentity") {
              hajdentity = {
                name = "hajdentity";
                group = cfg.group;
                isSystemUser = true;
              };
            };
            users.groups = lib.mkIf (cfg.group == "hajdentity") { hajdentity = { }; };

            systemd.services.hajdentity = {
              description = "Hajdentity Backend API";
              wantedBy = [ "multi-user.target" ];
              requires = lib.mkIf (cfg.db.enable && isPostgresUnixSocket) [ "postgresql.service" ];
              after = [ "network.target" ] ++ lib.optionals (cfg.db.enable && isPostgresUnixSocket) [ "postgresql.service" ];

              serviceConfig = {
                Type = "simple";
                StateDirectory = "hajdentity";
                WorkingDirectory = "/var/lib/hajdentity";
                EnvironmentFile = lib.optional (cfg.environmentFile != null) cfg.environmentFile;
                ExecStart = "${cfg.package}/bin/hajdentity-backend --host ${cfg.host} --port ${toString cfg.port}";
                Restart = "on-failure";
                User = cfg.user;
                Group = cfg.group;
              };

              environment = {
                HAJDENTITY_ADMIN_EMAIL = cfg.adminEmail;
                HAJDENTITY_SYSTEM_ID = cfg.systemId;
                HAJDENTITY_BASE_URL = cfg.baseUrl;
                HAJDENTITY_SESSION_IDLE_MINUTES = toString cfg.sessionIdleMinutes;
                HAJDENTITY_SESSION_ABSOLUTE_DAYS = toString cfg.sessionAbsoluteDays;
                HAJDENTITY_NFC_SESSION_MINUTES = toString cfg.nfcSessionMinutes;
                HAJDENTITY_VERIFICATION_TOKEN_EXPIRE_MINUTES = toString cfg.verificationTokenExpireMinutes;
                HAJDENTITY_MAX_IMAGE_SIZE = toString cfg.maxImageSize;

                HAJDENTITY_DB__DATABASE = cfg.db.database;
                HAJDENTITY_DB__USER = cfg.db.user;
                HAJDENTITY_DB__HOST = cfg.db.host;
                HAJDENTITY_DB__PORT = toString cfg.db.port;

                HAJDENTITY_MAIL__USERNAME = cfg.mail.username;
                HAJDENTITY_MAIL__FROM_ADDRESS = cfg.mail.fromAddress;
                HAJDENTITY_MAIL__FROM_NAME = cfg.mail.fromName;
                HAJDENTITY_MAIL__PORT = toString cfg.mail.port;
                HAJDENTITY_MAIL__SERVER = cfg.mail.server;
                HAJDENTITY_MAIL__STARTTLS = boolToStr cfg.mail.startTls;
                HAJDENTITY_MAIL__SSL_TLS = boolToStr cfg.mail.sslTls;
                HAJDENTITY_MAIL__USE_CREDS = boolToStr cfg.mail.useCreds;
                HAJDENTITY_MAIL__VALIDATE_CERTS = boolToStr cfg.mail.validateCerts;

                HAJDENTITY_S3__ENDPOINT = cfg.s3.endpoint;
                HAJDENTITY_S3__BUCKET = cfg.s3.bucket;
                HAJDENTITY_S3__SECURE = boolToStr cfg.s3.secure;
                HAJDENTITY_S3__REGION = cfg.s3.region;

                HAJDENTITY_SHARKEY__BASE_URL = cfg.sharkey.baseUrl;
                HAJDENTITY_SHARKEY__PUBLIC_URL = cfg.sharkey.publicUrl;
              };
            };

            systemd.services.hajdentity-frontend = lib.mkIf cfg.frontend.enable {
              description = "Hajdentity Frontend Nuxt Server";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" ];

              serviceConfig = {
                Type = "simple";
                ExecStart = "${cfg.frontend.package}/bin/hajdentity-frontend";
                Restart = "on-failure";
                User = cfg.user;
                Group = cfg.group;
              };

              environment = {
                HOST = cfg.frontend.host;
                PORT = toString cfg.frontend.port;
                NUXT_PUBLIC_API_URL = cfg.baseUrl;
                NUXT_API_PROXY_TARGET = "http://127.0.0.1:${toString cfg.port}";
              };
            };
          };
        };
    };
}
