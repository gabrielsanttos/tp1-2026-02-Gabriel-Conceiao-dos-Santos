DB_ARGS = --db-host db --db-port 5432 --db-name ecommerce --db-user postgres --db-pass postgres

up:
	docker compose up -d --build

load:
	docker compose run --rm app python src/tp1_3.2.py $(DB_ARGS) --input /data/snap_amazon.txt

dashboard:
	docker compose run --rm app python src/tp1_3.3.py $(DB_ARGS) --product-asin $(ASIN) --output /app/out

clean:
	docker compose down -v

.PHONY: up load dashboard clean
