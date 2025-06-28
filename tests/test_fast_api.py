import jobserver

# import jobserver.data as data

config = data.ConfigClient()
database = data.DatabaseClient(config)
job_server = core.JobServer(config, database)
