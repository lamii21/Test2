# 📥 GUIDE DE TÉLÉCHARGEMENT - Component Data Processor v2.0

## 🎯 **FICHIER PRINCIPAL À TÉLÉCHARGER**

### ⭐ **`Update_YYYY-MM-DD.xlsx`** ← **C'EST VOTRE FICHIER !**

**Ce fichier contient :**
- ✅ **VOS données d'origine** (celles que vous avez uploadées)
- ✅ **Informations du Master BOM ajoutées** selon le projet sélectionné :
  - `Status` : Statut du composant (D, X, etc.)
  - `Description` : Description du composant
  - `Price` : Prix (si disponible)
  - `Supplier` : Fournisseur (si disponible)
- ✅ **Colonnes de traitement** : Action, Notes, etc.

**Exemple de nom :** `Update_2025-08-05.xlsx`

---

## 📁 **AUTRES FICHIERS DISPONIBLES**

### 🗄️ **`Master_BOM_Updated_YYYY-MM-DD.xlsx`**
- **Contenu :** Master BOM complet mis à jour
- **Usage :** Fichier de référence pour l'équipe
- **Taille :** ~1 MB (beaucoup plus gros)

### 📈 **`Processing_Summary_YYYY-MM-DD.csv`**
- **Contenu :** Statistiques du traitement
- **Usage :** Rapport pour analyse
- **Format :** CSV

---

## 🌐 **COMMENT TÉLÉCHARGER**

### **Via Interface Web :**
1. **Allez sur :** http://localhost:5000/results
2. **Cherchez le fichier avec :**
   - ⭐ **Icône étoile dorée**
   - 🟢 **Bordure verte et fond clair**
   - 🏷️ **Badge "FICHIER PRINCIPAL"**
   - 📝 **Description "VOS DONNÉES enrichies..."**
3. **Cliquez sur :** "Télécharger Principal"

### **Via URL Directe :**
- **Format :** `http://localhost:5000/download/Update_YYYY-MM-DD.xlsx`
- **Exemple :** http://localhost:5000/download/Update_2025-08-05.xlsx

---

## 🔍 **COMMENT IDENTIFIER LE BON FICHIER**

### ✅ **Fichier Principal (à télécharger) :**
```
Nom : Update_2025-08-05.xlsx
Taille : ~75 KB (relativement petit)
Contenu : VOS données + informations Master BOM
```

### ❌ **Fichier à NE PAS télécharger (sauf besoin spécifique) :**
```
Nom : Master_BOM_Updated_2025-08-05.xlsx
Taille : ~1 MB (beaucoup plus gros)
Contenu : Master BOM complet (pas vos données)
```

---

## 📊 **CONTENU DU FICHIER PRINCIPAL**

Votre fichier `Update_YYYY-MM-DD.xlsx` contient vos colonnes d'origine plus :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `PN` | Numéro de pièce | ABC123 |
| `Project` | Projet sélectionné | V710_AWD_PP_YOTK |
| `Status` | Statut du Master BOM | D, X, etc. |
| `Description` | Description du composant | Connector 5-pin |
| `Price` | Prix (si disponible) | 1.25 |
| `Supplier` | Fournisseur (si disponible) | Supplier A |
| `Action` | Action de traitement | Added, Updated |
| `Notes` | Notes du traitement | New component |

---

## 🚀 **ACCÈS RAPIDE**

### **🌐 Interface Web :**
- **Page principale :** http://localhost:5000
- **Page résultats :** http://localhost:5000/results
- **Interface avancée :** http://localhost:5000/enhanced

### **📡 API Directe :**
- **Liste des fichiers :** http://localhost:8000/list-outputs
- **Téléchargement direct :** http://localhost:8000/download/Update_2025-08-05.xlsx

---

## ❓ **FAQ**

### **Q: Quel fichier contient mes données avec les informations du Master BOM ?**
**R:** Le fichier `Update_YYYY-MM-DD.xlsx` (avec l'icône étoile dorée)

### **Q: Pourquoi y a-t-il plusieurs fichiers ?**
**R:** 
- `Update_*.xlsx` = VOS données enrichies (à télécharger)
- `Master_BOM_Updated_*.xlsx` = Master BOM complet (référence)
- `Processing_Summary_*.csv` = Statistiques (rapport)

### **Q: Comment savoir si c'est le bon fichier ?**
**R:** Vérifiez :
- ✅ Nom commence par "Update_"
- ✅ Taille relativement petite (~75 KB)
- ✅ Icône étoile dorée dans l'interface
- ✅ Badge "FICHIER PRINCIPAL"

### **Q: Le fichier contient-il les informations du projet sélectionné ?**
**R:** Oui ! Le lookup est fait avec la colonne de projet que vous avez sélectionnée lors du traitement.

---

## 🎯 **RÉSUMÉ**

**TÉLÉCHARGEZ :** `Update_YYYY-MM-DD.xlsx` (icône ⭐)
**CONTIENT :** Vos données + informations Master BOM selon le projet
**ACCÈS :** http://localhost:5000/results → Bouton "Télécharger Principal"

🎉 **C'est votre fichier de résultat final !**
