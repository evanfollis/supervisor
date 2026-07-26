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
	@for test_file in tests/test-*.py; do python3 "$$test_file"; done
	@for test_file in tests/test-*.sh; do bash "$$test_file"; done

eval:
	scripts/prompteval check .

check: contract test eval
