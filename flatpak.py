import subprocess, dotbot

from typing import Dict, List, Literal, NamedTuple, Union


type Setting = Union[str, Dict[Literal["name", "url", "repo", "reinstall"], Union[str, bool]]]
type FlatpakSettings = Dict[Literal["repos", "apps"], List[Setting]]


class Repo(NamedTuple):
    name: str
    url: str


class App(NamedTuple):
    name: str
    repo: str
    reinstall: bool


KNOWN_REPOS = {
    "flathub": "https://dl.flathub.org/repo/flathub.flatpakrepo",
    "flathub-beta": "https://flathub.org/beta-repo/flathub-beta.flatpakrepo",
    "fedora": "oci+https://registry.fedoraproject.org",
    "gnome-nightly": "https://nightly.gnome.org/gnome-nightly.flatpakrepo",
    "elementary": "https://flatpak.elementary.io/repo.flatpakrepo",
    "rhel": "https://flatpaks.redhat.io/rhel.flatpakrepo"
}


class Flatpak(dotbot.Plugin):
    """
    Install Flatpak
    """

    _directive = "flatpak"
    _default_repo = "flathub"
    _default_reinstall = False

    def can_handle(self, directive: str) -> bool:
        return self._directive == directive

    def handle(self, directive: str, data: FlatpakSettings) -> bool:
        if not self.can_handle(directive):
            raise ValueError(f"flatpak cannot handle directive {directive}")

        self._get_defaults()
        success = True
        for key, settings in data.items():
            if key == "repos":
                success = success and self._handle_repos(settings)
            elif key == "apps":
                success = success and self._handle_apps(settings)
            else:
                self._log.warn(f"Invalid option: '{key}' is being ignored.")

        if success:
            self._log.info("All flatpak repos and apps have been installed")
        else:
            self._log.error("Not all flatpak repos and apps were successfully installed")

        return success


    def _get_defaults(self) -> None:
        """
        Gets the flatpak specific defaults from context.
        """
        defaults = self._context.defaults().get("flatpak", {})
        if "repo" in defaults:
            self._default_repo = defaults["repo"]
        if "reinstall" in defaults:
            self._default_reinstall = defaults["reinstall"]


    def _handle_repos(self, settings: List[Setting]) -> bool:
        """
        Add flatpak repositories
        """

        success = True
        for setting in settings:
            repo: Repo

            if isinstance(setting, str) and setting in KNOWN_REPOS:
                repo = Repo(setting, KNOWN_REPOS[setting])
            elif isinstance(setting, dict) \
                    and "name" in setting and "url" in setting \
                    and isinstance(setting["name"], str) \
                    and isinstance(setting["url"], str):
                repo = Repo(setting["name"], setting["url"])
            else:
                self._log.warn(f"Unknown repo '{setting}' is being ignored.")
                continue

            try:
                subprocess.run(
                    ["flatpak", "remote-add", "--if-not-exists", repo.name, repo.url], 
                    check=True
                )
            except subprocess.CalledProcessError:
                self._log.error(f"{repo[0]} was not added successfully")
                success = False
        return success


    def _handle_apps(self, settings: List[Setting]) -> bool:
        """
        Install flatpak apps
        """
        success = True
        for setting in settings:
            app: App

            if isinstance(setting, str):
                app = App(setting, self._default_repo, self._default_reinstall)
            elif isinstance(setting, dict) \
                    and "name" in setting and isinstance(setting["name"], str):
                app = App(
                    setting["name"],
                    str(setting.get("repo", self._default_repo)),
                    bool(setting.get("reinstall", self._default_reinstall))
                )
            else:
                self._log.warn(f"Invalid app '{setting}' is being ignored")
                continue

            try:
                parts = [
                    "flatpak",
                    "install",
                    "--noninteractive",
                    "--reinstall" if app.reinstall else None,
                    app.repo,
                    app.name
                ]
                subprocess.run([
                        part
                        for part in parts
                        if part is not None
                    ], 
                    check=True
                )
            except subprocess.CalledProcessError:
                success = False 
        return success
