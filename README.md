# OpenTV installer distribution

GitHub Pages publishes the compiled installer, its corresponding source archive and the GPL licence
so that the Downloader app can retrieve the APK without exposing a home IP address or credentials.

`verify_distribution.py` is a mandatory pre-publish guard: it rejects the plain `app.opentv`
variant and verifies that the upgrade-compatible `app.opentv.stremiolab` APK contains the complete
bundled playlist, guide and folder indexes.

The internal package identifier is retained solely for in-place upgrade compatibility. The installed
application name and displayed version are `OpenTV` and `0.13.17`.

The optional Tribler integration is a REST client for a user-owned Tribler 8 core. Tribler itself is
not bundled; configure its address, API key and anonymous-hop preference under Settings → Tribler.
