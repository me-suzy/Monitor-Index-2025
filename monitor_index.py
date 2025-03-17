import urllib.request
import re
import http.client
from urllib.parse import urlparse
import sys
from subprocess import run

# Set console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def is_link_online(url):
    """Verifică dacă link-ul este accesibil online"""
    try:
        parsed_url = urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=10)
        conn.request("HEAD", parsed_url.path)
        response = conn.getresponse()
        conn.close()

        # Dacă status code este sub 400, link-ul există
        return response.status < 400
    except Exception as e:
        print(f"Eroare la verificarea link-ului {url}: {e}")
        return False

def get_current_link():
    """Preia ultimul link din pagina index.html"""
    try:
        # Accesăm pagina index.html
        index_file_path = r"file:///e:/Carte/BB/17 - Site Leadership/Principal/ro/index.html"
        with urllib.request.urlopen(index_file_path) as response:
            html_content = response.read().decode('utf-8')

        # Căutăm link-ul
        pattern = r'<td><span class="den_articol"><a href="([^"]+)" class="linkMare">'
        match = re.search(pattern, html_content)

        if match:
            return match.group(1)
        else:
            print("Nu s-a găsit niciun link în index.html")
            return None
    except Exception as e:
        print(f"Eroare la obținerea link-ului: {e}")
        return None

def run_perfecto():
    """Rulează scriptul PERFECTO pentru trimiterea email-ului"""
    try:
        print("Se execută scriptul PERFECTO-2-Gmail.py...")
        result = run(['python', 'PERFECTO-2-Gmail.py'],
                     check=True,
                     text=True,
                     capture_output=True)

        if "Email trimis cu succes!" in result.stdout:
            print("✓ Email trimis cu succes!")
            return True
        else:
            print("✗ Script executat, dar fără confirmare de email.")
            print(f"Output: {result.stdout}")
            return False
    except Exception as e:
        print(f"✗ Eroare la rularea scriptului PERFECTO: {e}")
        return False

# Funcția principală
def main():
    print("\n=== VERIFICARE ARTICOL ONLINE ===")

    # Obținem link-ul din index.html
    link = get_current_link()
    if not link:
        return

    print(f"Link-ul găsit în index.html: {link}")

    # Verificăm dacă link-ul există online
    exists_online = is_link_online(link)
    print(f"Link-ul există online: {'DA' if exists_online else 'NU'}")

    # Dacă link-ul nu există online, rulăm PERFECTO
    if not exists_online:
        print("\nArticolul există doar local și nu este publicat online!")
        print("Se procedează la trimiterea prin email...")

        # Actualizăm fișierul link-actual.txt cu noul link
        try:
            with open("link-actual.txt", "r", encoding="utf-8") as file:
                existing_links = file.read().splitlines()
        except:
            existing_links = []

        if link not in existing_links:
            with open("link-actual.txt", "w", encoding="utf-8") as file:
                file.write(link + "\n" + "\n".join(existing_links))

        # Rulăm PERFECTO pentru a trimite email
        run_perfecto()
    else:
        print("\nArticolul există deja online. Nu este necesară nicio acțiune.")

if __name__ == "__main__":
    main()