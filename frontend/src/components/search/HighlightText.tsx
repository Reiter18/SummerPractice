import React from 'react'

interface HighlightTextProps {
  text: string
  query: string
}

export const HighlightText: React.FC<HighlightTextProps> = ({ text, query }) => {
  if (!query || !query.trim()) {
    return <span>{text}</span>
  }

  const escapedQuery = query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

  const words = escapedQuery.split(/\s+/).filter(w => w.length > 0)

  if (words.length === 0) {
    return <span>{text}</span>
  }

  const pattern = words.map(w => `(${w})`).join('|')
  const regex = new RegExp(pattern, 'gi')

  const parts = text.split(regex)

  return (
    <span>
      {parts.map((part, index) => {
        const isMatch = words.some(w =>
          part.toLowerCase() === w.toLowerCase()
        )

        return isMatch ? (
          <mark key={index} className="bg-yellow-200 rounded px-0.5">
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        )
      })}
    </span>
  )
}