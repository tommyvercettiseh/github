# Projectstandaard

## Minimale structuur

```text
project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── previews/
│       └── latest.webp
├── src/
├── tests/
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── ROADMAP.md
├── VERSION
└── turbo-project.json
```

Niet ieder project heeft letterlijk `src` nodig. Android gebruikt bijvoorbeeld `app`; een statische site kan `src` en `public` gebruiken. De metadata en documenten blijven gelijk.

## Verplichte bestanden

| Bestand | Doel |
|---|---|
| `README.md` | Wat het is, hoe het start en wat de actuele status is |
| `VERSION` | Huidige semantische versie |
| `CHANGELOG.md` | Veranderingen per versie |
| `ROADMAP.md` | Alleen geplande stappen, geen ideeënberg |
| `turbo-project.json` | Machineleesbare metadata voor Hub en automation |
| `AGENTS.md` | Projectspecifieke regels voor AI en developers |
| `.gitignore` | Sluit secrets, caches, builds, logs en lokale data uit |

## Naamgeving

| Onderdeel | Regel | Voorbeeld |
|---|---|---|
| Repository | lowercase kebab-case | `pallet-optimizer-web` |
| Branch | type/korte-naam | `feat/project-cards` |
| Commit | conventionele korte boodschap | `feat: add project registry` |
| Release | semver | `v1.2.0` |
| Publieke URL | korte slug | `/pallet-optimizer/` |

Bestaande repositorynamen hoeven niet direct te wijzigen. Pas de regel toe op nieuwe projecten en bij een geplande migratie.

## GitHub-profiel

Iedere actieve repository krijgt:

| Veld | Inhoud |
|---|---|
| Description | Eén concrete zin met resultaat |
| Topics | Drie tot zes functionele tags |
| Homepage | Publieke URL of lege waarde |
| Visibility | Privé tenzij publicatie bewust voordeel heeft |
| Archive | Aan voor vervangen of gestopt werk |

## Automatische controles

| Controle | Vereist voor |
|---|---|
| Metadata-schema | Alle projecten |
| Tests | Alle projecten met logica |
| Build | Web, Android en desktop |
| Secret scan | Alle projecten |
| Dependency scan | Projecten met dependencies |
| Artifactcontrole | Publiceerbare projecten |
| Healthcheck | Live webprojecten |

## Nieuw project met minimale input

De gebruiker levert alleen:

| Vraag | Voorbeeld |
|---|---|
| Naam | Finance Widget |
| Doel in één zin | Hypotheekruimte en spaardoel tonen |
| Platform | Android en web |
| Publiek of privé | Privé |

Automation maakt daarna de repositorystructuur, metadata, CI, README, roadmap, previewplaats en eerste versie aan.

## Releasebeleid

| Wijziging | Versie |
|---|---|
| Fix zonder nieuw gedrag | Patch |
| Nieuwe backwards-compatible functie | Minor |
| Brekende wijziging of datamigratie | Major |

Geen handmatig APK- of webbestand zonder bijbehorende versie, changelog en buildbewijs.
