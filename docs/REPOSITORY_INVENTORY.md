# Repository-inventarisatie

Momentopname: 2026-10-02  
Account: `tommyvercettiseh`

## Samenvatting

| Onderdeel | Aantal |
|---|---:|
| Repositories | 38 |
| Publiek | 20 |
| Privé | 18 |
| Leeg | 4 |
| Met `turbo-project.json` | 19 |
| Met ingevulde GitHub-beschrijving | 0 |
| Gearchiveerd | 0 |

## Belangrijkste bevindingen

| Prioriteit | Bevinding | Gevolg | Advies |
|---|---|---|---|
| Kritiek | Website kan via drie workflows naar Hostnet | Dubbele deploys en onduidelijke eigenaar | Alleen `hostnet` laten publiceren |
| Hoog | Pallet Optimizer bestaat als Pythonrepo, webrepo en kopie in `website` | Drift en dubbel onderhoud | Webversie alleen uit `pallet_optimizer_html` deployen |
| Hoog | Projectstandaard is gedeeltelijk ingevoerd | Hub moet uitzonderingen kennen | Schema valideren en gefaseerd uitrollen |
| Hoog | Alle GitHub-beschrijvingen zijn leeg | Slechte vindbaarheid en weinig context | Beschrijving, topics en homepage automatisch vullen |
| Midden | Vier lege repositories zijn actief zichtbaar | Ruis | Verwijderen of archiveren na controle |
| Midden | Meerdere naamclusters overlappen | Onduidelijk wat actueel is | Per cluster één actieve eigenaar kiezen |
| Midden | Grote gegenereerde mappen staan in `runescape` | Zware repository en ruis | Build, dist, logs en cache uit Git houden |

## Indeling

| Domein | Repositories | Voorgestelde status |
|---|---|---|
| Platform | `github`, `turbo-repo-launcher`, `hostnet`, `website` | Actief, duidelijke rollen geven |
| Productiviteit | `palletoptimizer`, `pallet_optimizer_html`, `barcode_extractor`, `pdf_to_image`, `youtubedownloader` | Actief, duplicatie Pallet oplossen |
| Fitness | `kcal-zen-dash`, `repcounter`, `mealplanner`, `fitmess_assistant` | Actief of backlog expliciet maken |
| Finance en woning | `money`, `woningmarkt`, `cbs`, `funda`, `duo`, `energy` | Consolideren rond duidelijke producten |
| Widgets en mobiel | `widget-launcher`, `osrs-price-widget`, `flitsers`, `gifs`, `maps`, `bluetooth`, `claudesensor` | Via Hub registreren |
| Vision en input | `ai-mouse`, `mouse`, `aimlab`, `facedetect`, `pokemoncardscanner` | Eigenaarschap per experiment vastleggen |
| RuneScape | `runescape`, `runescapetwo`, `objectmarker`, `sensor`, `rebirthchecker` | Actief versus legacy markeren |
| Overig | `tiktok` | Doel en status toevoegen |

## Directe kandidaten voor besluit

| Cluster | Huidige situatie | Voorgesteld besluit |
|---|---|---|
| `funda` | Leeg | Archiveren totdat de datastroom echt bestaat |
| `mealpllanner-` | Leeg en typefout | Verwijderen na controle |
| `duo` | Leeg | Archiveren of opnemen in `money` |
| `fitmess_assistant` | Leeg | Backloglabel of archiveren |
| `palletoptimizer` | Pythonproduct | Behouden als desktop/backendvariant |
| `pallet_optimizer_html` | Webproduct en deploybron | Enige webbron maken |
| `website/pallet-optimizer` | Handmatige kopie | Na omschakeling verwijderen |
| `runescape` en `runescapetwo` | Overlappende naam en functie | Eén active, één legacy |
| `ai-mouse`, `mouse`, `aimlab` | Overlappende experimenten | Eén productrepo, overige prototypes labelen |
| `github` en `turbo-repo-launcher` | Hub en launcher raken elkaar | `github` als control plane, launcher als herbruikbare client |

## Standaardstatus

Gebruik voortaan exact één status in `turbo-project.json`:

| Status | Betekenis |
|---|---|
| `active` | Wordt gebruikt en onderhouden |
| `backlog` | Idee, nog niet actief gebouwd |
| `prototype` | Experiment zonder productgarantie |
| `maintenance` | Werkt, alleen noodzakelijke fixes |
| `legacy` | Vervangen, alleen als naslag |
| `archived` | Niet meer gebruiken |
