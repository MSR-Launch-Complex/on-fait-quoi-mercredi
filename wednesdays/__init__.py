"""on-fait-quoi-mercredi: the data reader, the schema check, and the site builder.

Everything here is standard library only, on purpose: `make build` has to work on a
clean checkout with no network and no install step, so the build cannot depend on a
package index being reachable. See docs/schema.md for the record shape.
"""
