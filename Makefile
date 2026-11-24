.PHONY: migrate-workspaces

migrate-workspaces:
	docker compose run --rm --no-deps --build workspaces sh -ec '\
		PGHOST="$$DB_HOST" PGPORT="$$DB_PORT" \
		PGUSER="$$DB_USER" PGPASSWORD="$$DB_PASSWORD" \
		uv run --locked yoyo apply --batch --no-config-file \
		--database "postgresql+psycopg:///$$DB_NAME" \
		$(if $(REVISION),--revision "$(REVISION)") services/workspaces/migrations'

migrate-events:
	docker compose run --rm --no-deps --build events sh -ec '\
		PGHOST="$$DB_HOST" PGPORT="$$DB_PORT" \
		PGUSER="$$DB_USER" PGPASSWORD="$$DB_PASSWORD" \
		uv run --locked yoyo apply --batch --no-config-file \
		--database "postgresql+psycopg:///$$DB_NAME" \
		$(if $(REVISION),--revision "$(REVISION)") services/events/migrations'