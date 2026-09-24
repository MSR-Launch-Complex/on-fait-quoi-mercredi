"""on-fait-quoi-mercredi: the data reader, the schema check, and the site builder.

One dependency, PyYAML, declared in pyproject.toml; everything else is standard
library. `make build` reaches the network at no point, and neither does the page it
writes. See docs/schema.md for the record shape.
"""
