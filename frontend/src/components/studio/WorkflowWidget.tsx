import { ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'
import { ReactNode } from 'react'

interface WorkflowWidgetProps {
  title: string
  subtitle?: string
  collapsed: boolean
  onToggle: () => void
  children: ReactNode
}

export default function WorkflowWidget({
  title,
  subtitle,
  collapsed,
  onToggle,
  children,
}: WorkflowWidgetProps) {
  return (
    <section className="rounded-xl border border-space-600 bg-space-800/70">
      <button
        type="button"
        onClick={onToggle}
        className={clsx(
          'w-full px-3 py-2 flex items-center justify-between text-left',
          'hover:bg-space-700/60 transition-colors rounded-xl',
        )}
      >
        <span>
          <span className="block text-sm font-semibold">{title}</span>
          {subtitle ? <span className="block text-xs text-gray-400">{subtitle}</span> : null}
        </span>
        {collapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
      </button>
      {!collapsed ? <div className="px-3 pb-3">{children}</div> : null}
    </section>
  )
}
