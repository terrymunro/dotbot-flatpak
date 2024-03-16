# Dotbot `flatpak` plugin

Plugin for [dotbot](https://github.com/anishathalye/dotbot) that adds a flatpak directive, to allow you to install flatpak packages and configure flathub and other repositories.


## Installation

Add it as a submodule of your dotfiles repository.

```sh
git submodule add https://github.com/terrymunro/dotbot-flatpak.git
```

Modify your `install` script, to enable the plugin.

```sh
"${BASEDIR}/${DOTBOT_DIR}/${DOTBOT_BIN}" \
    -p dotbot-flatpak/flatpak.py \
    -d "${BASEDIR}" \
    -c "${CONFIG}" \
    "${@}"
```

## Usage

### Full example

```yaml
- defaults:
    flatpak:
        repo: flathub           # Default repository that will be used for apps
        reinstall: false        # Default for reinstall or if-not-exists

# Every setting is optional
- flatpak:
    repos:                      # Enable various repositories
        - flathub
        - fedora
        - name: flathub-beta
          url: https://flathub.org/beta-repo/flathub-beta.flatpakrepo
        - name: elementary
          url: https://flatpak.elementary.io/repo.flatpakrepo
    apps:                       # Flatpak apps to install
        - com.slack.Slack
        - org.telegram.desktop
        - name: com.discordapp.Discord
          repo: flathub
        - name: io.elementary.calendar
          repo: appcenter-elementary
        - name: com.spotify.Client
          reinstall: true
```

### Minimal example

```yaml
- flatpak:
    apps:
        - com.slack.Slack
        - org.telegram.desktop
        - com.discordapp.Discord
```
