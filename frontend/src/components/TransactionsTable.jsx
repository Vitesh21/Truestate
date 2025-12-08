import React, { useRef } from 'react'

export default function TransactionsTable({ rows }) {
  const containerRef = useRef(null)

  function scrollLeft() {
    if (!containerRef.current) return
    containerRef.current.scrollBy({ left: -300, behavior: 'smooth' })
  }

  function scrollRight() {
    if (!containerRef.current) return
    containerRef.current.scrollBy({ left: 300, behavior: 'smooth' })
  }

  return (
    <div className="table-wrap" style={{ marginTop: '50px' }}>
      <div className="table-scroll-controls">
        <button onClick={scrollLeft} aria-label="Scroll left">◀</button>
        <button onClick={scrollRight} aria-label="Scroll right">▶</button>
      </div>
      <div className="table-container" ref={containerRef}>
        <table className="transactions">
          <thead>
            <tr>
              <th>Transaction ID</th>
              <th>Date</th>
              <th>Customer ID</th>
              <th>Customer Name</th>
              <th>Phone</th>
              <th>Gender</th>
              <th>Age</th>
              <th>Product Category</th>
              <th>Quantity</th>
              <th>Total Amount</th>
              <th>Region</th>
              <th>Product ID</th>
              <th>Employee Name</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                <td>{r.TransactionID}</td>
                <td>{r.Date ? new Date(r.Date).toLocaleDateString() : ''}</td>
                <td>{r.CustomerID}</td>
                <td>{r.CustomerName}</td>
                <td>{r.PhoneNumber}</td>
                <td>{r.Gender}</td>
                <td>{r.Age}</td>
                <td>{r.ProductCategory}</td>
                <td>{r.Quantity}</td>
                <td>{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(r.TotalAmount)}</td>
                <td>{r.CustomerRegion}</td>
                <td>{r.ProductID}</td>
                <td>{r.EmployeeName}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
