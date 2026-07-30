"""
Script opcional para re-intentar URLs que dieron 406 en Node.js fetch.
Usa requests con headers más completos y rotación de User-Agent.
Uso: python retry_406_urls.py
"""
import json
import re
import subprocess
import sys
import urllib.request
import urllib.error
from html.parser import HTMLParser

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?51[\s\-]?)?(9\d{8}|\d{7,8})")


def extract_phones(text):
    return list(set(m.group(0) for m in PHONE_RE.finditer(text)))


def extract_emails(text):
    raw = list(set(m.group(0).lower() for m in EMAIL_RE.finditer(text)))
    validos = []
    for e in raw:
        local, dominio = e.split("@", 1)
        tld = dominio.rsplit(".", 1)[-1]
        if len(tld) < 2 or len(dominio) < 4:
            continue
        if dominio in ("example.com", "domain.com", "test.com"):
            continue
        if local in ("elcorreoquequieres", "tuemail", "tucorreo", "example", "test"):
            continue
        validos.append(e)
    return validos


def fetch_url(url):
    headers = {
        "User-Agent": USER_AGENTS[0],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            return {"status": resp.status, "html": html}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "html": ""}
    except Exception as e:
        return {"status": "ERR", "error": str(e), "html": ""}


def actualizar_bd(web, telefono, correos):
    if not telefono and not correos:
        return
    tel_str = " | ".join(telefono[:3]) if telefono else ""
    corr_str = " | ".join(correos[:5]) if correos else ""
    script = (
        "const D=require('better-sqlite3');"
        "const d=new D('contactos.db');"
        "d.prepare('UPDATE negocios SET telefono_web = ?, correo = ? "
        "WHERE web = ? AND (telefono_web = \"\" OR telefono_web = \"—\") "
        "AND (correo = \"\" OR correo = \"—\")').run(process.argv[2], process.argv[3], process.argv[4]);"
        "d.close();"
    )
    subprocess.run(["node", "-e", script, "--", tel_str, corr_str, web], cwd=".")


def main():
    # Leer URLs desde la BD via Node
    result = subprocess.run(
        [
            "node",
            "-e",
            "const D=require('better-sqlite3');const d=new D('contactos.db');const r=d.prepare('SELECT DISTINCT web FROM negocios WHERE web!=\"\" AND web!=\"—\"').all();console.log(JSON.stringify(r.map(x=>x.web)));d.close();",
        ],
        capture_output=True,
        text=True,
        cwd=".",
    )
    urls = json.loads(result.stdout.strip())

    for url in urls:
        if not url.startswith("http"):
            continue
        print(f"\n--- {url}")
        result = fetch_url(url)
        if result["status"] == 406:
            # Reintentar con otro UA
            for ua in USER_AGENTS[1:]:
                h = {
                    "User-Agent": ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
                }
                req = urllib.request.Request(url, headers=h)
                try:
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        html = resp.read().decode("utf-8", errors="replace")
                        phones = extract_phones(html)
                        emails = extract_emails(html)
                        print(f"  OK con UA {ua}")
                        if phones:
                            print(f"  Teléfonos: {phones}")
                        if emails:
                            print(f"  Correos: {emails}")
                        actualizar_bd(url, phones, emails)
                        break
                except Exception:
                    continue
            else:
                print(f"  Sigue dando 406 después de reintentos")
        elif result["status"] == 200:
            html = result["html"]
            phones = extract_phones(html)
            emails = extract_emails(html)
            print(f"  Status: 200, longitud: {len(html)}")
            if phones:
                print(f"  Teléfonos: {phones[:3]}")
            if emails:
                print(f"  Correos: {emails[:3]}")
            actualizar_bd(url, phones, emails)
        else:
            print(f"  Status: {result['status']}")

    print("\nListo.")


if __name__ == "__main__":
    main()
