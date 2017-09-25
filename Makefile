.PHONY: help
help:
	@echo "Target       Description"
	@echo "============ =================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

.PHONY: test
test: ## Run unit tests and generate coverage.
	@bash -c "source test_env.sh; nosetests --with-coverage \
	                                        --cover-package=muse_gdrive \
                                                --cover-tests \
                                                --cover-erase \
                                                --cover-min-percentage=90"

LINT_TARGETS := setup.py muse_gdrive bin/google_drive
.PHONY: lint
lint: ## Run pep8 and pylint checks on python files.
	pep8 $(LINT_TARGETS)
	pylint $(LINT_TARGETS)

.PHONY: docs
docs: ## Create HTML documentation.
	@python -msphinx -M html doc doc/build

.PHONY: docs-publish
docs-publish: docs ## Publishes built documentation to GitHub Pages.
	@REV="$$(git describe)" && \
	 URL=$$(git config --get remote.origin.url | \
                sed -r 's|https://([^/]+?)/|git@\1:|') && \
	 cd doc/build && \
	 rm -rf repo && \
	 git clone -b gh-pages $${URL} repo && \
	 cd repo && \
	 git rm -rf . && \
	 find ../html -mindepth 1 -maxdepth 1 -exec mv {} . \; && \
	 git add . && \
	 git commit -m "Documentation generated for $${REV}." && \
	 git push origin gh-pages

.PHONY: hooks
hooks: ## Installs git pre-commit hook for the repository.
	@rm -f .git/hooks/pre-commit
	@printf "#!/usr/bin/env bash\nmake pre-commit" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit

.PHONY: no-unstaged
no-unstaged:
	@git diff --quiet || (echo "Unstaged changes found!" && exit 1)

# The docs target is part of pre-commit so we can make sure the docs at least
# build properly.
.PHONY: pre-commit
pre-commit: no-unstaged test lint docs ## Run all pre-commit checks.
