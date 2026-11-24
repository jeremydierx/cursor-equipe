# Composants tiers

Ce paquet est distribué sous licence MIT (voir `LICENSE`). Il reprend ou adapte des éléments des projets ci-dessous, dont les mentions de licence sont reproduites ici, comme ces licences l'exigent.

## BMad Builder

- Projet : BMad Builder, version 2.2.2, <https://github.com/bmad-code-org/bmad-builder>
- Licence : MIT, texte reproduit ci-dessous
- Repris à l'identique : `agents/devops/skill/references/prompt-quality-canon.md`
- Adaptés et traduits en français :
  - `agents/devops/skill/SKILL.md`
  - `agents/devops/skill/customize.toml`
  - `agents/devops/skill/assets/BOND-template.md`
  - `agents/devops/skill/assets/CAPABILITIES-template.md`
  - `agents/devops/skill/assets/CREED-template.md`
  - `agents/devops/skill/assets/INDEX-template.md`
  - `agents/devops/skill/assets/MEMORY-template.md`
  - `agents/devops/skill/assets/PERSONA-template.md`
  - `agents/devops/skill/references/capability-authoring.md`
  - `agents/devops/skill/references/first-breath.md`
  - `agents/devops/skill/references/memory-guidance.md`
  - `agents/devops/skill/scripts/init-sanctum.py`
  - `agents/devops/skill/scripts/wake.py`
  - `agents/devops/skill/scripts/tests/test-init-sanctum.py`
- Plus largement, la structure des agents (sanctuaire, réveil, premier souffle, capacités) suit celle des agents à mémoire de BMad Builder.

Ce paquet n'est ni affilié à BMad Code, LLC, ni soutenu par elle. Les marques BMad ne sont pas concédées par la licence ci-dessous.

```text
MIT License

Copyright (c) 2025 BMad Code, LLC

This project incorporates contributions from the open source community.
See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contributor attribution.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

TRADEMARK NOTICE:
BMad™, BMad Method™, and BMad Core™ are trademarks of BMad Code, LLC, covering all
casings and variations (including BMAD, bmad, BMadMethod, BMAD-METHOD, etc.). The use of
these trademarks in this software does not grant any rights to use the trademarks
for any other purpose. See [TRADEMARK.md](TRADEMARK.md) for detailed guidelines.
```

Les fichiers `CONTRIBUTORS.md` et `TRADEMARK.md` cités ci-dessus sont ceux du dépôt BMad Builder.

## keyring

- Projet : keyring, <https://github.com/jaraco/keyring>
- Licence : MIT
- Usage : bibliothèque Python que `uv` télécharge au premier lancement de `identifiant.py`. Elle n'est pas incluse dans ce paquet.
