# La liste

Liste de courses partagée à deux. Page statique sur GitHub Pages, données dans `data/liste.json`, mail à l'autre à chaque modification.

## Fonctionnement

Le navigateur lit et écrit `data/liste.json` via l'API GitHub, avec un jeton saisi une fois par appareil et gardé en local. Chaque écriture crée un commit ; le workflow lit l'auteur dans le message de commit et envoie le mail à l'autre personne.

Le site publié se limite à `docs/`. Les données vivent dans `data/`, hors du dossier publié : l'appli y accède par l'API, jamais par l'URL du site. Un dépôt privé rend donc la liste réellement inaccessible, même si la page, elle, reste ouverte à qui a l'adresse.

```
docs/          publié par Pages — la page, rien de sensible
data/          la liste — jamais servie par le site
.github/       le workflow qui envoie le mail
```

Les modifications sont groupées : l'envoi part 2,5 s après la dernière frappe, pas à chaque article. Hors réseau, tout reste utilisable et repart à la reconnexion.

## Installation

**1. Le dépôt**

Crée le dépôt, pousse ces fichiers, puis Settings → Pages → Source : `Deploy from a branch`, branche `main`, dossier **`/docs`**.

Mets le dépôt en privé si tu veux que la liste le soit : `data/liste.json` n'est alors visible ni sur github.com ni sur le site. Pages depuis un dépôt privé demande un compte Pro — gratuit via le GitHub Student Developer Pack. En dépôt public, le fichier reste lisible sur github.com par n'importe qui.

Dans les deux cas, la page publiée est accessible à qui connaît l'URL. Ce n'est pas un problème : sans jeton, elle est vide.

**2. Les prénoms**

Dans `docs/index.html`, remplace la ligne `const NOMS = ["Jean", "Ma conjointe"];` par vos deux prénoms. Ils doivent correspondre exactement aux secrets ci-dessous.

**3. Le jeton, sur chaque téléphone**

Settings → Developer settings → Personal access tokens → Fine-grained tokens.

- Repository access : ce dépôt uniquement
- Permissions → Repository → Contents : **Read and write**
- Expiration : 1 an maximum, à renouveler

Ouvre le site, la fenêtre de connexion s'affiche : dépôt (`pseudo/liste-courses`), qui tu es, jeton. Pour la rouvrir ensuite, touche la ligne d'état sous le titre.

Le jeton reste dans le navigateur de l'appareil. Sa portée est limitée à ce dépôt : au pire, quelqu'un modifie la liste de courses.

**4. Le mail**

Le workflow passe par le SMTP de Gmail. Il faut la validation en deux étapes activée, puis un mot de passe d'application : myaccount.google.com → Sécurité → Mots de passe des applications.

Settings → Secrets and variables → Actions, ajoute :

| Secret | Valeur |
|---|---|
| `SMTP_USER` | l'adresse Gmail qui envoie |
| `SMTP_PASS` | le mot de passe d'application (16 caractères) |
| `NOM_A` | le premier prénom, identique à `NOMS[0]` |
| `MAIL_A` | son adresse |
| `MAIL_B` | l'adresse de l'autre |

**5. Sur le téléphone**

Ajoute la page à l'écran d'accueil : elle s'ouvre en plein écran, sans barre de navigateur.

## Usage

Taper puis Entrée pour ajouter. Toucher une ligne pour la barrer. Le × retire l'article, « Retirer ce qui est pris » vide les lignes barrées d'un coup.

## Limites

- Environ 2 à 3 secondes entre une modification et son apparition chez l'autre ; l'écran se rafraîchit toutes les 20 s quand il est ouvert.
- Édition simultanée : la version la plus récente de chaque article gagne, article par article. Rien n'est perdu, mais deux modifications du même article dans la même seconde peuvent en écraser une.
- Les articles retirés sont conservés 7 jours dans le fichier avant d'être purgés, le temps que les deux appareils voient la suppression.
- Un commit par modification : l'historique du dépôt grossit vite. Sans importance, mais c'est visible.
