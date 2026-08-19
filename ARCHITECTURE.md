# Architecture

Note de lecture pour comprendre ce que fait chaque fichier, sans connaître le web au préalable.

## Le principe

Il n'y a pas de serveur. Personne ne fait tourner de programme quelque part pour toi.

Il y a une page, copiée sur les deux téléphones à chaque ouverture, et un fichier de données dans le dépôt qui sert de source unique de vérité. Les deux téléphones lisent et réécrivent ce fichier chacun de leur côté. GitHub joue trois rôles distincts, et c'est ce qui rend le montage un peu déroutant au départ :

| Rôle | Ce que c'est | Payé par |
|---|---|---|
| Hébergeur | GitHub Pages sert `docs/` | gratuit (dépôt public) |
| Base de données | `data/liste.json` dans le dépôt | gratuit |
| Automate | GitHub Actions envoie le mail | gratuit |

```
        Téléphone 1                                  Téléphone 2
        ┌──────────┐                                 ┌──────────┐
        │  la page │                                 │  la page │
        └────┬─────┘                                 └────┬─────┘
             │  écrit / lit                    lit / écrit │
             │        (API GitHub + jeton)                 │
             └────────────────┐         ┌──────────────────┘
                              ▼         ▼
                    ┌──────────────────────────┐
                    │   data/liste.json        │   ← le dépôt GitHub
                    └────────────┬─────────────┘
                                 │  chaque écriture = 1 commit
                                 ▼
                    ┌──────────────────────────┐
                    │   GitHub Actions         │
                    │   .github/workflows      │
                    └────────────┬─────────────┘
                                 │  SMTP Gmail
                                 ▼
                          mail à l'autre
```

La page elle-même, elle, arrive par un chemin séparé et sans jeton : le téléphone la télécharge depuis `docs/` au premier chargement, puis la garde en cache. Elle ne contient aucune donnée.

## Le cycle d'une modification

C'est une vraie séquence, dans cet ordre :

1. Tu tapes « lait » et valides. L'article est ajouté à une liste en mémoire dans le téléphone.
2. L'écran se redessine immédiatement. Rien n'est encore parti sur le réseau — c'est pour ça que ça ne rame jamais.
3. La liste est recopiée dans le stockage local du navigateur. Si tu fermes tout maintenant, rien n'est perdu.
4. Un compte à rebours de 2,5 s démarre. Chaque nouvelle frappe le remet à zéro, ce qui évite un commit par article.
5. Le compte à rebours arrive à zéro : le téléphone envoie tout le fichier à l'API GitHub, avec le message de commit `liste: maj par Jean`.
6. GitHub écrit le fichier, crée le commit, et déclenche le workflow.
7. Le workflow lit le prénom dans le message, en déduit à qui écrire, extrait les articles non pris et envoie le mail.
8. L'autre téléphone, lui, redemande le fichier toutes les 20 s tant que l'appli est ouverte, et fusionne ce qu'il reçoit.

Le point 5 mérite une précision. L'API GitHub exige le `sha` de la version qu'on croit modifier. Si l'autre a écrit entre-temps, ce `sha` est périmé et GitHub refuse (erreur 409). L'appli relit alors la version à jour, fusionne article par article en gardant la plus récente des deux dates, et réessaie. C'est ce qui empêche l'un d'écraser l'autre.

## Ce que contient chaque fichier

| Fichier | Rôle | Modifié par |
|---|---|---|
| `docs/index.html` | toute l'appli : structure, apparence, comportement | toi, à la main |
| `docs/manifest.json` | permet l'ajout à l'écran d'accueil | jamais |
| `docs/icon.svg`, `docs/icon-192.png`, `docs/icon-512.png` | l'icône de l'appli, en plusieurs formats — les launchers Android gèrent mal le SVG seul | jamais |
| `docs/.nojekyll` | dit à Pages de publier les fichiers tels quels | jamais |
| `data/liste.json` | la liste | l'appli, automatiquement |
| `.github/workflows/notif.yml` | recette du mail | toi, si tu changes le SMTP |

