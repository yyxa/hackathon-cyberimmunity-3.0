SHELL := bash

MODULES := managment-system \
			payment-system \
			mobile-client \
			car-monitor \
			car-network \
			car-verify-service \
			car-verify-payment \
			car-manager-service \
			car-control \
			car-verify-geodata \
			car-data \
			car-get-speed-from-geo \
			car-complex \
			car-gps \
			car-glonass \
			car-monitoring \
			car-engine \
			car-speed-lower \
			car-verify-driver \
			car-camera \
			car-get-speed-from-camera \
			car-speed-sensors \
			car-adas \
			car-verify-speed \
			car-energy \
			car-skin-sensors \



SLEEP_TIME := 10

.PHONY: dev_install
dev_install:
	@sudo apt install librdkafka-dev python3-venv
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -U pip
	.venv/bin/pip install -r requirements.txt

.PHONY: remove_kafka
remove_kafka:
	@if docker stop zookeeper broker; then \
		docker rm zookeeper broker; \
	fi

.PHONY: all
all:
	@$(MAKE) remove_kafka
	docker compose down
	docker compose up --build -d
	sleep ${SLEEP_TIME}

	for MODULE in ${MODULES}; do \
		echo Creating $${MODULE} topic; \
		docker exec broker \
			kafka-topics --create --if-not-exists \
			--topic $${MODULE} \
			--bootstrap-server localhost:9092 \
			--replication-factor 1 \
			--partitions 1; \
	done

.PHONY: logs
logs:
	@docker compose logs -f --tail 100

.PHONY: test
test:
	@$(MAKE) all
	sleep ${SLEEP_TIME}
	$(MAKE) test_e2e
	$(MAKE) test_security
	$(MAKE) clean

.PHONY: test_all
test_all: test_e2e test_security

.PHONY: test_e2e
test_e2e: check_venv
	@.venv/bin/python -m pytest tests/e2e-test/test_base_scheme.py

.PHONY: test_security
test_security: check_venv
	@.venv/bin/python tests/test_policies.py

.PHONY: down
down:
	@docker compose down 

.PHONY: clean
clean:
	@$(MAKE) down
	for MODULE in ${MODULES}; do \
		docker rmi $${MODULE};  \
	done

.PHONY: check_venv
check_venv:
	@[ -d ".venv" ] || (echo "Virtual environment not found. Run 'make dev_install' first."; exit 1)
