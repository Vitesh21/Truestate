import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function FilterPanel({ onChange }) {
  const [region, setRegion] = useState([])
  const [gender, setGender] = useState([])
  const [ageMin, setAgeMin] = useState('')
  const [ageMax, setAgeMax] = useState('')
  const [productCategories, setProductCategories] = useState([])
  const [tags, setTags] = useState([])
  const [paymentMethods, setPaymentMethods] = useState([])
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [availableOptions, setAvailableOptions] = useState({
    regions: [],
    categories: [],
    tags: [],
    paymentMethods: []
  })

  // Fetch available filter options
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 3;

    async function fetchOptions() {
      try {
        const res = await axios.get(`${API}/api/transactions/filter-options`, {
          timeout: 10000 // Reduced timeout since it should be fast now
        })
        const options = res.data || {}
        setAvailableOptions({
          regions: options.regions || [],
          categories: options.productCategories || [],
          tags: options.tags || [],
          paymentMethods: options.paymentMethods || []
        })

        // If options are empty, retry after a delay (data might still be loading)
        if (options.regions.length === 0 && retryCount < maxRetries) {
          retryCount++;
          setTimeout(fetchOptions, 5000); // Retry after 5 seconds
        }
      } catch (err) {
        console.warn('Could not load filter options:', err.message)
        // Fallback to default values if API fails
        setAvailableOptions({
          regions: ['North', 'South', 'East', 'West', 'Central'],
          categories: [],
          tags: [],
          paymentMethods: ['UPI', 'Credit Card', 'Debit Card', 'Cash', 'Wallet']
        })

        // Retry if connection error
        if (err.code === 'ECONNABORTED' || err.code === 'ECONNREFUSED') {
          if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(fetchOptions, 3000); // Retry after 3 seconds
          }
        }
      }
    }
    fetchOptions()
  }, [])

  function toggle(arr, v) {
    return arr.includes(v) ? arr.filter(x => x !== v) : [...arr, v]
  }

  function apply() {
    const filters = {}
    if (region.length) filters.customerRegions = region
    if (gender.length) filters.genders = gender
    if (ageMin || ageMax) {
      filters.ageRange = {
        min: ageMin ? Number(ageMin) : undefined,
        max: ageMax ? Number(ageMax) : undefined
      }
    }
    if (productCategories.length) filters.productCategories = productCategories
    if (tags.length) filters.tags = tags
    if (paymentMethods.length) filters.paymentMethods = paymentMethods
    if (dateFrom || dateTo) {
      filters.dateRange = {
        from: dateFrom || undefined,
        to: dateTo || undefined
      }
    }
    onChange(filters)
  }

  function clear() {
    setRegion([])
    setGender([])
    setAgeMin('')
    setAgeMax('')
    setProductCategories([])
    setTags([])
    setPaymentMethods([])
    setDateFrom('')
    setDateTo('')
    onChange({})
  }

  return (
    <div className="filters">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h4>Filters</h4>
        <button onClick={clear} style={{ fontSize: '12px', padding: '4px 8px' }}>Clear All</button>
      </div>

      <div className="filter-group">
        <label>Customer Region:</label>
        <div className="filter-buttons">
          {availableOptions.regions.length > 0 ? (
            availableOptions.regions.map(r => (
              <button
                key={r}
                onClick={() => setRegion(toggle(region, r))}
                className={region.includes(r) ? 'active' : ''}
              >
                {r}
              </button>
            ))
          ) : (
            <>
              <button onClick={() => setRegion(toggle(region, 'North'))} className={region.includes('North') ? 'active' : ''}>North</button>
              <button onClick={() => setRegion(toggle(region, 'South'))} className={region.includes('South') ? 'active' : ''}>South</button>
              <button onClick={() => setRegion(toggle(region, 'East'))} className={region.includes('East') ? 'active' : ''}>East</button>
              <button onClick={() => setRegion(toggle(region, 'West'))} className={region.includes('West') ? 'active' : ''}>West</button>
              <button onClick={() => setRegion(toggle(region, 'Central'))} className={region.includes('Central') ? 'active' : ''}>Central</button>
            </>
          )}
        </div>
      </div>

      <div className="filter-group">
        <label>Gender:</label>
        <div className="filter-buttons">
          <button onClick={() => setGender(toggle(gender, 'Male'))} className={gender.includes('Male') ? 'active' : ''}>Male</button>
          <button onClick={() => setGender(toggle(gender, 'Female'))} className={gender.includes('Female') ? 'active' : ''}>Female</button>
        </div>
      </div>

      <div className="filter-group">
        <label>Age Range:</label>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="number"
            placeholder="Min"
            value={ageMin}
            onChange={e => setAgeMin(e.target.value)}
            style={{ width: '80px', padding: '4px' }}
          />
          <input
            type="number"
            placeholder="Max"
            value={ageMax}
            onChange={e => setAgeMax(e.target.value)}
            style={{ width: '80px', padding: '4px' }}
          />
        </div>
      </div>

      <div className="filter-group">
        <label>Product Category:</label>
        <div className="filter-buttons" style={{ maxHeight: '120px', overflowY: 'auto' }}>
          {availableOptions.categories.length > 0 ? (
            availableOptions.categories.map(cat => (
              <button
                key={cat}
                onClick={() => setProductCategories(toggle(productCategories, cat))}
                className={productCategories.includes(cat) ? 'active' : ''}
              >
                {cat}
              </button>
            ))
          ) : (
            <div style={{ fontSize: '12px', color: '#666' }}>Loading...</div>
          )}
        </div>
      </div>

      <div className="filter-group">
        <label>Tags:</label>
        <div className="filter-buttons" style={{ maxHeight: '120px', overflowY: 'auto' }}>
          {availableOptions.tags.length > 0 ? (
            availableOptions.tags.map(tag => (
              <button
                key={tag}
                onClick={() => setTags(toggle(tags, tag))}
                className={tags.includes(tag) ? 'active' : ''}
              >
                {tag}
              </button>
            ))
          ) : (
            <div style={{ fontSize: '12px', color: '#666' }}>Loading...</div>
          )}
        </div>
      </div>

      <div className="filter-group">
        <label>Payment Method:</label>
        <div className="filter-buttons">
          {availableOptions.paymentMethods.length > 0 ? (
            availableOptions.paymentMethods.map(method => (
              <button
                key={method}
                onClick={() => setPaymentMethods(toggle(paymentMethods, method))}
                className={paymentMethods.includes(method) ? 'active' : ''}
              >
                {method}
              </button>
            ))
          ) : (
            <div style={{ fontSize: '12px', color: '#666' }}>Loading...</div>
          )}
        </div>
      </div>

      <div className="filter-group">
        <label>Date Range:</label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <input
            type="date"
            placeholder="From"
            value={dateFrom}
            onChange={e => setDateFrom(e.target.value)}
            style={{ padding: '4px' }}
          />
          <input
            type="date"
            placeholder="To"
            value={dateTo}
            onChange={e => setDateTo(e.target.value)}
            style={{ padding: '4px' }}
          />
        </div>
      </div>

      <div style={{ marginTop: '12px' }}>
        <button onClick={apply} style={{ width: '100%', padding: '8px', fontWeight: 'bold' }}>Apply Filters</button>
      </div>
    </div>
  )
}
