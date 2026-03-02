import type { Item } from '../lib/api'
import StatusBadge from './StatusBadge'

interface ItemCardProps {
  item: Item
  onClick: (item: Item) => void
}

function ItemCard({ item, onClick }: ItemCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div
      onClick={() => onClick(item)}
      className="bg-white rounded-lg shadow border border-gray-200 p-5 hover:shadow-md hover:border-primary transition-all cursor-pointer"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
        <StatusBadge status={item.status} />
      </div>

      {item.description && (
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {item.description}
        </p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Created: {formatDate(item.created_at)}</span>
        {item.user && <span>By: {item.user.name}</span>}
      </div>
    </div>
  )
}

export default ItemCard
