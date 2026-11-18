# Assets du profil

Les SVG de `assets/` sont générés par `build_assets.py` (texte converti en tracés, animations SMIL/CSS, rien d'externe).

```bash
pip install fonttools
python tools/build_assets.py
```

Pour changer un projet, une techno ou un texte : modifier le bloc `DONNÉES` en haut du script, puis relancer.

- Polices (SIL Open Font License) : Bebas Neue, Share Tech Mono, DotGothic16, Inter.
- Icônes : Simple Icons (CC0), chemins copiés dans `icons.json`.
