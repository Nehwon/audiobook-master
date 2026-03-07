# Matrice des formats audio supportés

Cette matrice décrit les formats **réellement pris en charge aujourd'hui** par le pipeline (CLI + Web), en se basant sur l'implémentation courante.

## Sortie cible

- **Format de sortie unique**: `.m4b` (AAC encapsulé MP4/M4B).
- Upload Audiobookshelf: le client d'intégration envoie le fichier en `audio/m4b`.

## Entrées audio (dossiers source)

| Extension | Détection Web (bibliothèque) | Exploitable par le processeur | Notes / contraintes |
|---|---:|---:|---|
| `.mp3` | ✅ | ✅ | Cas nominal.
| `.m4a` | ✅ | ✅ | Pris en charge en entrée.
| `.wav` | ✅ | ✅ | Pris en charge en entrée.
| `.flac` | ✅ | ✅ | Pris en charge en entrée.
| `.aac` | ✅ | ✅ | Pris en charge en entrée.
| `.m4b` | ✅ | ⚠️ partiel | Détecté côté Web; le processeur peut l'inspecter mais le dossier source contenant déjà des `.m4b` est considéré non conforme pour reconversion.
| `.ogg` | ✅ | ❌ | Visible côté Web mais non retenu comme "audio exploitable" par le pipeline actuel.

## Archives en entrée

| Extension | Validation | Extraction | Contraintes |
|---|---:|---:|---|
| `.zip` | ✅ | ✅ | Rejet des ZIP vides, protégés par mot de passe, ou corrompus.
| `.rar` | ✅ | ✅ | Rejet des RAR vides, protégés par mot de passe, ou corrompus.
| autre | ❌ | ❌ | Format non supporté.

## Contraintes techniques importantes

- Outils requis: `ffmpeg` et `ffprobe` disponibles dans le `PATH`.
- Encodage cible: AAC (`-c:a aac`) avec bitrate et sample rate configurables.
- Modes de traitement disponibles: `concat_fast`, `encode_aac`, `final_m4b`.
- La présence d'un `.m4b` déjà généré dans un dossier source peut entraîner son exclusion du flux de conversion (comportement de protection).

## Paramètres de sortie (config)

- Bitrates disponibles: `64k`, `96k`, `128k`, `160k`, `192k`, `256k`, `320k`.
- Sample rate par défaut: `44100` (configurable).

## Périmètre

- Cette matrice reflète l'état actuel du code et doit être mise à jour à chaque évolution des extensions gérées dans `core` et `web`.
