import jobserver as jserv


class FileWriteReadJob(jserv.Job):
    def __init__(self, job_parameters: jserv.structs.JobTemplate):
        super().__init__(
            _template=self.Template,
            _states=[
                FileWriteReadJob.State1_WriteFile,
                FileWriteReadJob.State2_ReadFile,
            ],
        )
        self.name = "FileWriteReadJob"

    class Parameters(jserv.structs.JobParameters):
        excited: bool

        def __init__(
            self,
            excited: bool,
            priority: jserv.enums.JobPriority = jserv.enums.JobPriority.NORMAL,
            max_threads: int = 1,
        ):
            self.excited = excited
            super().__init__(
                name="FileWriteReadJob",
                priority=priority,
                max_threads=max_threads,
            )

    class Template(jserv.structs.JobTemplate):
        def __init__(self, name: str, description: str, args: dict):
            super().__init__(
                name=name,
                description=description,
                args=args,
                parameter_class=FileWriteReadJob.Parameters,
            )

    class State1_WriteFile(jserv.Job.State):
        def start(self) -> bool:
            # Simulate file creation
            print("Creating file...")
            with open("example.txt", "w") as f:
                f.write("Hello, World!")
            return True

    class State2_ReadFile(jserv.Job.State):
        def start(self) -> bool:
            # Simulate writing to file
            with open("example.txt", "r") as f:
                content = f.read()
            print(f"File content: {content}")
            return True
