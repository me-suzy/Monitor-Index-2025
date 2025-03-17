# Explicație Detaliată a Sistemului Monitor-Index-2025

Acest proiect conține două scripturi Python care lucrează împreună pentru a monitoriza și procesa automat articole noi de pe un site web.

## 1. `monitor_index.py`

Acest script verifică dacă există articole noi în pagina locală de index și, dacă acestea nu sunt încă publicate online, trimite o notificare prin email.

### Funcționalități principale:

- **`is_link_online(url)`**: Verifică dacă un URL este accesibil online făcând o cerere HTTP HEAD și verificând codul de răspuns.
- **`get_current_link()`**: Extrage link-ul celui mai recent articol din fișierul index.html local.
- **`run_perfecto()`**: Execută scriptul PERFECTO-2-Gmail.py care formatează și trimite conținutul articolului prin email.
- **`main()`**: Funcția principală care coordonează procesul:
  1. Obține link-ul celui mai recent articol din index.html
  2. Verifică dacă link-ul există online
  3. Dacă articolul nu există online, actualizează lista de link-uri din fișierul link-actual.txt și rulează PERFECTO pentru a trimite email

## 2. `PERFECTO-2-Gmail.py`

Acest script procesează conținutul articolului, formatează corespunzător și trimite prin email.

### Funcționalități principale:

1. **Extragerea conținutului**:
   - Accesează fișierul index.html pentru a găsi link-ul ultimului articol
   - Încearcă să acceseze link-ul online; dacă nu reușește, accesează versiunea locală
   - Extrage titlul și link-ul canonical din HTML
   - Extrage conținutul dintre marcatorii `<!-- ARTICOL START -->` și `<!-- ARTICOL FINAL -->`
   - Extrage informații despre dată și autor

2. **Procesarea conținutului**:
   - Elimină tabelul care conține titlul și informațiile despre autor din conținutul articolului
   - Formatează paragrafele conform cerințelor specifice:
     - `<p class="text_obisnuit2">` devine `<p><strong>...</strong></p>` (text bold)
     - `<span class="text_obisnuit2">` devine `<strong>...</strong>` (text bold)
     - `<p class="text_obisnuit">` devine `<p>...</p>` (text normal)
     - `<em>` rămâne italic

3. **Pregătirea și trimiterea email-ului**:
   - Citește șablonul HTML din fișierul online.html
   - Modifică header-ul pentru a include titlul și informațiile despre dată și autor
   - Înlocuiește placeholder-ele din șablon cu conținutul procesat
   - Adaugă CSS pentru formatarea corectă în email
   - Trimite email-ul folosind SMTP

### Detalii tehnice importante:

- **Manipulare HTML**: Scriptul folosește expresii regex pentru a manipula conținutul HTML
- **Formatare specială**: Include formatare specială pentru textele bold și italice
- **Gestionare codificare**: Configurează UTF-8 pentru a gestiona corect diacriticele românești
- **Backup și restaurare**: Creează un backup al fișierului original și îl restaurează după procesare

## Flux de lucru complet:

1. Scriptul `monitor_index.py` este rulat (manual sau prin programare)
2. Verifică dacă există un articol nou în index.html care nu este încă online
3. Dacă găsește un astfel de articol, execută `PERFECTO-2-Gmail.py`
4. `PERFECTO-2-Gmail.py` extrage conținutul articolului, îl formatează și trimite prin email
5. Email-ul trimis conține:
   - Titlul articolului lângă sigla L, cu formatare albastră
   - Data și autorul sub titlu, cu iconița de calendar
   - Conținutul articolului formatat corespunzător (paragrafe normale, text bold, text italic)

## Utilizare:

Pentru a utiliza sistemul:
1. Asigură-te că toate fișierele sunt în același director
2. Configurează calea către fișierele locale și credențialele pentru email
3. Rulează `monitor_index.py` pentru a verifica și procesa articole noi

Acest sistem automatizează procesul de detectare și notificare pentru articole noi, permițând trimiterea lor prin email înainte de a fi publicate online.
