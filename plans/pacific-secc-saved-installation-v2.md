# Saved installation with cloud Git object transport

The v1 installation passed source/parent preflight and all eight refusal checks.
GitHub then rejected a large Git Blobs REST API request with HTTP422. The run
finished without changing the branch. Preserve the executed v1 source, request,
workflow and failure receipt; do not rerun that transport.

V2 retains the exact two reviewed artifacts, all byte hashes, 22-file generated
inventory, scientific preservation, parent checks, one-cloud-job sequencing,
and the prohibition on builds, browser runs, main merges and local bulk sync.
Its explicit request additionally permits Git object transport **in cloud**.

Write verified binary blobs to the cloud checkout's object store. Build one
candidate tree through a private index initialized from the exact control
commit. Replace only the 22 saved paths, add the installation proof and disable
the v2 request. Check every candidate blob ID/size, the parent, allowed diff,
and all protected paths before publishing. Send exactly one nonforce refspec
to the existing working branch, then verify remote blob identities and main.
Never use force, wildcard refspecs, tags, deletions or a main refspec.

An isolated local fixture exercises exact binary preservation, unrelated-file
preservation, a successful single-ref transaction and rejection of a stale
competing transaction. This fixture uses only tiny synthetic Git repositories;
it loads no installed OSW packet, builds no code and launches no browser.

The v1 request must be disabled in the same source activation that enables v2.
Retain original artifact failures and the successful image review. Update the
measurement coverage checkpoint only after a remotely verified installation.
