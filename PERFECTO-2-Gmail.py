import urllib.request
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import shutil
import sys

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
        print("Link-ul deschis este:", link_url)

        # 3) Accesăm link-ul articolului online sau local
        try:
            response = urllib.request.urlopen(link_url)
            link_content = response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Eroare la accesarea link-ului online: {e}")
            filename = link_url.split('/')[-1]
            local_path = r"e:/Carte/BB/17 - Site Leadership/Principal/ro/" + filename
            print(f"Încercăm să citim fișierul local: {local_path}")
            with open(local_path, 'r', encoding='utf-8', errors='ignore') as file:
                link_content = file.read()

        # 4) Extragem <title> și <link rel="canonical"> folosind regex
        title_match = re.search(r'<title[^>]*>(.*?)</title>', link_content)
        title = title_match.group(1) if title_match else "Fără titlu"

        canonical_match = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"[^>]*>', link_content)
        canonical = canonical_match.group(1) if canonical_match else link_url

        # 5) Extragem conținutul dintre <!-- ARTICOL START --> și <!-- ARTICOL FINAL -->
        article_pattern = r'<!-- ARTICOL START -->([\s\S]*?)<!-- ARTICOL FINAL -->'
        article_match = re.search(article_pattern, link_content)
        if not article_match:
            print("Nu s-a găsit conținutul articolului (ARTICOL START / ARTICOL FINAL).")
            sys.exit(0)

        article_content = article_match.group(1)

        # 6) Extragem data și autorul din conținutul articolului
        date_author_pattern = r'<td class="text_dreapta">(.*?)</td>'
        date_author_match = re.search(date_author_pattern, article_content)
        date_author_info = ""
        if date_author_match:
            date_author_info = date_author_match.group(1)
            print(f"S-au extras informațiile despre dată și autor: {date_author_info}")
        else:
            # Dacă nu găsim informațiile, folosim un text default
            date_author_info = "On Martie 13, 2025, by Neculai Fantanaru"
            print("Nu s-au găsit informații despre dată și autor, se folosește textul default")

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
        article_content = re.sub(
            r'<p class="text_obisnuit2">(.*?)</p>',
            r'<p><strong>\1</strong></p>',
            article_content,
            flags=re.DOTALL
        )

        # Înlocuim span-urile text_obisnuit2 din interiorul paragrafelor cu <strong>
        article_content = re.sub(
            r'<span class="text_obisnuit2">(.*?)</span>',
            r'<strong>\1</strong>',
            article_content,
            flags=re.DOTALL
        )

        # Înlocuim paragrafele text_obisnuit cu <p> normal
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
            sender_email = 'YOUR-EMAIL@gmail.com'
            sender_password = 'PASS'            #  VECHE  'iwpd jzqa wwpp jgxs'  #  NU E PAROLA TA ORIGINALA In the "Two-step authentication" section
            receiver_emails = ['other-email@gmail.com', 'other-email@gmail.com']

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