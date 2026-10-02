# Hessel Build System

## Doel

Beheer alle projecten als één samenhangend systeem met minimale gebruikersinput. Een wijziging moet begrijpelijk, testbaar en terug te draaien zijn.

## Niet onderhandelbare regels

1. Eén repository is eigenaar van iedere bron.
2. Gegenereerde bestanden worden niet handmatig aangepast.
3. Productie wordt alleen gepubliceerd na automatische validatie.
4. Een project bevat geen geheimen, tokens, wachtwoorden of privésleutels.
5. Bestaande gebruikersdata en lokale wijzigingen worden nooit stil overschreven.
6. Nieuwe infrastructuur moet aantoonbaar minder handwerk opleveren.
7. Kies de kleinste begrijpelijke oplossing die het probleem volledig oplost.
8. Houd de code zonder AI leesbaar voor een gewone developer.

## Werkwijze voor agents en developers

1. Lees eerst `README.md`, `ARCHITECTURE.md`, `docs/PROJECT_STANDARD.md` en het lokale `turbo-project.json`.
2. Controleer vóór een wijziging welke repository eigenaar is van de code of content.
3. Maak kleine, gerichte commits.
4. Werk via een branch en pull request voor wijzigingen aan architectuur, deployment of productie.
5. Voer de relevante tests, build en healthcheck uit.
6. Werk documentatie en changelog bij wanneer gedrag verandert.
7. Meld expliciet welke bron leidend is en welke kopieën of oude routes moeten verdwijnen.

## Source of truth

| Onderdeel | Eigenaar |
|---|---|
| Portfolio en websitecontent | `website` |
| Hostnet deployment | `hostnet` |
| Projectregister en desktop Hub | `github` |
| Pallet Optimizer webapp | `pallet_optimizer_html` |
| Rebirth webapp | `rebirthchecker/web` |
| Projectspecifieke code | De eigen projectrepository |

## Definition of done

Een wijziging is klaar wanneer de code bouwt, tests slagen, healthcheck werkt, documentatie klopt, secrets ontbreken en er nog maar één productiepad bestaat.
