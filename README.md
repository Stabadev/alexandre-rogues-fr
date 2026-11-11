# Alexandre Rogues

Site statique français, sans dépendance ni compilation. `index.html` contient l’accueil ; `projets/*/index.html` les cinq présentations ; `style.css` et `site.js` sont partagés. `assets/portraitCV.png` est la source conservée, les WebP sont ses déclinaisons sans recadrage. Les anciennes illustrations inutilisées sont conservées dans assets.

## Prévisualiser

Depuis la racine :

```sh
python3 -B -m http.server 8000 --bind 127.0.0.1
```

Ouvrir http://127.0.0.1:8000/ ; arrêter avec Ctrl+C. Les chemins absolus nécessitent un serveur HTTP, pas une ouverture file://.

## Modifier

Modifier directement le HTML français. Reporter les changements pertinents entre accueil et fiches projets. Mettre à jour titres, descriptions et sitemap lorsqu’une page change. Les images doivent conserver leurs dimensions et textes alternatifs. Aucun contenu essentiel ne dépend de JavaScript.

## Futur déploiement (non effectué)

Vérifier les pages à 360, 390, 768 et 1440 px, le clavier, le menu et les liens externes. Confirmer les intitulés de formations et le téléphone. Publier uniquement les fichiers du site : HTML, CSS, JS, favicon.svg, robots.txt, sitemap.xml, fichier de validation Google, projets et ressources nécessaires. Exclure .git, les fichiers de travail et le PNG source si inutile à la publication. Supprimer sur la cible les anciens PDF, le dossier en et les anciens portraits : une simple copie additive les laisserait accessibles.

## Réouverture : proposition Caddy, non appliquée

Remplacer uniquement le bloc `alexandre.rogues.fr` lors de la réouverture validée. Cette proposition omet volontairement `basic_auth`. Elle n’a pas été validée par un binaire Caddy dans cet environnement.

```caddy
alexandre.rogues.fr {
    root * /opt/sites/alexandre-rogues-fr
    encode zstd gzip

    # Noms stables : stockage possible, revalidation avant réutilisation.
    header Cache-Control "no-cache"

    @ancienneAccueil path /en /en/ /en/index.html
    redir @ancienneAccueil / 301

    @anciensCV path /CV_Rogues_Alexandre_122025.pdf /en/CV_Rogues_Alexandre_122025_english.pdf
    respond @anciensCV "Ce document a été retiré." 410

    file_server
}
```

`file_server` conserve son comportement natif : slash final ajouté aux répertoires et erreur HTTP 404 pour un chemin absent. Pas de fallback vers `index.html`, pas de redirection globale des erreurs et pas de page 404 personnalisée. Les canoniques, liens et sitemap utilisent `/` et `/projets/nom/`. Les alias `/index.html` restent exclus du sitemap et portent la canonique de leur répertoire.

`no-cache` ne désactive pas le stockage : il impose une revalidation, adaptée aux noms stables du HTML, CSS, JS et images. Aucun `immutable` ni cache long. `encode` négocie zstd/gzip pour les réponses adaptées ; vérifier réellement la compression après publication. Aucun nouvel en-tête de sécurité ajouté sans besoin établi.

