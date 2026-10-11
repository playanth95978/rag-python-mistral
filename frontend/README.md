# Interface Mistral

React + Vite + Tailwind CSS. La clé Mistral est configurée uniquement dans le backend.

```powershell
npm ci
npm run dev
```

FastAPI doit tourner sur http://127.0.0.1:8001. Le proxy Vite transmet les requêtes `/api`.
`API_PROXY_TARGET` permet de modifier cette adresse côté serveur de développement.

- `/` : chat Mistral avec conversations sauvegardées dans le navigateur.
- `/admin/vespa` : consultation des collections, recherche textuelle et détails des vecteurs.
- `src/lib/api.js` : tous les appels au backend.

```powershell
npm run build
npm test
```

Le build est généré dans `../app/static/ui` et servi par FastAPI aux mêmes routes.
Les dépendances sont verrouillées par `package-lock.json` ; utiliser `npm ci` pour les réinstaller.
