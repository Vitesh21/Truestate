import React from 'react'

export default function Pagination({ page, pageSize, total, onPageChange }) {
  const pages = Math.max(1, Math.ceil(total / pageSize))
  function prev() { if (page > 1) onPageChange(page - 1) }
  function next() { if (page < pages) onPageChange(page + 1) }
  return (
    <div className="pagination simple">
      <button onClick={prev} disabled={page === 1}>Prev</button>
      <span className="page-indicator">Page {page} of {pages}</span>
      <button onClick={next} disabled={page === pages}>Next</button>
    </div>
  )
}
