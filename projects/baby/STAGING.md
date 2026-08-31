# Why this lives here

`baby` is meant to be its own repo (`hbschlac/baby`, private). It is staged inside
`hbschlac/hbschlac` only because the web session's GitHub integration cannot create
repositories — `POST /user/repos` returns `403 Resource not accessible by integration`.

## Moving it out

Once `hbschlac/baby` exists (create it empty and private, no README):

```bash
cd projects/baby
git init -b main
git add .
git commit -m "Baby: registry, names, and nursery planning"
git remote add origin git@github.com:hbschlac/baby.git
git push -u origin main
```

Then delete `projects/baby/` from this repo — including this file.
