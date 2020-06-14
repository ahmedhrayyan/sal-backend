import React from 'react';

interface Props {
  className: string
}

function Spinner({ className }: Props) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 60 60"
        aria-labelledby="spinner-title"
        role="graphic"
        className="spinner"
      >
        <title id="spinner-title">Loading...</title>
        <circle className="spinner-circle" cx="30" cy="30" r="24"></circle>
        <circle className="spinner-semi-circle" cx="30" cy="30" r="24"></circle>
      </svg>
    </div>
  )
}

export default Spinner;
