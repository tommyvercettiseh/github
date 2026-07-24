# Turbo GitHub Hub

Een simpele Windows desktopapp om lokale GitHub-projecten te herkennen, status te controleren, veilig te pullen en te openen.

## Functies

- Detecteert lokale Git-repositories in een gekozen hoofdmap
- Voert `git fetch` uit en vergelijkt lokaal met `origin`
- Statussen: up-to-date, update beschikbaar, lokale commits, conflict/diverged en lokale wijzigingen
- Veilige pull alleen wanneer de werkmap schoon is
- Openen in Visual Studio Code, Verkenner en GitHub
- Toont projectmetadata uit `turbo-project.json`
- Toont een preview uit `docs/previews/`
- Schrijft begrijpelijke logs naar `logs/github-hub.log`

## Starten op Windows

Dubbelklik op `Start Project.bat`.

De eerste keer kies je de map waarin je lokale repositories staan, bijvoorbeeld:

`C:\Users\Hesse\Projects`

## Veiligheid

De hub voert nooit automatisch een destructieve Git-actie uit. Pull wordt geblokkeerd bij lokale wijzigingen, een ontbrekende upstream of uiteenlopende branches.
