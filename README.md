# jserv (Python Job Server)

jserv provides a framework to create, run, and manage jobs via a REST API. 

Some of the core functionality includes:
- Job priority management
- Pause/resume/cancel functionality
- Persistent storage for recovery of interrupted jobs
- State machine support
- SQLite-based tracking of updates, errors, server connections, and artifacts
- Webhook-based progress monitoring
