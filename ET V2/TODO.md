# ET V2 - V1 UI Migration TODO

## Progress
- [x] Backend stable (OCR/parser safe)
- [ ] Copy V1 UI files
- [ ] Backend /health + manual expense  
- [ ] Frontend deps (react-dropzone, lucide-react)
- [ ] npm install + vite restart
- [ ] Test full V1 UI + V2 backend

## Steps
1. Backend endpoints (/health, manual expense)
2. Frontend src/api/API.js (V1)
3. src/pages/UploadPage.jsx/css → overwrite V2
4. src/pages/DashboardPage.jsx/css → Dashboard.jsx  
5. src/App.jsx → V1 layout (no auth)
6. src/index.css → V1 vars  
7. package.json deps + npm i

**Next: Backend /health**

