import React, { useEffect, useState } from 'react'
import axios from 'axios'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/FilterPanel'
import TransactionsTable from './components/TransactionsTable'
import Pagination from './components/Pagination'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [q, setQ] = useState('')
  const [filters, setFilters] = useState({})
  const [sortField, setSortField] = useState('Date')
  const [sortDir, setSortDir] = useState('desc')
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [data, setData] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { fetchData() }, [q, filters, sortField, sortDir, page])

  async function fetchData() {
    setLoading(true)
    setError(null)
    const params = {
      q,
      page,
      pageSize,
      sortField,
      sortDir,
      filters: JSON.stringify(filters)
    }
    const url = `${API}/api/transactions`

    try {
      const res = await axios.get(url, {
        params,
        timeout: 60000, // Increased timeout for large CSV loading
        headers: {
          'Content-Type': 'application/json'
        }
      })
      setData(res.data.data || [])
      setTotal(res.data.total || 0)
    } catch (err) {
      console.error('API fetch error:', err)
      let message = 'Failed to fetch data'

      if (err.code === 'ECONNABORTED') {
        message = 'Request timeout. Please check if the backend server is running on port 8000.'
      } else if (err.code === 'ECONNREFUSED') {
        message = 'Cannot connect to backend server. Please ensure the backend is running on port 8000.'
      } else if (err.response) {
        message = err.response.data?.error || err.response.statusText || `Server error: ${err.response.status}`
      } else if (err.message) {
        message = err.message
      }

      setError(message)
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  function onSearch(val) { setPage(1); setQ(val) }
  function onFiltersChange(f) { setPage(1); setFilters(f) }
  function onSortChange(field, dir) { setSortField(field); setSortDir(dir) }
  function onPageChange(p) { setPage(p) }

  return (
    <div className="app">
      <header className="topbar">Sales Management System</header>
      <div className="controls">
        <SearchBar onSearch={onSearch} />
        <div className="sort">
          <label>Sort by: </label>
          <select value={`${sortField}-${sortDir}`} onChange={e => {
            const [field, dir] = e.target.value.split('-')
            onSortChange(field, dir)
          }}>
            <option value="Date-desc">Date (Newest First)</option>
            <option value="Date-asc">Date (Oldest First)</option>
            <option value="Quantity-desc">Quantity (High to Low)</option>
            <option value="Quantity-asc">Quantity (Low to High)</option>
            <option value="CustomerName-asc">Customer Name (A–Z)</option>
            <option value="CustomerName-desc">Customer Name (Z–A)</option>
          </select>
        </div>
      </div>
      <div className="main">
        <aside><FilterPanel onChange={onFiltersChange} /></aside>
        <section>
          <div className="stats">Total: {total}</div>
          {loading && <div className="loading">Loading...</div>}
          {error && <div className="error">Error: {error}</div>}
          {!loading && !error && (
            <>
              <TransactionsTable rows={data} />
              <Pagination page={page} pageSize={pageSize} total={total} onPageChange={onPageChange} />
            </>
          )}
        </section>
      </div>
    </div>
  )
}