Le jeton n'est nulle part dans cette liste, et c'est volontaire. Il vit dans le navigateur de chaque téléphone.

## Ce qu'il y a dans index.html

Un fichier web tient trois choses de nature différente. Dans notre cas elles sont empilées dans le même fichier, faute d'avoir besoin de plus.

**La structure** — les balises `<h1>`, `<ul>`, `<input>`. Ça décrit *quoi* est à l'écran, sans dire à quoi ça ressemble. C'est l'arborescence, l'équivalent d'une hiérarchie de widgets. Elle est courte ici : un titre, une ligne d'état, une liste vide, un champ de saisie, une fenêtre de réglages.

**Le style** — le bloc `<style>`. Ça décrit *comment* ça se présente : couleurs, tailles, espacements. On sélectionne des éléments par leur nom ou leur classe et on leur applique des propriétés. Les couleurs et dimensions du projet sont regroupées en haut sous `:root`, c'est là qu'on touche si on veut changer l'allure :

```
--papier    #EFF1EC   le fond
--encre     #1B2A22   le texte
--stylo     #1D3FBE   le trait de rature, les boutons
--marge     #D4453C   le filet vertical rouge
--reglure   #C3D0E8   les lignes horizontales
--ligne     34px      la hauteur d'une ligne du cahier
```

**Le comportement** — le bloc `<script>`. C'est du JavaScript, et c'est le seul endroit où il y a de la logique. Les fonctions y sont nommées en français :

```
etatDoc          la liste en mémoire
rendre()         redessine l'écran à partir de etatDoc
modifier()       applique un changement, sauve en local, planifie l'envoi
tirer()          lit le fichier depuis GitHub et fusionne
pousser()        écrit le fichier sur GitHub
fusionner()      arbitre entre deux versions, article par article
synchroniser()   décide s'il faut tirer ou pousser
```

Rien d'autre. Pas de bibliothèque, pas de compilation, pas de `npm install`. Le fichier que tu ouvres est exactement celui qui tourne, ce qui rend le débogage direct.

## Le layout

Une seule colonne, centrée, jamais plus large que 560 px. Sur téléphone elle occupe tout, sur ordinateur elle reste au milieu.

```
┌─────────────────────────────────────────┐
│ │                                       │  ← filet de marge rouge, vertical
│ │  La liste                             │     titre
│ │  À jour                               │     ligne d'état (toucher = réglages)
│ │ ─────────────────────────────────     │
│ │  lait                                 │  ← les lignes sont calées
│ │ ─────────────────────────────────     │     sur la réglure du cahier
│ │  farine                    ELSA       │  ← prénom si l'autre l'a ajouté
│ │ ─────────────────────────────────     │
│ │  c̶a̶f̶é̶                          ×      │  ← barré, descendu en bas
│ │ ─────────────────────────────────     │
│ │  Retirer ce qui est pris              │
│ │ ─────────────────────────────────     │
│ │                                       │
│ │            (espace vide)              │
│ │                                       │
├─────────────────────────────────────────┤
│  [ Ajouter…            ]  [ Ajouter ]   │  ← fixé en bas, à portée de pouce
└─────────────────────────────────────────┘
```

Trois décisions à connaître, parce qu'elles expliquent le reste du style :

Le fond est une image répétée tous les 34 px, générée en CSS, pas un fichier. La hauteur de ligne du texte vaut exactement ces 34 px, donc chaque article tombe pile sur une ligne. Si tu changes la taille du texte sans changer `--ligne`, le calage se casse — les deux valeurs vont ensemble.

Le champ de saisie est en position fixe en bas de l'écran. Sur un téléphone tenu d'une main dans un magasin, c'est la seule zone atteignable au pouce sans se contorsionner. Le titre, lui, n'a aucune importance fonctionnelle et occupe donc la zone la moins accessible.

Les articles pris descendent automatiquement en bas et se barrent d'un trait bleu tracé en 0,22 s. La rature n'est pas un caractère spécial mais un rectangle bleu de 2 px dont la largeur passe de 0 à 100 %. C'est ce qui donne l'impression d'un trait de stylo qui court.
