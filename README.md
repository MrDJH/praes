# Offlinefähige reveal.js-Präsentationsbibliothek

Eine statische Präsentationsbibliothek, die **lokal ohne Internetverbindung** betrieben und optional über GitHub Pages veröffentlicht werden kann.

## Eigenschaften

- Lokale reveal.js-Abhängigkeiten (nach einmaliger Installation).
- Keine CDN-, Google-Fonts- oder API-Aufrufe zur Laufzeit.
- Automatischer Katalog aus den Präsentationsordnern.
- Suche und Filterung nach Kategorie.
- Ein gemeinsamer Kataloggenerator für lokale Nutzung und Veröffentlichung.
- GitHub Pages kann den Ordner `docs/` direkt veröffentlichen.
- Lokaler Webserver bindet standardmäßig nur an `127.0.0.1`.

## Voraussetzungen

- Python 3.10 oder neuer (nur Standardbibliothek, keine `pip install`-Pakete nötig).
- Ein moderner Browser.
- Internetzugang **einmalig**, um reveal.js 6.0.2 herunterzuladen. Danach funktioniert die Bibliothek samt Präsentationen offline.

> Hinweis: Die ZIP-Datei dieses Starterprojekts enthält die Projektdateien. Die originale reveal.js-Distribution ist ein separates Drittanbieterpaket und wird aus Sicherheits- und Lizenzgründen über das mitgelieferte Installationsskript aus dem offiziellen Release bezogen. Ohne diesen einmaligen Schritt ist die Beispielpräsentation noch nicht startbereit.

## 1. reveal.js einmalig lokal installieren

Im entpackten Projektverzeichnis ausführen:

```bash
python tools/fetch_reveal.py
```

Das Skript lädt das fest konfigurierte Release `6.0.2` vom offiziellen reveal.js-GitHub-Repository, prüft die Paketversion und die benötigten Dateien und kopiert nur die Laufzeitdateien aus `dist/` nach `docs/vendor/reveal.js/dist/`.

Es wird kein Node.js und kein npm benötigt. Nach diesem Schritt ist reveal.js lokal gespeichert und für den Offlinebetrieb verfügbar.

Offizielle Release- und Installationsinformationen:

- https://github.com/hakimel/reveal.js/releases
- https://revealjs.com/installation/

## 2. Lokal starten

Im Projekt-Hauptverzeichnis:

```bash
python tools/serve.py
```

Im Browser öffnen:

http://127.0.0.1:8000

Beenden mit `Ctrl+C`.

Der Server bindet standardmäßig ausschließlich an `127.0.0.1`; andere Geräte im Netzwerk können ihn damit nicht erreichen. `file://` sollte nicht verwendet werden, weil die Startseite `catalog.json` per HTTP lädt.

Optionaler Port:

```bash
python tools/serve.py --port 8080
```

## 3. Neue Präsentation anlegen

Empfohlener Weg über das Hilfsskript:

```bash
python tools/new_presentation.py produktstrategie \
  --title "Produktstrategie" \
  --category "Strategie" \
  --description "Strategische Leitlinien und Prioritäten."
```

Unter Windows PowerShell kann der Befehl in einer Zeile eingegeben werden:

```powershell
python tools/new_presentation.py produktstrategie --title "Produktstrategie" --category "Strategie" --description "Strategische Leitlinien und Prioritäten."
```

Das Skript erstellt einen neuen Ordner unter `docs/presentations/` mit `index.html`, `meta.json` und einer lokalen Beispielgrafik. Anschließend `python tools/serve.py` erneut starten; der Katalog wird beim Start neu erzeugt.

Alternativ kannst du einen Präsentationsordner manuell anlegen. Er wird aufgenommen, sobald er einen gültigen Ordnernamen und eine `index.html` enthält. `meta.json` ist optional.

## 4. Katalog manuell aktualisieren / prüfen

```bash
python tools/build_catalog.py
```

Nur prüfen, ohne `catalog.json` zu verändern:

```bash
python tools/build_catalog.py --check
```

Der Katalog enthält nur Präsentationen mit einer `index.html`. Die Metadaten werden validiert. Fehlerhafte JSON-Dateien, ungültige Slugs oder ungültige Datumswerte führen zu einer verständlichen Fehlermeldung.

## 5. GitHub Pages veröffentlichen

1. Gesamten Projektordner als Git-Repository verwenden.
2. Alle gewünschten Dateien committen und zu GitHub pushen.
3. Im GitHub-Repository `Settings → Pages` öffnen.
4. Unter **Build and deployment** `Deploy from a branch` wählen.
5. Branch `main` und Ordner `/docs` auswählen.
6. Speichern.

Bevor du pushst, Katalog neu erstellen:

```bash
python tools/build_catalog.py
git add .
git commit -m "Präsentationen aktualisiert"
git push origin main
```

GitHub Pages veröffentlicht den Inhalt aus `docs/`. Die Links und Ressourcen sind relativ gehalten, damit sie lokal und unter einer GitHub-Pages-Projektadresse funktionieren.

## 6. Datenschutz und Veröffentlichung

GitHub Pages veröffentlicht die Dateien im `docs/`-Ordner öffentlich, sofern die Pages-Website öffentlich erreichbar ist. Lege keine vertraulichen oder personenbezogenen Inhalte in `docs/`, wenn sie nicht öffentlich zugänglich sein dürfen. Ein privates Repository macht eine veröffentlichte Pages-Seite nicht automatisch privat.

Keine GitHub-Tokens, Passwörter oder Zugangsdaten in dieses Repository eintragen.

## 7. Offline-Check

Nach erfolgreicher Installation von reveal.js:

1. `python tools/serve.py` starten.
2. Die Startseite und jede Präsentation einmal laden.
3. Internetverbindung trennen.
4. Seite neu laden und Folien, Suche, lokale Bilder und Navigation testen.

Verwende in Präsentationen ausschließlich lokale Ressourcen, wenn die Inhalte offline verfügbar bleiben müssen. Externe Weblinks sind zwar anklickbar, deren Ziele sind offline naturgemäß nicht erreichbar.

## Verzeichnisübersicht

```text
.
├── README.md
├── .gitignore
├── tools/
│   ├── build_catalog.py
│   ├── fetch_reveal.py
│   ├── new_presentation.py
│   └── serve.py
├── templates/presentation/
│   ├── index.html
│   ├── meta.json
│   └── media/thumbnail.svg
└── docs/                         # GitHub-Pages-Veröffentlichungsordner
    ├── .nojekyll
    ├── index.html
    ├── catalog.json
    ├── assets/
    │   ├── css/style.css
    │   └── js/app.js
    ├── vendor/reveal.js/         # wird durch fetch_reveal.py befüllt
    └── presentations/demo/
        ├── index.html
        ├── meta.json
        └── media/thumbnail.svg
```

## Lizenzhinweise

Die Dateien dieses Starterprojekts werden ohne zusätzliche externe Laufzeit-Abhängigkeiten bereitgestellt. reveal.js ist ein separates Open-Source-Projekt unter MIT-Lizenz. Das Installationsskript legt die Lizenzdatei des heruntergeladenen Release neben der Distribution ab.
