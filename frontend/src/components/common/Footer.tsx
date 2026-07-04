import React from 'react'

interface FooterProps {
  year?: number
  companyName?: string
}

export const Footer: React.FC<FooterProps> = ({
  year = new Date().getFullYear()
}) => {
  return (
    <footer className="bg-white border-t border-gray-200 py-4 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-2 text-xs sm:text-sm text-gray-500">
          <span>© {year} Поиск по базе знаний</span>
          <div className="flex items-center gap-4">
            <span>Версия 1.0.0</span>
          </div>
        </div>
      </div>
    </footer>
  )
}