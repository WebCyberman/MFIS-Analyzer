
# MFIS-Analyzer

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.x-green.svg)
![PyQtGraph](https://img.shields.io/badge/PyQtGraph-Latest-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Description

MFIS-Analyzer est une application d'analyse audio développée en Python permettant de mesurer et visualiser la réponse fréquentielle d'un système audio à partir de différents signaux de test.

Le projet combine :

- Acquisition audio Full Duplex
- Traitement numérique du signal (DSP)
- Analyse fréquentielle FFT
- Diagrammes de Bode
- Diagrammes de Nyquist
- Interface graphique moderne basée sur Qt

L'objectif est de fournir une base extensible pour les mesures acoustiques, les expérimentations DSP et l'analyse de systèmes audio.

---

## Fonctionnalités

### Acquisition audio

- Détection automatique des périphériques audio
- Sélection indépendante de l'entrée et de la sortie
- Acquisition Full Duplex
- Support des interfaces audio USB
- Compatibilité Windows

### Génération de signaux de test

- Logarithmic Sweep
- White Noise
- Pink Noise

### Analyse DSP

- FFT (Fast Fourier Transform)
- Fonction de transfert
- Diagramme de Bode (Amplitude)
- Diagramme de Bode (Phase)
- Diagramme de Nyquist
- Statistiques du signal

### Interface graphique

- PySide6
- PyQtGraph
- Zoom et déplacement interactifs
- Graphiques haute performance
- Barre de progression
- Journal des opérations
- Gestion multithread via QThread

### Export

- Export CSV des résultats
- Architecture prête pour l'export PNG et JSON

---

# Captures d'écran

## Interface principale

![Fenêtre principale](screens/Capture%20d'écran%202026-11-12%20214023.png)

---

# Architecture

```text
MFIS-Analyzer/
│
├── main.py
├── models.py
├── audio.py
├── dsp.py
├── workers.py
│
└── ui/
    ├── __init__.py
    ├── main_window.py
    ├── plots.py
    └── widgets.py
```

---

# Description des modules

## main.py

Point d'entrée de l'application.

Responsabilités :

- Création de QApplication
- Gestion globale des exceptions
- Ouverture de la fenêtre principale

---

## models.py

Contient toutes les structures de données du projet :

- AudioDevice
- MeasurementConfig
- MeasurementData
- FFTResult
- BodeResult
- NyquistResult
- AnalysisResult
- ProgressInfo
- ErrorInfo

---

## audio.py

Gestion audio :

- Détection des périphériques
- Génération des signaux de test
- Acquisition Full Duplex
- Interface SoundDevice

Classes principales :

- AudioDeviceManager
- SignalGenerator
- AudioRecorder

---

## dsp.py

Traitement numérique du signal :

- FFT
- Fonction de transfert
- Diagrammes de Bode
- Diagramme de Nyquist
- Statistiques
- Export CSV

Classes principales :

- FFTAnalyzer
- BodeAnalyzer
- NyquistAnalyzer
- StatisticsAnalyzer
- MeasurementAnalyzer

---

## workers.py

Gestion du multithreading Qt :

- AcquisitionWorker
- AnalysisWorker
- WorkerManager

Responsabilités :

- Exécuter l'acquisition audio dans un thread dédié
- Exécuter l'analyse DSP dans un thread dédié
- Communiquer avec l'interface graphique via les signaux Qt

---

## ui/widgets.py

Composants réutilisables :

- DeviceSelectorWidget
- MeasurementConfigWidget
- ControlWidget
- StatusWidget
- LogWidget

---

## ui/plots.py

Affichage temps réel :

- FFT
- Bode Amplitude
- Bode Phase
- Nyquist

Technologie utilisée :

- PyQtGraph

---

## ui/main_window.py

Fenêtre principale de l'application.

Responsabilités :

- Connexion des widgets
- Gestion des mesures
- Gestion de l'export
- Affichage des résultats

---

# Installation

## Clonage du dépôt

```bash
git clone https://github.com/WebCyberman/MFIS-Analyzer.git

cd MFIS-Analyzer
```

---

## Création de l'environnement virtuel

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Installation des dépendances

```bash
pip install -r requirements.txt
```

Ou manuellement :

```bash
pip install PySide6
pip install pyqtgraph
pip install numpy
pip install scipy
pip install sounddevice
```

---

# Lancement

```bash
python main.py
```

---

# Utilisation

## Étape 1

Sélectionner :

- Le pé---

## Étape 2

Choisir :

- Log Sweep
- White Noise
- Pink Noise

---

## Étape 3

Configurer :

- Fréquence d'échantillonnage
- Durée
- Amplitude

---

## Étape 4

Cliquer sur :

```text
Lancer
```

---

## Étape 5

Consulter :

- FFT
- Bode Amplitude
- Bode Phase
- Nyquist

---

## Étape 6

Exporter les données au format CSV.

---

# Dépendances

| Bibliothèque | Rôle |
|-------------|------|
| PySide6 | Interface graphique |
| PyQtGraph | Visualisation |
| NumPy | Calcul scientifique |
| SciPy | DSP |
| SoundDevice | Acquisition audio |

---

# Roadmap

## DSP

- Réponse impulsionnelle
- Analyse harmonique
- THD
- THD+N
- Compensation automatique de latence
- Calibration

## Interface

- Thème sombre avancé
- Sauvegarde des configurations
- Historique des mesures
- Sessions utilisateur

## Visualisation

- Spectrogramme temps réel
- Waterfall
- Affichage temporel
- Analyse spectrale live

---

# Développement

Pour contribuer :

```bash
git checkout -b ma-branche
```

Puis :

```bash
git add .

git commit -m "Description des modifications"

git push origin ma-branche
```

Créer ensuite une Pull Request.

---

# Licence

Ce projet est distribué sous licence MIT.

---

# Auteur

**WebCyberman**

Projet d'expérimentation et d'analyse audio basé sur Python, Qt et le traitement numérique du signal.
