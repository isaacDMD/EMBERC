# EMBERC

**Plateforme Numérique de l'Église Mission Baptiste Évangélique Royaume du Christ**

> Ce README fait office de dossier de référence du projet — il décrit le système tel qu'il est **réellement implémenté**, pas tel qu'il a été initialement conçu. Voir [État d'avancement](#-état-davancement-du-projet) pour le détail module par module.

---

## Sommaire

- [Contexte](#contexte)
- [Objectifs](#objectifs)
- [État d'avancement du projet](#-état-davancement-du-projet)
- [Architecture technique](#architecture-technique)
- [Structure du projet](#structure-du-projet-backend)
- [Base de données](#base-de-données-postgresql--schéma-réel)
- [API REST](#api-rest--endpoints-réellement-implémentés)
- [Rôles et permissions](#gestion-des-rôles-et-permissions)
- [Feuille de route](#feuille-de-route--avancement-réel)
- [Environnement de développement](#environnement-de-développement)
- [Bonnes pratiques](#bonnes-pratiques-à-respecter)
- [Vision long terme](#vision-long-terme-v2-et-au-delà)
- [Glossaire](#glossaire)

---

## Contexte

L'EMBERC est une communauté chrétienne composée de plusieurs paroisses. Chaque paroisse organise régulièrement des cultes, des réunions, des événements spéciaux et des activités impliquant différents groupes tels que les lecteurs, les groupes musicaux, les responsables de ministères et les fidèles.

Actuellement, la diffusion des informations se fait principalement sous format papier ou verbalement, ce qui limite l'accès à l'information pour les fidèles absents, les nouveaux membres ou les personnes souhaitant se préparer à l'avance.

## Objectifs

**Objectif général** : développer une plateforme numérique centralisée permettant aux fidèles et aux responsables des différentes paroisses de consulter, publier et gérer les informations relatives à la vie de l'église.

**Objectifs spécifiques**
- Faciliter l'accès aux programmes des cultes et événements
- Centraliser les lectures bibliques prévues pour les cultes
- Mettre à disposition une bibliothèque numérique des chants
- Permettre l'écoute des versions audio des chants
- Améliorer la communication entre les paroisses et les fidèles
- Réduire la dépendance aux supports papier
- Favoriser la préparation spirituelle des fidèles avant les cultes

---

## 🚧 État d'avancement du projet

### Phase 1 — Fondations & environnement
- [x] Docker Compose, PostgreSQL, FastAPI `/docs` accessible

### Phase 2 — Module Chants
- [x] CRUD complet (GET liste, GET détail, POST, PUT)
- [x] Champ `fichier_audio_url` (URL simple, pas encore d'upload réel vers Cloudflare R2)
- [ ] Upload réel de fichier audio (`POST /chants/{id}/audio`)
- [ ] Champs `partition_url` et `ajoute_par` non implémentés (décision consciente, à revoir plus tard)

### Phase 3 — Module Programmes
- [x] CRUD `programmes_culte` (GET liste avec filtres `paroisse_id`/`publie`, GET détail, POST, PUT, DELETE)
- [x] Chants programmés (`programme_chants`) avec ordre de passage — GET, POST, PUT, DELETE nichés sous `/programmes/{id}/chants`
- [x] Lectures bibliques (`lecture_biblique`) avec lecteurs multiples et langue par lecteur (`lecture_lecteurs`) — nichés sous `/lectures/{id}/lecteurs`

### Phase 4 — Authentification & rôles
- [x] Authentification par identifiant (username) + mot de passe — pas par email, pour rester accessible aux fidèles/staff sans adresse email
- [x] Hashage bcrypt (librairie `bcrypt` directe, `passlib` abandonné pour incompatibilité avec bcrypt 4.x)
- [x] JWT access token (60 min) + refresh token (30 jours) via `python-jose`
- [x] Endpoints `/auth/login`, `/auth/refresh`, `/auth/me`
- [x] Gestion des utilisateurs réservée au `super_admin` (`/users`)
- [x] Protection par rôle (`require_roles`) sur tous les endpoints d'écriture
- [x] Isolation par paroisse (`verify_paroisse_access`) : un `admin_paroisse` ou `resp_lecteurs` ne peut agir que sur sa propre paroisse ; le `super_admin` n'a aucune restriction

### Phase 5 — Annonces, Événements, Médias
- [x] CRUD Annonces avec `auteur_id` déduit automatiquement de l'utilisateur connecté, filtre `actives_seulement`
- [x] CRUD Événements avec filtre `a_venir_seulement`
- [x] CRUD Médias avec filtre par `type_media`
- [x] Les trois modules respectent l'isolation par paroisse

### Ce qui reste à faire
- [ ] **Favoris** — modèle en base existant, mais schema/service/router non implémentés
- [ ] **Actualités / Articles** — pas encore de modèle en base
- [ ] **Upload réel de fichiers** vers Cloudflare R2 (actuellement, tous les champs `*_url` sont de simples chaînes de caractères saisies manuellement)
- [ ] **Notifications** (PWA push FCM, email)
- [ ] **Frontend Nuxt** — non commencé à ce jour

---

## Architecture technique

### Vue d'ensemble

La plateforme suit une architecture client-serveur à 3 couches : Frontend (Nuxt/Vue.js — non démarré), Backend (FastAPI — en cours), et Persistance (PostgreSQL + Cloud Storage prévu). La communication entre le frontend et le backend se fait via une API REST sécurisée par JWT.

### Stack technologique

| Couche | Technologie | Rôle | Statut |
|---|---|---|---|
| Frontend | Vue.js 3 / Nuxt 3 | UI, SSR, routing | Non démarré |
| Backend | FastAPI | API REST Python | En cours |
| Backend | SQLAlchemy 2.x | ORM Python ↔ PostgreSQL | Actif |
| Backend | Alembic | Migrations de base de données | Actif |
| Backend | Pydantic v2 | Validation des données | Actif |
| Backend | python-jose[cryptography] | Génération / validation JWT | Actif |
| Backend | bcrypt (direct) | Hashage des mots de passe | Actif — remplace passlib |
| Backend | email-validator | Validation du champ email optionnel | Actif |
| Base de données | PostgreSQL 16+ | Base relationnelle principale | Actif |
| Stockage | Cloudflare R2 | Fichiers audio / vidéo / documents | Prévu, non intégré |

> ℹ️ **passlib a été abandonné** : la librairie n'est plus maintenue et est incompatible avec bcrypt ≥ 4.0 (l'attribut `__about__` a été retiré). On utilise désormais le package `bcrypt` directement, avec la même interface `hash_password`/`verify_password`.

### Authentification — choix retenu

Contrairement à la conception initiale (email + mot de passe), l'authentification se fait par un **identifiant (username)** attribué par un administrateur, avec l'email en champ optionnel. Ce choix a été fait pour rester accessible dans un contexte où une partie des fidèles et même du personnel de paroisse ne possède pas d'adresse email — l'email reste disponible pour les notifications futures, mais n'est jamais requis pour se connecter.

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/v1/auth/login` | POST | Connexion par identifiant + mot de passe, retourne `access_token` + `refresh_token` |
| `/api/v1/auth/refresh` | POST | Renouvelle un `access_token` à partir d'un `refresh_token` valide |
| `/api/v1/auth/me` | GET | Profil de l'utilisateur courant (token requis) |

---

## Structure du projet (backend)

```
backend/app/
├── main.py                    ← Point d'entrée, enregistre tous les routers
├── database.py
├── dependencies.py            ← get_db
├── models/
│   ├── user.py                ← identifiant (unique), email (nullable)
│   ├── paroisse.py
│   ├── programme_culte.py
│   ├── programme_chants.py
│   ├── chant.py                ← fichier_audio_url
│   ├── lecture_biblique.py
│   ├── lecture_lecteurs.py     ← multi-lecteurs, langue par lecteur
│   ├── annonces.py
│   ├── evenement.py
│   ├── media.py
│   └── favoris.py               ← modèle existant, non exposé par l'API
├── enums/
│   ├── roles.py
│   ├── chant_categorie.py
│   ├── culte_type.py
│   ├── annonce_type.py
│   ├── evenement_type.py
│   └── medias_type.py
├── schemas/                    ← un module par domaine (Base/Create/Update/Out)
├── services/                   ← logique métier, un module par domaine
├── routers/                    ← un router par domaine, préfixe /api/v1/...
└── auth/
    ├── security.py              ← hash_password / verify_password (bcrypt)
    ├── jwt.py                   ← create_access_token / create_refresh_token / decode_token
    └── permissions.py           ← get_current_user, require_roles, verify_paroisse_access
```

---

## Base de données (PostgreSQL) — schéma réel

> Cette section reflète les tables telles qu'elles existent réellement après migrations, et non la conception initiale. Les écarts avec la v1.0 sont signalés en note.

### Table : `users`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| nom | VARCHAR(100) | NOT NULL | Nom de famille |
| prenom | VARCHAR(150) | NOT NULL | Prénom |
| identifiant | VARCHAR(100) | NOT NULL, UNIQUE | Identifiant de connexion (remplace l'email obligatoire) |
| email | VARCHAR(150) | NULLABLE, UNIQUE | Email optionnel (notifications futures) |
| mot_de_passe | VARCHAR(255) | NOT NULL | Hash bcrypt |
| role | ENUM RoleEnum | NOT NULL, défaut `fidele` | super_admin / admin_paroisse / resp_musical / resp_lecteurs / fidele |
| paroisse_id | INT | FK → paroisses.id, nullable | Paroisse de rattachement |
| locale | VARCHAR(10) | défaut `fr` | Langue préférée |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

> ℹ️ Écart avec la v1.0 : `email` n'est plus la clé de connexion et devient optionnel ; `identifiant` est la nouvelle colonne unique obligatoire.

### Table : `chants`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| numero | VARCHAR(20) | NOT NULL, UNIQUE | Numéro dans le recueil |
| titre | VARCHAR(255) | NOT NULL | Titre du chant |
| paroles | TEXT | | Paroles complètes |
| categorie | ENUM CategorieChantEnum | NOT NULL | Catégorie du chant |
| auteur | VARCHAR(255) | | Auteur / Compositeur |
| fichier_audio_url | VARCHAR(255) | | URL audio (renommé depuis `url_audio`) |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

> ℹ️ `partition_url` et `ajoute_par` de la v1.0 ne sont pas implémentés — décision consciente pour l'instant.

### Table : `programmes_culte`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| titre | VARCHAR(255) | NOT NULL | Titre du programme |
| type_culte | ENUM CulteTypeEnum | défaut `DIMANCHE` | Type de culte |
| predicateur | VARCHAR(200) | | Nom du prédicateur |
| date_heure | TIMESTAMP | NOT NULL | Date et heure du culte (fusion de `date_culte` + `heure` de la v1.0) |
| paroisse_id | INT | FK → paroisses.id | Paroisse organisatrice |
| publie | BOOLEAN | défaut FALSE | Visible par les fidèles |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

> ℹ️ Écart avec la v1.0 : les colonnes distinctes `date_culte`, `heure`, `lieu` et `theme` ont été simplifiées en un seul `date_heure` ; `lieu` et `theme` ne sont pas implémentés à ce stade.

### Table : `programme_chants` (liaison)

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| programme_culte_id | INT | FK → programmes_culte.id | Programme concerné |
| chant_id | INT | FK → chants.id | Chant programmé |
| ordre | INT | NOT NULL | Ordre de passage |

### Table : `lecture_biblique`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| reference | VARCHAR(100) | NOT NULL | Ex : Jean 3:16-21 |
| texte | TEXT | | Texte complet ou extrait |
| date_lecture | TIMESTAMP | NOT NULL | Date du culte concerné |
| type_evenement | VARCHAR(100) | | Culte, Veillée, Camp… |
| programme_id | INT | FK → programmes_culte.id | Programme associé |
| paroisse_id | INT | FK → paroisses.id | Paroisse concernée |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

> ℹ️ Écart avec la v1.0 : `lecteur_id` a été retiré de cette table. Un seul lecteur ne suffisait pas — voir `lecture_lecteurs` ci-dessous.

### Table : `lecture_lecteurs` (liaison, nouvelle par rapport à la v1.0)

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| lecture_id | INT | FK → lecture_biblique.id | Lecture concernée |
| lecteur_id | INT | FK → users.id | Fidèle désigné comme lecteur |
| langue | VARCHAR(10) | défaut `fr` | Langue de lecture assignée |
| created_at | TIMESTAMP | auto | Date d'assignation |

### Table : `annonces`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| titre | VARCHAR(255) | NOT NULL | Titre de l'annonce |
| contenu | TEXT | NOT NULL | Corps de l'annonce |
| type_annonce | ENUM AnnonceType | défaut `REUNION` | Type d'annonce |
| date_debut / date_fin | DATE | NOT NULL | Période de validité |
| important | BOOLEAN | défaut FALSE | Déclencheur notification, priorité d'affichage |
| paroisse_id | INT | FK → paroisses.id | Paroisse émettrice |
| auteur_id | INT | FK → users.id | Déduit automatiquement de l'utilisateur connecté |
| publie | BOOLEAN | défaut FALSE | Visible par les fidèles |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

### Table : `evenements`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| titre | VARCHAR(255) | NOT NULL | Nom de l'événement |
| description | TEXT | | Description complète |
| type_evenement | ENUM EvenementTypeEnum | | congres / conference / concert / camp… |
| date_debut / date_fin | DATE | NOT NULL | Période de l'événement (simplifié depuis TIMESTAMP en v1.0) |
| lieu | VARCHAR(255) | | Lieu de l'événement |
| image_url | VARCHAR(255) | | Affiche |
| paroisse_id | INT | FK → paroisses.id | Paroisse organisatrice |
| publie | BOOLEAN | défaut FALSE | Visible par les fidèles |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

### Table : `medias`

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | SERIAL | PK | Identifiant unique |
| titre | VARCHAR(255) | NOT NULL | Titre du média |
| type_media | ENUM MediaTypeEnum | NOT NULL | audio / video / photo / document |
| description | TEXT | | Résumé / contexte |
| url_media | VARCHAR(255) | NOT NULL | URL du fichier |
| thumbnail_url | VARCHAR(255) | | Image de couverture |
| duree_secondes | INT | | Durée (audio/vidéo) |
| paroisse_id | INT | FK → paroisses.id | Paroisse source |
| publie | BOOLEAN | défaut FALSE | Visible par les fidèles |
| created_at / updated_at | TIMESTAMP | auto | Horodatage |

### Table : `favoris` (modèle existant, non encore exposé par l'API)

Le modèle SQLAlchemy existe déjà (`user_id`, `type`, `item_id`, `created_at`), mais aucun schema/service/router n'a encore été créé.

---

## API REST — endpoints réellement implémentés

Préfixe global : `/api/v1/`. Authentification : `Bearer Token JWT` dans le header `Authorization`. Sauf mention contraire, les listes acceptent `?page=&limit=` pour la pagination.

### Authentification

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| POST | `/auth/login` | Public | Connexion par identifiant + mot de passe |
| POST | `/auth/refresh` | Refresh token valide | Renouvelle les tokens |
| GET | `/auth/me` | Connecté | Profil de l'utilisateur courant |

### Utilisateurs

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/users` | super_admin | Liste paginée des utilisateurs |
| POST | `/users` | super_admin | Créer un utilisateur |
| PUT | `/users/{id}/role` | super_admin | Modifier le rôle d'un utilisateur |

### Paroisses

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/paroisses` | Public | Liste des paroisses |
| GET | `/paroisses/{id}` | Public | Détail d'une paroisse |
| POST | `/paroisses` | super_admin | Créer une paroisse |
| PUT | `/paroisses/{id}` | super_admin, admin_paroisse (la sienne) | Modifier une paroisse |

### Chants

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/chants` | Public | Liste des chants |
| GET | `/chants/{id}` | Public | Détail d'un chant |
| POST | `/chants` | super_admin, admin_paroisse, resp_musical | Ajouter un chant |
| PUT | `/chants/{id}` | super_admin, admin_paroisse, resp_musical | Modifier un chant |

### Programmes de culte

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/programmes` | Public | Liste, filtrable par `paroisse_id`, `publie` |
| GET | `/programmes/{id}` | Public | Détail d'un programme |
| POST | `/programmes` | super_admin, admin_paroisse (sa paroisse) | Créer un programme |
| PUT | `/programmes/{id}` | super_admin, admin_paroisse (sa paroisse) | Modifier un programme |
| DELETE | `/programmes/{id}` | super_admin, admin_paroisse (sa paroisse) | Supprimer un programme |

### Chants programmés (nichés sous un programme)

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/programmes/{id}/chants` | Public | Liste des chants du programme, triés par ordre |
| POST | `/programmes/{id}/chants` | super_admin, admin_paroisse, resp_musical | Ajouter un chant au programme |
| PUT | `/programmes/{id}/chants/{chant_id}` | super_admin, admin_paroisse, resp_musical | Modifier l'ordre de passage |
| DELETE | `/programmes/{id}/chants/{chant_id}` | super_admin, admin_paroisse, resp_musical | Retirer un chant du programme |

### Lectures bibliques

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/lectures` | Public | Liste, filtrable par `paroisse_id`, `programme_id` |
| GET | `/lectures/{id}` | Public | Détail d'une lecture |
| POST | `/lectures` | super_admin, admin_paroisse, resp_lecteurs (sa paroisse) | Créer une lecture |
| PUT | `/lectures/{id}` | super_admin, admin_paroisse, resp_lecteurs (sa paroisse) | Modifier une lecture |
| DELETE | `/lectures/{id}` | super_admin, admin_paroisse, resp_lecteurs (sa paroisse) | Supprimer une lecture |

### Lecteurs assignés (nichés sous une lecture)

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/lectures/{id}/lecteurs` | Public | Liste des lecteurs assignés, avec nom/langue |
| POST | `/lectures/{id}/lecteurs` | super_admin, admin_paroisse, resp_lecteurs | Assigner un lecteur (avec langue) |
| DELETE | `/lectures/{id}/lecteurs/{assoc_id}` | super_admin, admin_paroisse, resp_lecteurs | Retirer un lecteur assigné |

### Annonces

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/annonces` | Public | Liste, filtres `paroisse_id`/`publie`/`actives_seulement` |
| GET | `/annonces/{id}` | Public | Détail d'une annonce |
| POST | `/annonces` | super_admin, admin_paroisse (sa paroisse) | Publier une annonce (`auteur_id` automatique) |
| PUT | `/annonces/{id}` | super_admin, admin_paroisse (sa paroisse) | Modifier une annonce |
| DELETE | `/annonces/{id}` | super_admin, admin_paroisse (sa paroisse) | Supprimer une annonce |

### Événements

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/evenements` | Public | Liste, filtres `paroisse_id`/`publie`/`a_venir_seulement` |
| GET | `/evenements/{id}` | Public | Détail d'un événement |
| POST | `/evenements` | super_admin, admin_paroisse (sa paroisse) | Créer un événement |
| PUT | `/evenements/{id}` | super_admin, admin_paroisse (sa paroisse) | Modifier un événement |
| DELETE | `/evenements/{id}` | super_admin, admin_paroisse (sa paroisse) | Supprimer un événement |

### Médias

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| GET | `/medias` | Public | Liste, filtres `paroisse_id`/`publie`/`type_media` |
| GET | `/medias/{id}` | Public | Détail d'un média |
| POST | `/medias` | super_admin, admin_paroisse (sa paroisse) | Ajouter un média |
| PUT | `/medias/{id}` | super_admin, admin_paroisse (sa paroisse) | Modifier un média |
| DELETE | `/medias/{id}` | super_admin, admin_paroisse (sa paroisse) | Supprimer un média |

### Favoris — non implémenté

⏳ Aucun endpoint `/favoris` n'existe encore. Prévu : `GET`/`POST`/`DELETE /favoris`, restreints à l'utilisateur connecté sur ses propres favoris.

---

## Gestion des rôles et permissions

### Mécanisme

Deux dépendances FastAPI travaillent ensemble :

- **`require_roles(*roles)`** — vérifie que le rôle de l'utilisateur connecté fait partie de la liste autorisée pour cette route ; sinon `403`.
- **`verify_paroisse_access(current_user, paroisse_id)`** — pour les rôles non `super_admin`, vérifie que la paroisse ciblée correspond à celle de l'utilisateur ; sinon `403 "Vous n'avez pas accès à cette paroisse"`.

> ℹ️ Sur les routes `PUT`/`DELETE`, la vérification se fait sur le `paroisse_id` déjà stocké en base pour la ressource concernée — jamais sur celui du payload envoyé par le client, qui pourrait être absent ou falsifié en `PUT` partiel.

### Matrice des permissions

| Action | super_admin | admin_paroisse | resp_musical | resp_lecteurs | fidèle |
|---|:---:|:---:|:---:|:---:|:---:|
| Gérer toutes les paroisses | ✓ | ✗ | ✗ | ✗ | ✗ |
| Gérer sa paroisse uniquement | ✓ | ✓ | ✗ | ✗ | ✗ |
| Gérer tous les utilisateurs | ✓ | ✗ | ✗ | ✗ | ✗ |
| Ajouter / modifier un chant | ✓ | ✓ | ✓ | ✗ | ✗ |
| Programmer des chants | ✓ | ✓ | ✓ | ✗ | ✗ |
| Publier un programme | ✓ | ✓ (sa paroisse) | ✗ | ✗ | ✗ |
| Ajouter / modifier une lecture | ✓ | ✓ (sa paroisse) | ✗ | ✓ (sa paroisse) | ✗ |
| Publier une annonce | ✓ | ✓ (sa paroisse) | ✗ | ✗ | ✗ |
| Créer un événement | ✓ | ✓ (sa paroisse) | ✗ | ✗ | ✗ |
| Uploader un média | ✓ | ✓ (sa paroisse) | ✗ | ✗ | ✗ |
| Consulter tous les contenus publics | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Feuille de route — avancement réel

| Phase | Nom | Statut |
|---|---|---|
| Phase 1 | Fondations & environnement | ✅ Terminée |
| Phase 2 | Module Chants | ✅ Terminée (upload audio réel non fait) |
| Phase 3 | Module Programmes (+ chants programmés + lectures) | ✅ Terminée |
| Phase 4 | Authentification & rôles (+ isolation par paroisse) | ✅ Terminée |
| Phase 5 | Annonces & Événements & Médias | ✅ Terminée |
| — | Favoris | ⏳ À faire |
| Phase 6 | Médias & Actualités (upload réel, articles) | ⏳ Partielle — CRUD médias fait, upload et actualités restants |
| Phase 7 | Notifications | ⏳ À faire |
| Phase 8 | Polissage & déploiement | ⏳ À faire |
| Frontend | Application Nuxt 3 | ❌ Non démarrée |

---

## Environnement de développement

### Prérequis

- Node.js 20+ (pour Nuxt, à venir)
- Python 3.12+ / testé aussi avec 3.14 (pour FastAPI)
- Docker Desktop (PostgreSQL en local)
- Git

### Dépendances backend clés (`requirements.txt`)

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
bcrypt>=4.0.0
email-validator>=2.0.0
```

> ℹ️ `passlib[bcrypt]` a été retiré de la liste — voir la section [Authentification](#authentification--choix-retenu) pour la raison.

### Commandes de démarrage

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# → API sur http://localhost:8000
# → Documentation sur http://localhost:8000/docs
```

---

## Bonnes pratiques à respecter

### Git
- Une branche par fonctionnalité : `feature/chants-library`, `feature/auth-jwt`
- Commits en français, message court et clair
- Ne jamais committer le fichier `.env`

### Sécurité
- Mots de passe hashés avec bcrypt (via la librairie `bcrypt` directement, pas `passlib`)
- Toutes les entrées validées côté backend avec Pydantic
- JWT : access token courte durée (60 min), refresh token longue durée (30 jours), champ `type` distinct pour éviter la confusion entre les deux
- Isolation stricte par paroisse pour tous les rôles non `super_admin`

### Performance
- Pagination obligatoire sur toutes les listes (`page`, `limit`)
- Filtres dédiés par domaine (`paroisse_id`, `publie`, `actives_seulement`, `a_venir_seulement`, `type_media`…)

---

## Vision long terme (v2 et au-delà)

| Fonctionnalité | Impact architectural | Priorité |
|---|---|---|
| Upload réel de fichiers (Cloudflare R2) | Remplacer les champs URL saisis manuellement par un vrai flux d'upload | Haute |
| Diffusion en direct des cultes | Intégration LivePeer ou YouTube Live API | Haute |
| Inscriptions aux événements | Table `registrations` + paiement optionnel | Haute |
| Contributions financières | Stripe / Mobile Money (MTN, Moov) | Haute |
| Authentification par téléphone + OTP | Passerelle SMS locale, pour ouvrir les comptes aux fidèles à grande échelle | Moyenne |
| Application mobile native | React Native ou Flutter partageant l'API | Moyenne |
| Multi-église | Tenant isolation dans la DB | Basse |

---

## Glossaire

| Terme | Définition |
|---|---|
| API REST | Interface de programmation permettant la communication entre frontend et backend via HTTP |
| JWT | JSON Web Token — jeton sécurisé contenant l'identité et les droits de l'utilisateur |
| Access token | Jeton de courte durée (60 min) utilisé pour authentifier chaque requête |
| Refresh token | Jeton de longue durée (30 jours) utilisé pour renouveler un access token expiré |
| bcrypt | Algorithme de hashage de mots de passe, utilisé directement (sans passlib) |
| Isolation par paroisse | Règle métier : un rôle autre que `super_admin` ne peut agir que sur les données de sa propre paroisse |
| ORM | Object-Relational Mapper — SQLAlchemy traduit les objets Python en requêtes SQL |
| Migration | Script Alembic qui fait évoluer la structure de la base de données sans perdre les données |
| Pydantic | Bibliothèque Python de validation de données, utilisée par FastAPI |

---

*Dossier de référence EMBERC — Version 2.0 — Juillet 2026*
