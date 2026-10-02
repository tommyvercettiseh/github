# Website-architectuur

## Huidige situatie

De website is een statische Hostnet-site met sterke motion en eigen fotografie. De homepage staat grotendeels in één `index.html` van ruim 43 KB met inline CSS en JavaScript.

Er bestaan momenteel drie publicatieroutes:

| Route | Locatie |
|---|---|
| Directe veilige SFTP-deploy | `website/.github/workflows/deploy-hostnet.yml` |
| Trigger naar centrale deploy | `website/.github/workflows/publish-hostnet.yml` |
| Centrale deploy | `hostnet/.github/workflows/deploy-hostnet.yml` |

Daarnaast staat Pallet Optimizer zowel in `pallet_optimizer_html` als gekopieerd onder `website/pallet-optimizer`.

## Doel

`website` wordt de enige bron voor portfolio en content. `hostnet` wordt de enige publicatielaag. Losse tools blijven eigenaar van hun eigen webbuild.

## Voorgestelde structuur

```text
website/
├── content/
│   ├── blog/
│   ├── projects/
│   └── services/
├── public/
│   ├── assets/
│   ├── fonts/
│   └── media/
├── src/
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── scripts/
│   └── styles/
├── tests/
├── astro.config.mjs
├── package.json
└── turbo-project.json
```

Astro bouwt statische bestanden naar `dist/`. Hostnet hoeft geen Node.js te draaien.

## Contentmodel

Een project toevoegen vereist één Markdownbestand:

```md
---
title: Freeze the Future
slug: freeze-the-future
summary: Hypotheekruimte en spaargroei in één helder dashboard.
status: active
featured: true
tags: [finance, web, automation]
image: /assets/projects/freeze-the-future.webp
app_url: /projects/hypotheek/
source_url: ""
order: 10
---

Korte uitleg van probleem, aanpak en resultaat.
```

De homepage, projectpagina en SEO-metadata worden hieruit gegenereerd.

## Designsysteem

| Token | Rol |
|---|---|
| Color | Achtergrond, tekst, accent, status |
| Type | Manrope voor UI, DM Mono voor metadata |
| Motion | Eén set durations, easing en reduced-motion gedrag |
| Card | Eén projectkaart met varianten |
| CTA | Eén primaire en één subtiele variant |
| Layout | Maxbreedte, spacing en mobiele breekpunten |

Beweging blijft onderdeel van de identiteit, maar wordt per component geladen. Geen generatieve animatie op pagina's waar zij geen inhoudelijke functie heeft.

## Publicatie

1. Pull request bouwt previewartifact.
2. CI controleert HTML, links, toegankelijkheid, performancebudget en metadata.
3. Merge naar `main` triggert `hostnet`.
4. `hostnet` downloadt alleen het gebouwde artifact.
5. Deployment maakt back-up, uploadt atomisch waar mogelijk en voert live checks uit.
6. Bij falen blijft de vorige release beschikbaar.

## Eerst oplossen

| Volgorde | Actie |
|---|---|
| 1 | Eén van de drie deployroutes kiezen: centraal via `hostnet` |
| 2 | Pallet Optimizer-kopie uit `website` uitfaseren |
| 3 | Homepage opsplitsen zonder zichtbaar ontwerpverlies |
| 4 | Projecten en diensten contentgedreven maken |
| 5 | Blog toevoegen vanuit Markdown |
| 6 | Projectmetadata uit het centrale register hergebruiken |
