# Changelog

## 0.2.0

### Toegevoegd

• GitHub-login via GitHub CLI en browser
• Alle publieke en private accountrepositories als minimalistische kaarten
• Downloadknop voor repositories die nog niet lokaal staan
• Zoekfunctie op repositorynaam en omschrijving
• Projectmap instellen vanuit de app

### Gewijzigd

• Interface volledig vereenvoudigd naar één loginbalk en een raster met kaarten
• Open opent een lokale repository direct in Visual Studio Code
• Windows-launcher controleert Python, Git en GitHub CLI

### Veiligheid

• Pull gebruikt uitsluitend `git pull --ff-only`
• Pull wordt niet aangeboden bij lokale wijzigingen, lokale commits of uiteenlopende branches
• De app slaat zelf geen GitHub-wachtwoord of token op

### Handmatige controle

• Eerste browserlogin bij GitHub
• Eenmalig de gewenste lokale projectmap kiezen

## 0.1.0

### Toegevoegd

• Lokale Git-repositories herkennen
• Git fetch en statusvergelijking
• Veilige pull
• Openen in Visual Studio Code en GitHub
• Windows-launcher en GitHub Actions
