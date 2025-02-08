import subprocess
import os
from typing import List, Union

# setup path incase it does not exist
if os.getenv("PATH", None) is None:
    os.environ["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

if "/bin" not in os.environ["PATH"]:
    os.environ["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" + ":" + os.environ["PATH"]

class CommandRunner:
    """
    A helper class to run a command in the terminal.

    Example:
        runner = CommandRunner()
        result = runner.run(["ls", "-al"])
    """

    @staticmethod
    def run(command: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(command, check=True, stdout=subprocess.PIPE)


class Installer:

    @staticmethod
    def install(url: str,
                target_folder_name: str = None,
                untar: bool = False,
                untar_file_name: str = None,
                relative_sys_paths_to_add: List[str] = None):
        """
        Install a file by downloading it via wget and untarring it.

        Args:
            url (str): The URL of the file to install.
            target_folder_name (str): Target folder to install the file.
            untar (bool): Whether to untar the file.
            untar_file_name (str): The name of the untarred file.
            relative_sys_paths_to_add (List[str]): The paths to add to the
                system environment variable PATH.

        Returns:
            None
        """
        print(f"Installing {url}")
        if target_folder_name is not None and os.path.exists(target_folder_name) is False:
            os.mkdir(target_folder_name)
        resp = CommandRunner.run(["wget", url])
        if resp.returncode == 0:
            if untar:
                file_name = untar_file_name or url.split("/")[-1]
                print(f"Untarring {file_name}")
                if target_folder_name is None:
                    resp = CommandRunner.run(["tar", "-xf", file_name])
                else:
                    resp = CommandRunner.run(
                        ["tar", "--strip-components", "1", "-xf", file_name, "-C", target_folder_name])
                if resp.returncode == 0:
                    os.remove(file_name)
            if relative_sys_paths_to_add:
                cwd = os.getcwd()
                for path in relative_sys_paths_to_add:
                    if path.startswith("/"):
                        path = path[1:]
                    print(f"Adding {cwd}/{path} to PATH")
                    os.environ["PATH"] = f"{cwd}/{path}:{os.environ['PATH']}"


class NodeJSLTS:
    V18_LTS = "v18.20.3"


class OperatingSystem:
    LINUX = "linux"
    MACOS = "macos"


class NodeJSInstaller:
    def __init__(self,
                 target_folder_name: str = None,
                 version=NodeJSLTS.V18_LTS,
                 _os=OperatingSystem.LINUX,
                 arch="x64"):
        """
        Initialize NodeJSInstaller

        Args:
            target_folder_name (str): target folder to download the nodejs distro to
            version (NodeJSLTS): The version of nodejs to install
            _os (OperatingSystem): The OS to download the nodejs distro for
            arch (str): The architecture to download the nodejs distro for
        """
        self.version = version
        self.os = _os
        self.arch = arch
        self.target_folder_name = target_folder_name or "nodejs_download"

    def _download_url(self):
        return f"https://nodejs.org/dist/{self.version}/node-{self.version}-{self.os}-{self.arch}.tar.xz"

    def install(self):
        """
        Downloads and installs the NodeJS distro
        """
        Installer.install(
            url=self._download_url(),
            target_folder_name=self.target_folder_name,
            untar=True,
            relative_sys_paths_to_add=[f"{self.target_folder_name}/bin"]
        )

    def sys_path(self):
        """
        The path to the binary folder of the nodejs distro
        """
        
        return f"{os.getcwd()}/{self.target_folder_name}/bin"

    def node_path(self):
        """
        Returns the full path to the Node.js binary within the installed
        Node.js distribution.

        This path is constructed based on the current working directory
        and the target folder where Node.js is installed.

        Returns:
            str: The full path to the Node.js binary.
        """

        return f"{os.getcwd()}/{self.target_folder_name}/bin/node"

    def npm_path(self):
        """
        Returns the full path to the NPM binary within the installed
        Node.js distribution.

        This path is constructed based on the current working directory
        and the target folder where Node.js is installed.

        Returns:
            str: The full path to the NPM binary.
        """
        
        return f"{os.getcwd()}/{self.target_folder_name}/bin/npm"

    def npx_path(self):
        """
        Returns the full path to the Npx binary within the installed
        Node.js distribution.

        This path is constructed based on the current working directory
        and the target folder where Node.js is installed.

        Returns:
            str: The full path to the Npx binary.
        """
        
        return f"{os.getcwd()}/{self.target_folder_name}/bin/npx"


class BinaryCommandRunner:

    def __init__(self, ):
        self.binary_path = None

    def configure(self, binary_path: str):
        self.binary_path = binary_path

    def run(self, command: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run([self.binary_path] + command, check=True)


class NodeJsEntrypoint:

    def __init__(self,
                 version=NodeJSLTS.V18_LTS,
                 _os=OperatingSystem.LINUX,
                 arch="x64"):
        self._installer = NodeJSInstaller(version=version, _os=_os, arch=arch)
        self.npm_command_runner = BinaryCommandRunner()
        self.npx_command_runner = BinaryCommandRunner()
        self._commands = []
        self._chdir = None

    def with_command(self, command: Union[List[str], str]):
        """
        Adds a command to the list of commands to be executed.

        This method accepts a command in the form of either a string or a list.
        If a string is provided, it is split into a list of arguments. If the
        command starts with "npm", the "npm" part is removed.

        Args:
            command (Union[List[str], str]): The command to be added, either as a
            list of arguments or a single string.

        Returns:
            self: The NodeJsEntrypoint instance, to allow for method chaining.
        """

        if isinstance(command, str):
            command = command.split(" ")
        if command[0] == "npm":
            command = command[1:]

        self._commands.append(command)
        return self

    def with_cwd(self, cwd: str):
        self._chdir = cwd
        return self

    def _configure_sys_path(self):
        """
        Configures the system PATH environment variable to include the Node.js
        binary distribution, so that the Node.js binaries can be found by the
        subprocess module.

        This method ensures that the PATH environment variable contains the
        path to the Node.js binary distribution, by appending it to the
        existing value. This allows the subprocess module to find the Node.js
        binaries.

        The method does not do anything if the PATH environment variable
        already contains the path to the Node.js binary distribution.

        Note that this method does not modify the system-wide PATH
        environment variable, but only the PATH environment variable for the
        current process.

        """
        
        if self._installer.sys_path() not in os.environ["PATH"]:
            os.environ["PATH"] = f"{self._installer.sys_path()}:{os.environ['PATH']}"

    def _setup_binaries(self):
        """
        Sets up the Node.js binaries by installing them if they do not already
        exist and configuring the BinaryCommandRunners for npm and npx.

        This method first checks if the Node.js binaries exist. If they do not,
        it installs them using the NodeJSInstaller. Then, it configures the
        BinaryCommandRunners for npm and npx with the paths to the npm and npx
        binaries.

        """

        if self._chdir:
            os.chdir(self._chdir)

        node_path = self._installer.node_path()
        npm_path = self._installer.npm_path()
        npx_path = self._installer.npx_path()
        if os.path.exists(node_path) is False or os.path.exists(npm_path) is False:
            self._installer.install()

        self.npm_command_runner.configure(npm_path)
        self.npx_command_runner.configure(npx_path)

    def run(self):
        """
        Executes the list of commands using the configured Node.js environment.

        This method sets up the necessary Node.js binaries and configures the
        system PATH to include the Node.js distribution. It then iterates over
        each command in the list of commands, running them using the npx command
        runner. The output of each command is printed to the console.

        Raises:
            subprocess.CalledProcessError: If a command execution fails.
        """

        self._setup_binaries()
        self._configure_sys_path()
        for command in self._commands:
            print(f"Running {command}")
            resp = self.npx_command_runner.run(command)
            print(resp)
