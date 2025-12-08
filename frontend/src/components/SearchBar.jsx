import React, { useState } from 'react'

export default function SearchBar({ onSearch }) {
  const [val, setVal] = useState('')
  
  function handleKeyPress(e) {
    if (e.key === 'Enter') {
      onSearch(val)
    }
  }
  
  return (
    <div className="searchbar">
      <input 
        placeholder="Search by Customer Name or Phone Number" 
        value={val} 
        onChange={e => setVal(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <button onClick={() => onSearch(val)}>Search</button>
    </div>
  )
}
