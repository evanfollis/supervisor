.PHONY: help check test eval contract

help:
	@printf '%s\n' \
	  'make check     Run repository contract, deterministic tests, and prompt evals' \
	  'make contract  Validate this repository against ADR-0050' \
	  'make test      Run deterministic Python and shell tests' \
	  'make eval      Run governed prompt/instruction checks'

contract:
	python3 scripts/repository-contract.py .

test:
	@set -e; found=0; for test_file in tests/test-*.py; do \
	  [ -e "$$test_file" ] || continue; found=1; python3 "$$test_file"; \
	done; [ "$$found" -eq 1 ] || { echo 'no Python tests found' >&2; exit 1; }
	@set -e; for test_file in tests/test-*.sh; do \
	  [ -e "$$test_file" ] || continue; bash "$$test_file"; \
	done

eval:
	scripts/prompteval check .

check: contract test eval
