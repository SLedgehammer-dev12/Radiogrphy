import json
import os
import platform
import socket
import ssl
import sys
import tempfile
import threading
import urllib.request
import urllib.error

from src.core.version import __version__ as _version

GITHUB_REPO = "SLedgehammer-dev12/Radiography"
CURRENT_VERSION = _version


def _ssl_context():
    """
    Builds an SSL context with an explicit CA bundle.
    Packaged (PyInstaller) builds on Windows cannot always resolve the
    default OpenSSL CA bundle. certifi ships a self-contained cacert.pem.
    """
    try:
        import certifi
        cafile = certifi.where()
        if os.path.exists(cafile):
            return ssl.create_default_context(cafile=cafile)
    except Exception:
        pass
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()


def _open_url_with_fallback(req, timeout=10):
    """
    Tries to open URL with secure SSL context first; if an SSL certificate
    verification failure occurs on packaged Windows/embedded runtimes,
    falls back to an unverified context so update checks never fail silently.
    """
    ctx = _ssl_context()
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)
    except (ssl.SSLError, ssl.CertificateError, urllib.error.URLError) as e:
        err_msg = str(e).lower()
        if isinstance(e, ssl.SSLError) or "certificate" in err_msg or "ssl" in err_msg or "verify failed" in err_msg:
            try:
                unverified_ctx = ssl._create_unverified_context()
                return urllib.request.urlopen(req, timeout=timeout, context=unverified_ctx)
            except Exception:
                raise e
        raise e


class UpdateChecker:
    def __init__(self, repo=GITHUB_REPO, current_version=CURRENT_VERSION):
        self.repo = repo
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _parse_version(self, tag):
        v = tag.lstrip("vV")
        parts = v.split(".")
        return tuple(int(p) if p.isdigit() else 0 for p in parts)

    def check(self):
        try:
            req = urllib.request.Request(
                self.api_url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "Radiography-Updater/1.0"
                }
            )
            with _open_url_with_fallback(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"available": False, "error": str(e), "data": None}

        tag = data.get("tag_name", "")
        latest_ver = self._parse_version(tag)
        current_ver = self._parse_version(self.current_version)

        if latest_ver > current_ver:
            return {
                "available": True,
                "version": tag,
                "url": data.get("html_url", ""),
                "release_notes": data.get("body", ""),
                "assets": data.get("assets", []),
            }
        return {"available": False, "error": None, "data": data}

    def get_download_url(self, release_data):
        system = platform.system().lower()
        assets = release_data.get("assets", []) if release_data else []
        for asset in assets:
            name = asset.get("name", "")
            if system in ("windows", "win32") and name.endswith(".exe"):
                return asset.get("browser_download_url")
            elif system in ("darwin", "mac", "macos") and name.endswith(".dmg"):
                return asset.get("browser_download_url")
            elif ("android" in system or system == "linux") and name.endswith(".apk"):
                return asset.get("browser_download_url")
        # Generic fallback
        for asset in assets:
            name = asset.get("name", "")
            if system in ("windows", "win32") and ".exe" in name:
                return asset.get("browser_download_url")
            elif system in ("darwin", "mac", "macos") and ".dmg" in name:
                return asset.get("browser_download_url")
        return None

    def download_update(self, url, progress_callback=None):
        self._cancel = False
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Radiography-Updater/1.0"})
            with _open_url_with_fallback(req, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 8192
                system = platform.system().lower()
                if system in ("windows", "win32"):
                    suffix = ".exe"
                elif system in ("darwin", "mac", "macos"):
                    suffix = ".dmg"
                elif "android" in system or url.endswith(".apk"):
                    suffix = ".apk"
                else:
                    suffix = ".bin"
                fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="Radiography_")
                try:
                    with os.fdopen(fd, "wb") as f:
                        while not self._cancel:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total > 0:
                                progress_callback(downloaded / total)
                except Exception:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    raise
                if self._cancel:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    return None
                return tmp_path
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")

    def launch_installer(self, filepath):
        system = platform.system().lower()
        try:
            if system in ("windows", "win32"):
                os.startfile(filepath)
            elif system in ("darwin", "mac", "macos"):
                import subprocess
                subprocess.Popen(["open", filepath])
            elif "android" in system:
                import webbrowser
                webbrowser.open(filepath)
        except Exception as e:
            raise RuntimeError(f"Failed to launch installer: {e}")


def compare_versions(v1, v2):
    p1 = [int(x) if x.isdigit() else 0 for x in v1.lstrip("vV").split(".")]
    p2 = [int(x) if x.isdigit() else 0 for x in v2.lstrip("vV").split(".")]
    return (p1 > p2) - (p1 < p2)
