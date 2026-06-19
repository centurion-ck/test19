import subprocess

class DeploymentAgent:

    def deploy(self):

        subprocess.run(
            ["terraform","apply","-auto-approve"]
        )