Références : [file_server](https://caddyserver.com/docs/caddyfile/directives/file_server), [encode](https://caddyserver.com/docs/caddyfile/directives/encode), [header](https://caddyserver.com/docs/caddyfile/directives/header).

### Traitement des anciennes URL

| URL | Traitement prévu |
| --- | --- |
| `/en`, `/en/`, `/en/index.html` | 301 vers `/` |
| `/CV_Rogues_Alexandre_122025.pdf` | 410, sans redirection |
| `/en/CV_Rogues_Alexandre_122025_english.pdf` | 410, sans redirection |
| `/en/portrait.webp`, `/portrait.webp` | 404 après nettoyage des anciens fichiers |
| Autres chemins sous `/en/` | 404 : aucune autre ancienne page documentée ni correspondance connue |
| Toute URL inconnue | 404 native |

Ne pas bloquer ces anciennes URL dans robots.txt : les robots doivent pouvoir constater leur retrait. Ne pas copier l’ensemble du dépôt sur le serveur ; exclure aussi README, scripts de validation et fichiers sources non destinés au public.

## Contrôles locaux

```sh
python3 scripts/check_site.py
node --check site.js
```

Le contrôle statique vérifie les six pages, titres et descriptions uniques, canoniques, partage, JSON-LD, ressources, ancres, images et correspondance exacte avec le sitemap. Il ne mesure ni rendu ni performances. Les dates du sitemap correspondent à la création/refonte connue du 11 novembre 2026 ; les modifier uniquement après un changement réel de la page, jamais automatiquement à chaque déploiement.

Lighthouse et Caddy ne sont pas disponibles dans l’environnement de travail ; le serveur local y est bloqué par une restriction de création de socket. Aucun score Lighthouse mesuré. Objectif : 100/100 dans les quatre catégories, sans garantie de résultat. Tester l’accueil et `/projets/visiontrafic/` en mobile et desktop avec Lighthouse dans Chrome, en consignant version du navigateur/Lighthouse, date, URL, mode et conditions de throttling. Vérifier aussi le clavier, le menu, les contrastes et le rendu à 360, 390, 768 et 1440 px. Un score ne garantit ni accessibilité exhaustive, ni indexation, ni classement.

## Après déploiement — accès serveur et Search Console requis

1. Sauvegarder le site et la configuration Caddy existante. Préparer le seul bloc concerné, sans identifiants dans le dépôt. Valider la configuration complète avec `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` (adapter le chemin si nécessaire), puis seulement recharger le service. Ne pas modifier les autres sites.
2. Vérifier en navigation privée et avec une requête sans identifiants que l’accueil et les cinq projets répondent 200, sans défi d’authentification.
3. Contrôler les 301 du tableau, les deux PDF en 410, les anciens portraits et une URL inconnue en 404. Tester les redirections sans suivre automatiquement leur destination pour constater le statut initial. Vérifier le slash des répertoires et la destination finale.
4. Contrôler `robots.txt`, `sitemap.xml`, les canoniques et l’absence de `X-Robots-Tag` bloquant. Vérifier `Cache-Control`, la revalidation et `Content-Encoding` avec `Accept-Encoding: gzip` sur le HTML/CSS. Les contrôles locaux ne prouvent aucun de ces comportements en production.
5. Refaire Lighthouse sur l’accueil et VisionTrafic, en mobile et desktop. Conserver les rapports, corriger les problèmes réels et mesurer de nouveau après correction.
6. Vérifier la propriété dans Google Search Console et la présence de la balise HTML de validation dans le `<head>` de l’accueil public. Vérifier également l’accès au fichier `googleec8bd3385bb077c6.html`, conservé sans modification.
7. Soumettre `https://alexandre.rogues.fr/sitemap.xml`.
8. Inspecter l’accueil et les principales pages projets avec le test d’URL en direct ; demander leur indexation si nécessaire.

Le retour dans les résultats dépend ensuite de l’exploration et des décisions de Google. Aucun délai ni classement ne peut être promis.

## Validation Search Console à préserver

La propriété Search Console existante est validée par **balise HTML**, selon la méthode confirmée dans Search Console. Conserver exactement cette balise dans le `<head>` de `index.html` lors des futures refontes, sans doublon :

```html
<meta name="google-site-verification" content="ylva5NHAvvBIZWhkt4nmgTzVdqxMyYQFw1ojgWT32LI" />
```

`scripts/check_site.py` contrôle sa présence, sa valeur exacte et son unicité dans le `<head>` de l’accueil. Une autre valeur éventuelle est signalée sans être supprimée. Le fichier `googleec8bd3385bb077c6.html` est également conservé ; il ne remplace pas cette balise pour la méthode de validation actuelle.
