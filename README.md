# 🏆 AFCON Analytics Dashboard

🔗 **Accéder à l’application en ligne :**  
👉 https://afcon-dashboard.streamlit.app/


### *Analyse complète de la Coupe d’Afrique des Nations — Visualisations modernes, analyses interactives & insights avancés.*

---

## 📌 Présentation

**AFCON Analytics Dashboard** est une application interactive construite avec **Python + Streamlit**, permettant d’explorer l’histoire de la **Coupe d’Afrique des Nations**, les performances des nations africaines, les buteurs, les tendances statistiques et les données avancées.

🎯 **Objectif :** proposer un outil premium, moderne, fun et puissant pour analyser la CAN sous un angle Data.

---

## 🚀 Fonctionnalités principales

### ⚔️ Comparateur de nations

Comparer deux nations africaines sur :

* confrontations directes
* forme récente (12 derniers mois)
* statistiques CAN *phase finale uniquement*
* Graphiques : radar, barres, heatmaps
* résultats offensifs / défensifs

---

### 🐘 Focus pays — Analyse ultra détaillée

Pour chaque sélection :

* Palmarès complet
* Participation par édition
* Meilleurs classements
* Analyse buteurs historiques
* Visualisations interactives
* Évolution des performances

---

### 📊 Bar Chart Race — Buteurs par édition

Animation dynamique style :

* BBC
* Elastic Motion
* Classic Race

Filtres disponibles : année, pays, top N.

---

### 🇲🇦 Page spéciale CAN 2025

Inclut :

* calendrier complet officiel
* groupes A–F
* formats & règles CAF
* fonctionnement des meilleurs troisièmes
* tableau des éliminatoires
* stades, villes & ambiance du tournoi

---

### 🧠 Statistiques avancées CAN

* équipe la plus régulière
* meilleure attaque 2024
* meilleure défense 2024
* match le plus prolifique
* score le plus fréquent
* tendances historiques (longue période)

---

## 📂 Structure du projet

```
afcon-dashboard/
│── app.py
│── README.md
│── requirements.txt
│── data/
│   ├── afcon_results.csv
│   ├── afcon_goalscorers.csv
│── modules/
│   ├── home.py
│   ├── compare.py
│   ├── analyse_pays_can.py
│   ├── barchart_buteurs_advanced.py
│   ├── can2025_info.py
│── assets/
│   ├── logo.png
│   ├── drapeaux/
└── .streamlit/
    ├── config.toml
```

---

## 💻 Installation & exécution

### 1️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2️⃣ Lancer l’application

```bash
streamlit run app.py
```

---

## ☁️ Déploiement sur Streamlit Cloud

1. Pousser le projet sur GitHub
2. Aller sur **[https://streamlit.io/cloud](https://streamlit.io/cloud)**
3. “New App” → sélectionner ton repo
4. Déclarer `app.py` comme fichier principal
5. Vérifier la présence de `requirements.txt`

L’application sera déployée sur une URL du type :

```
https://<nom-du-projet>.streamlit.app
```

---

## 📦 requirements.txt (exemple)

```txt
streamlit==1.51.0
pandas
numpy
plotly
```

Ajoute toute autre lib utilisée dans tes modules (ex : pillow, seaborn...).

---

## 🧠 Jeu de données

Les datasets suivants ont été nettoyés et utilisés :

* **afcon_results.csv** : résultats historiques (CAN + qualifs)
* **afcon_goalscorers.csv** : buteurs par édition

---

## 🔮 Améliorations futures

* Simulation CAN 2025 (Elo + Monte Carlo)
* Page "Classement Buteurs — All Time"
* Intégration d’une map interactive Afrique
* Timeline animée “Histoire de la CAN”
* Mode sombre premium
* Version mobile optimisée

---

## 👨‍💻 Auteur

**Hamed SAVADOGO**
Data Engineer & Data Analyst
📧 [hamedsavadogo158@gmail.com](mailto:hamedsavadogo158@gmail.com)

---

## ⭐ Support

Laisse une ⭐ sur le repo GitHub si tu veux soutenir le projet !

---

# 🎉 Merci d'utiliser AFCON Analytics Dashboard !
