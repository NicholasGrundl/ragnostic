# Action Items

## Ingestion flow

Completed the basic ingestion flow and it runs in jupyter.  Whats missing is the following:
- cleanup of ingestion upon success
- possible adding the original filename as a file field on indexing (i.e. change name when indexed with doc_id) and a suffic to the docis for human use
  - can rename files later when we summarize...
- add some logging across the module and custom log setup
- integration test for ingestion flow

Database client
- the client needs some improvement and is tied to business logic currently
- id like the base cvlient to be a CRUD (get, set, update, delete) API caller to the database, we can use this in the API as well
- id like a indexing specific set of functions or database wrapper that have the dusiness logic

Document search and retrieval client
- id like a basic query client or call that runs on a simple keyword search or allows interfacing with the database in code
- basically search the document titles (original title) so humans can use it lightly as a library

## Semantic extraction flow

- just make functions without tests for demo
- run docling and update the database with text, images, tables
- combine all images with descriptions and insert in text at docling location
- assume document level sections and chunk using basic params (overlap and length)

## Query flow
- run standard query using vectors and chunks


