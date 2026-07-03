PYTHON ?= python3
CHECKER := skills/paper-explainer/scripts/check_sources.py

.PHONY: demo test validate-skill

demo:
	@set +e; \
	$(PYTHON) $(CHECKER) \
		--tables examples/mini-fake-citation/claims.json \
		--source examples/mini-fake-citation/source.txt; \
	code=$$?; \
	if [ $$code -ne 1 ]; then \
		echo "Expected demo checker to exit 1 because it contains one fake citation; got $$code" >&2; \
		exit 1; \
	fi

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-skill:
	$(PYTHON) "$${CODEX_HOME:-$$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/paper-explainer
