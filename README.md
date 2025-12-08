Overview

This project implements a Retail Sales Management System for the TruEstate SDE intern assignment. It provides a backend API that reads the provided CSV dataset and a minimal frontend that demonstrates search, filtering, sorting, and pagination over transactions.

Tech Stack

- Backend: Node.js, Express, csvtojson
- Frontend: React (Vite)
- Dev: nodemon, CORS

Search Implementation Summary

Full-text search is implemented server-side over `CustomerName` and `PhoneNumber`. Search is case-insensitive and combined with filters, sorting, and pagination on the backend so the frontend can request consistent paged results.

Filter Implementation Summary

Filters are implemented server-side and support multi-select for Customer Region, Gender, Product Category, Tags, Payment Method and range filters for Age and Date. Filters are passed as a JSON string in the `filters` query parameter.

Sorting Implementation Summary

Sorting is server-side. The API accepts `sortField` and `sortDir` query params. Supported sorts include `Date` (newest first), `Quantity`, and `CustomerName` (A–Z).

Pagination Implementation Summary

Pagination is server-side with `page` and `pageSize` query params. Default `pageSize` is 10. API returns `{ data, page, pageSize, total }` so the frontend can render pagination controls.

Setup Instructions

1. Install dependencies for backend and frontend.

```powershell
cd backend
npm install
cd ..\frontend
npm install
```

2. Run backend (port 4000) and frontend (port 5173 default for Vite):

```powershell
cd backend; npm run dev
cd ..\frontend; npm run dev
```

The backend reads the dataset file `truestate_assignment_dataset.csv` located at the repository root.
