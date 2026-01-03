test: .venv
	cp   convos/m.yml  convos/u.yml
	uv run -m hallmoot convos/u.yml
.venv: pyproject.toml
	uv sync
clean:
	find -name \*~ -o -name .\*~ | xargs rm -fr
realclean: clean
	find -name __pycache__ | xargs rm -fr
	tree --gitignore -a .
