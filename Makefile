PYTHON ?= python3
CHECKER := skills/paper-explainer/scripts/check_sources.py

.PHONY: demo test validate-skill

demo:
	@set +e; \
	output="$$( $(PYTHON) $(CHECKER) \
		--tables examples/mini-fake-citation/claims.json \
		--source examples/mini-fake-citation/source.txt 2>&1 )"; \
	code=$$?; \
	printf '%s\n' "$$output"; \
	if [ $$code -ne 1 ]; then \
		echo "Expected demo checker to exit 1 because it contains one fake citation; got $$code" >&2; \
		exit 1; \
	fi; \
	printf '%s\n' "$$output" | grep -F "L1 quote-exists: 3 ok / 1 unsupported" >/dev/null || { \
		echo "Expected demo output to contain L1 quote-exists: 3 ok / 1 unsupported" >&2; \
		exit 1; \
	}; \
	printf '%s\n' "$$output" | grep -F "VERDICT: REVIEW NEEDED" >/dev/null || { \
		echo "Expected demo output to contain VERDICT: REVIEW NEEDED" >&2; \
		exit 1; \
	}; \
	printf '%s\n' "$$output" | grep -F "Fake citation demo" >/dev/null || { \
		echo "Expected demo output to contain Fake citation demo" >&2; \
		exit 1; \
	}

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-skill:
	$(PYTHON) "$${CODEX_HOME:-$$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/paper-explainer
