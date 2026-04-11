import React from 'react'
import PropTypes from 'prop-types'

const SummaryCard = ({ 
  icon: Icon, 
  label, 
  value, 
  color = 'blue', 
  className = '' 
}) => {
  const colors = {
    blue: 'bg-gradient-to-br from-blue-500 to-indigo-600',
    green: 'bg-gradient-to-br from-emerald-500 to-teal-600',
    orange: 'bg-gradient-to-br from-orange-500 to-amber-600',
    purple: 'bg-gradient-to-br from-purple-500 to-violet-600'
  }

  return (
    <div className={`stat-card ${className}`}>
      <div className={`stat-icon ${colors[color] || colors.blue}`}>
        <Icon size={24} />
      </div>
      <div className="stat-info">
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
      </div>
    </div>
  )
}

SummaryCard.propTypes = {
  icon: PropTypes.elementType.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  color: PropTypes.oneOf(['blue', 'green', 'orange', 'purple']),
  className: PropTypes.string
}

export default SummaryCard

