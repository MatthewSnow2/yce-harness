interface StatusBadgeProps {
  status: 'active' | 'completed' | 'pending'
}

function StatusBadge({ status }: StatusBadgeProps) {
  const colorClasses = {
    active: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        colorClasses[status] || colorClasses.pending
      }`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default StatusBadge
