# Linux

:warning: To play on GNU/Linux, you have to run the server from source.

There are two ways to play:

- **Option A (easier):** Firefox with the Ruffle extension (see [Playing with Ruffle and Firefox](#playing-with-ruffle-and-firefox) section). No old browser or Flash Player needed.
- **Option B:** A Chromium browser with PPAPI Flash support and Adobe Flash Player (see [Flash Chromium browser](#flash-chromium-browser) and [Flash Player for Linux Pepper](#flash-player-for-linux-pepper) sections).

## Running the server from source

```sh
git clone https://github.com/AcidCaos/socialwarriors.git
cd socialwarriors
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

Keep the terminal open while playing. The server listens on `http://127.0.0.1:5055/` by default.

## Playing with Ruffle and Firefox

[Ruffle](https://ruffle.rs/) is an open source Flash Player emulator.

1. Install Firefox.
2. Install the [Ruffle extension for Firefox](https://addons.mozilla.org/firefox/addon/ruffle_rs/).
3. Start the server (see [Running the server from source](#running-the-server-from-source)).
4. Open `http://127.0.0.1:5055/` in Firefox.

## Playing with Chromium and Flash Player

You will need:

- A browser with Flash support (see [Flash Chromium browser](#flash-chromium-browser) section).
- Adobe Flash Player installed (see [Flash Player for Linux Pepper](#flash-player-for-linux-pepper) section).

## Flash Chromium browser

Download a Chromium version with PPAPI support.
<br>Tested with version *86.0.4240.75*, which can be downloaded [here](https://chromium.cypress.io/linux/stable/86.0.4240.75).

Fancy trying other versions? Here are some relevant Linux Chromium release comments:

| Version | Date | Comment |
| --- | --- | --- |
| 54.0.2840 | October 2016 | The message "Right-click to play Adobe Flash Player" now appears<br>while pages with Adobe Flash Player are loading. |
| 56.0.2924 | January 2017 | Adobe Flash Player is automatically blocked for most sites that<br>require the plugin. |
| 87.0.4280 | November 2020 | Flash Player end of support notifications now displaying at every<br>launch unless Flash is disabled. |

## Flash Player for Linux Pepper

Download `flashplayer32_0r0_371_linuxpep.x86_64.tar.gz` from the [32.0.0.371 archive](https://archive.org/download/flashplayerarchive/pub/flashplayer/installers/archive/fp_32.0.0.371_archive.zip/).
<br>For 32-bit, download `flashplayer32_0r0_371_linuxpep.i386.tar.gz`.

Extract its contents to `/usr/lib/adobe-flashplugin`

## Running Chromium with PPAPI Flash

Run the chrome binary with `--ppapi-flash-path=/usr/lib/adobe-flashplugin/libpepflashplayer.so`
<br>and `--ppapi-flash-version=32.0.0.371` flags.

*Note:* To avoid providing those flags every time, you might want to set `CHROMIUM_FLAGS`.
