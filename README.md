# D TV OpenTV installer distribution

The repository is private. GitHub Pages publishes only the compiled household installer, its
corresponding source archive and the GPL licence so that the Downloader app can retrieve the APK
without exposing a home IP address or any credentials.

`verify_distribution.py` is a mandatory pre-publish guard: it rejects the plain `app.opentv`
variant and verifies that the upgrade-compatible `app.opentv.stremiolab` APK contains the complete
bundled playlist, guide and folder indexes.
