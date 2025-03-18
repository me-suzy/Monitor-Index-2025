import urllib.request
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import shutil
import sys
import os

def main():
    try:
        # 1) Accesăm index.html local
        url = r"file:///e:/Carte/BB/17 - Site Leadership/Principal/ro/index.html"
        response = urllib.request.urlopen(url)
        html_content = response.read().decode('utf-8', errors='ignore')

        # 2) Identificăm link-ul ultimului articol
        pattern = r'<td><span class="den_articol"><a href="([^"]+)" class="linkMare">'
        match = re.search(pattern, html_content)
        if not match:
            print("Nu s-a găsit un link conform cerinței în index.html.")
            sys.exit(0)

        link_url = match.group(1)
        print("Link-ul identificat este:", link_url)

        # 3) Accesăm DOAR fișierul local, ignorând link-ul online
        filename = link_url.split('/')[-1]
        local_path = r"e:/Carte/BB/17 - Site Leadership/Principal/ro/" + filename
        print(f"Citim fișierul local: {local_path}")

        try:
            with open(local_path, 'r', encoding='utf-8', errors='ignore') as file:
                link_content = file.read()
            print("Fișierul local a fost citit cu succes.")
        except Exception as e:
            print(f"Eroare la citirea fișierului local: {e}")
            sys.exit(1)

        # 4) Extragem <title> și <link rel="canonical"> folosind regex
        title_match = re.search(r'<title[^>]*>(.*?)</title>', link_content)
        title = title_match.group(1) if title_match else "Fără titlu"

        canonical_match = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"[^>]*>', link_content)
        canonical = canonical_match.group(1) if canonical_match else link_url

        # 5) Afișăm primele 500 de caractere pentru debugging
        print("Primele 500 caractere din conținutul fișierului local:")
        print(link_content[:500])

        # Încercăm să găsim data direct, folosind un pattern mai general
        date_pattern = r'(On\s+\w+\s+\d{1,2},\s+\d{4})'
        date_match = re.search(date_pattern, link_content)

        if date_match:
            date_info = date_match.group(1)
            print(f"S-a extras data: {date_info}")

            # Încercăm să găsim autorul în apropiere
            # Căutăm în jurul datei
            surrounding_text = link_content[max(0, date_match.start() - 100):min(len(link_content), date_match.end() + 200)]
            author_pattern = r'by\s+([\w\s]+)'
            author_match = re.search(author_pattern, surrounding_text)

            if author_match:
                author_info = author_match.group(1).strip()
            else:
                author_info = "Neculai Fantanaru"

            date_author_info = f"{date_info}, by {author_info}"
            print(f"Informații complete extrase: {date_author_info}")
        else:
            print("Nu s-a găsit formatul de dată în conținutul fișierului local.")

            # Verificăm dacă există alte formate de dată
            alt_patterns = [
                r'(\d{1,2}\s+\w+\s+\d{4})',  # Format: 18 Martie 2025
                r'(\w+\s+\d{1,2},\s+\d{4})',  # Format: Martie 18, 2025
                r'(\d{1,2}\.\d{2}\.\d{4})'    # Format: 18.03.2025
            ]

            for pattern in alt_patterns:
                alt_match = re.search(pattern, link_content)
                if alt_match:
                    print(f"S-a găsit o dată în format alternativ: {alt_match.group(1)}")
                    # Reformatăm data găsită în formatul "On Martie X, YYYY"
                    months = {
                        "ianuarie": "Ianuarie", "februarie": "Februarie", "martie": "Martie",
                        "aprilie": "Aprilie", "mai": "Mai", "iunie": "Iunie",
                        "iulie": "Iulie", "august": "August", "septembrie": "Septembrie",
                        "octombrie": "Octombrie", "noiembrie": "Noiembrie", "decembrie": "Decembrie"
                    }
                    # Aici ar fi logica de conversie a formatului, dar e complexă și depinde de formatul exact găsit
                    break

            # Abandonăm execuția dacă nu găsim o dată validă
            print("Nu se poate continua fără o dată validă.")
            sys.exit(1)

        # 6) Extragem conținutul articolului
        article_pattern = r'<!-- ARTICOL START -->([\s\S]*?)<!-- ARTICOL FINAL -->'
        article_match = re.search(article_pattern, link_content)
        if not article_match:
            print("Nu s-a găsit conținutul articolului (ARTICOL START / ARTICOL FINAL).")
            sys.exit(0)

        article_content = article_match.group(1)

        # 7) Eliminăm tabelul cu titlu și informații din conținutul articolului
        table_pattern = r'<table[^>]*>.*?</table>'
        article_content = re.sub(table_pattern, '', article_content, count=1, flags=re.DOTALL)
        print("S-a eliminat tabelul cu titlu și informații autor din articol.")

        # 8) Formatăm paragrafele conform cerințelor:
        # - <p class="text_obisnuit2"> devine <strong>
        # - <span class="text_obisnuit2"> devine <strong>
        # - <p class="text_obisnuit"> rămâne normal
        # - <em> rămâne italic

        # Înlocuim paragrafele text_obisnuit2 cu <strong>
        # h3 class="text_obisnuit2" => <p style="font-weight: bold; color: #000; font-size:14px;">...</p>
        article_content = re.sub(
            r'<h3 class="text_obisnuit2">(.*?)</h3>',
            r'<p style="font-weight: bold; color: #000; font-size:12px;">\1</p>',
            article_content,
            flags=re.DOTALL
        )

        # p class="text_obisnuit2" => <p style="font-weight: bold; color: #000; font-size:14px;">...</p>
        article_content = re.sub(
            r'<p class="text_obisnuit2">(.*?)</p>',
            r'<p style="font-weight: bold; color: #000; font-size:12px;">\1</p>',
            article_content,
            flags=re.DOTALL
        )

        # H2 class="text_obisnuit2" => <p style="font-weight: bold; color: #000; font-size:14px;">...</p>
        article_content = re.sub(
            r'<h2 class="text_obisnuit2">(.*?)</p>',
            r'<p style="font-weight: bold; color: #000; font-size:12px;">\1</p>',
            article_content,
            flags=re.DOTALL
        )

        # span class="text_obisnuit2" => <span style="font-weight: bold; color: #000;">...</span>
        article_content = re.sub(
            r'<span class="text_obisnuit2">(.*?)</span>',
            r'<span style="font-weight: bold; color: #000; font-size:12px;">\1</span>',
            article_content,
            flags=re.DOTALL
        )

        # p class="text_obisnuit" => <p>...</p>
        article_content = re.sub(
            r'<p class="text_obisnuit">(.*?)</p>',
            r'<p>\1</p>',
            article_content,
            flags=re.DOTALL
        )

        # 9) Pregătim fișierele de backup și original (online.html)
        backup_path = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\MAIL TEXT\online_backup.html"
        original_path = r"e:\Carte\BB\17 - Site Leadership\alte\Ionel Balauta\Aryeht\Task 1 - Traduce tot site-ul\Doar Google Web\Andreea\Meditatii\2023\MAIL TEXT\online.html"

        # Creăm backup
        shutil.copy2(original_path, backup_path)

        try:
            # 10) Citim conținutul online.html
            with open(original_path, "r", encoding='utf-8') as file:
                online_html = file.read()

            # Curățăm titlul de sufixul " | Neculai Fantanaru" (dacă există)
            clean_title = title.replace(" | Neculai Fantanaru", "").strip()

            # 11) Modificăm header-ul pentru a include data și autorul sub titlu

            # Căutăm pattern-ul pentru titlu în șablon
            title_pattern = r'<a href="LINK-CANONICAL"[^>]*><strong>TITLU-ARTICOL</strong></a>'
            title_author_replacement = f'<a href="LINK-CANONICAL" style="color: #2585b2;"><strong>{clean_title}</strong></a></h3><div style="color: #5A5A5A; font-size: 13px; margin-top: 5px;">📅 {date_author_info}</div>'

            if re.search(title_pattern, online_html):
                # Înlocuim titlul cu titlul urmat de data și autor
                online_html = re.sub(title_pattern, title_author_replacement, online_html)
                print("S-a adăugat data și autorul sub titlu")

                # Eliminăm linia "by Neculai Fantanaru" din header (dacă există)
                online_html = re.sub(r'by\s*<a[^>]*>Neculai Fantanaru</a>', '', online_html)
                print("S-a eliminat linia 'by Neculai Fantanaru' din header")
            else:
                print("Nu s-a putut găsi pattern-ul pentru titlu în șablon")

            # 12) Înlocuim placeholder-ele din online.html
            replacements = {
                "TITLU-ARTICOL": clean_title,
                "LINK-CANONICAL": canonical,
                "COMENTARIU-BUTON": canonical,
                "COMENTARIU-LINK": canonical,
                "ARTICOL-BEBE": article_content
            }
            for old, new in replacements.items():
                online_html = online_html.replace(old, new)

            # 13) Adăugăm CSS pentru a asigura formatarea corectă a textului în email
            css_style = """
            <style type="text/css">
                p { font-family: Arial, Helvetica, sans-serif; font-size: 14px; line-height: 1.6; margin-bottom: 15px; }
                strong { font-weight: bold; }
                em { font-style: italic; }
            </style>
            """

            # Adăugăm CSS înainte de </head>
            online_html = online_html.replace('</head>', css_style + '</head>')

            # 14) Salvăm fișierul final
            with open(r"c:\Folder8\debug_online.html", "w", encoding='utf-8') as dbg:
                dbg.write(online_html)
                print("HTML salvat pentru debugging la c:\\Folder8\\debug_online.html")

            with open(r"c:\Folder8\online.html", "w", encoding='utf-8') as f:
                f.write(online_html)

            # 15) Trimitem email cu versiunea finală
            sender_email = 'ioan.fantanaru@gmail.com'
            sender_password = 'PASS'  # Înlocuiește cu parola corectă
            receiver_emails = ['neculai.fantanaru@gmail.com', 'me.suzana@gmail.com']

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = ', '.join(receiver_emails)
            message['Subject'] = title
            message.attach(MIMEText(online_html, 'html'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender_email, sender_password)
                smtp_server.send_message(message)

            print("Email trimis cu succes!")

        finally:
            # 16) Restaurăm fișierul original (online.html) din backup
            shutil.copy2(backup_path, original_path)
            print("Fișierul online.html a fost restaurat din backup!")

    except Exception as e:
        print(f"A apărut o eroare: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Configurare pentru output cu encoding UTF-8
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except Exception as e:
        print(f"A aparut o eroare: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        sys.exit(0)  # Asigură închiderea programului după executare