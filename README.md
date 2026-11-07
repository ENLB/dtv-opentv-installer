# OpenTV installer distribution

GitHub Pages publishes the compiled installer, its corresponding source archive and the GPL licence
so that the Downloader app can retrieve the APK without exposing a home IP address or credentials.

`verify_distribution.py` is a mandatory pre-publish guard: it rejects the plain `app.opentv`
variant and verifies that the upgrade-compatible `app.opentv.stremiolab` APK contains the complete
bundled playlist, guide and folder indexes.

The internal package identifier is retained solely for in-place upgrade compatibility. The installed
application name and displayed version are `OpenTV` and `0.13.18`.

P2P transport is embedded using FrostWire jlibtorrent 2.0.15.3 (MIT). Add-on magnet and info-hash
results therefore play on the Android device without a computer or external player. This transport
does not claim Tribler's anonymity or community/search features. Android 8.0 or newer is required.
