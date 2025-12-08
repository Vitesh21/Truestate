# Architecture

## Backend Architecture

- Built with Node.js + Express.
- CSV file loader (`csvtojson`) reads `truestate_assignment_dataset.csv` into memory on first request. Data is normalized and cached for the server lifetime.
- Main modules:
  - `src/index.js` - Express entrypoint and route wiring.
  - `src/routes/transactions.js` - API route for `/api/transactions`.
  - `src/controllers/transactionsController.js` - Handles request parsing and response shaping (search, filter, sort, pagination orchestration).
  - `src/services/dataService.js` - Loads and normalizes CSV rows and provides helper methods for searching, filtering and sorting.

## Frontend Architecture

- Minimal React (Vite) single-page app that queries the backend API and renders UI components:
  - `src/components/SearchBar.jsx` - Search input.
  - `src/components/FilterPanel.jsx` - Filter controls (multi-selects and range inputs).
  - `src/components/TransactionsTable.jsx` - Table renderer for transaction rows.
  - `src/components/Pagination.jsx` - Next/Previous and page numbers.
  - `src/App.jsx` - Orchestrates state and composes components.

## Data Flow

1. Frontend sends requests to `GET /api/transactions` with query params: `page`, `pageSize`, `q`, `sortField`, `sortDir`, `filters`.
2. Backend loads CSV (cached), applies search -> filters -> sort -> pagination and returns JSON `{ data, page, pageSize, total }`.
3. Frontend consumes the response and updates UI state.

## Folder Structure

```
root/
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   └── services/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── App.jsx
├── docs/
│   └── architecture.md
├── truestate_assignment_dataset.csv
```

## Module Responsibilities

- `dataService` - single source of truth for CSV normalization and the core logic for filtering/sorting/searching. Ensures no duplicate logic between controllers and services.
- `transactionsController` - parse incoming query params and orchestrate pipeline.
- Frontend components - presentational and controlled components; they assemble filter state and call API.
