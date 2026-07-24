# GitHub Hub

Een minimalistische Windows desktopapp waarmee je via GitHub inlogt en al je online repositories als kaarten bekijkt.

## Functies

• Login via GitHub CLI en browser
• Publieke en private repositories tonen
• Lokale repository vergelijken met de laatste GitHub commit
• Status: up-to-date, update beschikbaar, lokale wijzigingen of branches verschillen
• Veilig pullen met `git pull --ff-only`
• Downloaden wanneer een repository nog niet lokaal staat
• Openen in Visual Studio Code
• Openen op GitHub
• Zoeken op naam of omschrijving

## Starten op Windows

Dubbelklik op:

`Start Project.bat`

De launcher controleert automatisch of Python, Git en GitHub CLI aanwezig zijn.

Bij de eerste GitHub-login opent je browser. De app bewaart zelf geen wachtwoord of GitHub-token.

## Lokale projectmap

Klik op **Projectmap** en kies bijvoorbeeld:

`C:\Users\Hesse\GitHub`

Repositories die daar al bestaan worden automatisch gecontroleerd. Ontbrekende repositories kun je vanuit de kaart downloaden.

## Veiligheid

Pull wordt alleen aangeboden wanneer de lokale map schoon is, niet vooruitloopt en uitsluitend achterloopt op GitHub. Lokale wijzigingen worden nooit overschreven.
