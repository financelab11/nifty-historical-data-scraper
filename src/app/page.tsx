"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'

interface IndexData {
  date: string
  index_name: string
  open: number
  high: number
  low: number
  close: number
}

export default function Home() {
  const [data, setData] = useState<IndexData[]>([])
  const [loading, setLoading] = useState(true)

    useEffect(() => {
    async function fetchData() {
      setLoading(true)
      let offset = 0
      const limit = 1000
      let hasMore = true
      let allFetched: IndexData[] = []

      console.log("Starting data fetch...")

      while (hasMore) {
        const { data: records, error } = await supabase
          .from("nifty_momentum_50")
          .select("*")
          .order("date", { ascending: false })
          .range(offset, offset + limit - 1)

        if (error) {
          console.error("Error fetching data:", error)
          hasMore = false
        } else if (records && records.length > 0) {
          console.log(`Fetched ${records.length} records, offset ${offset}`)
          allFetched = [...allFetched, ...records]
          // Update state incrementally so the user sees something
          setData([...allFetched])
          
          if (records.length < limit) {
            hasMore = false
          } else {
            offset += limit
          }
        } else {
          hasMore = false
        }
      }

      setLoading(false)
      console.log(`Fetch complete. Total: ${allFetched.length} records.`)
    }

    fetchData()
  }, [])

  // No sampling for the chart for better accuracy, Recharts can handle ~5k points
  const getChartData = () => {
    if (data.length === 0) return []
    const reversed = [...data].reverse()
    return reversed.map(item => ({
      ...item,
      formattedDate: new Date(item.date).toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
    }))
  }

  const chartData = getChartData()

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-4 md:p-8 font-sans text-zinc-900 dark:text-zinc-100">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              Nifty500 Momentum 50
            </h1>
            <p className="text-zinc-500 dark:text-zinc-400">
              Complete Historical Performance (Since April 2005)
            </p>
          </div>
          <div className="flex items-center gap-3">
             <div className="bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 px-3 py-1 rounded-full text-xs font-medium border border-zinc-200 dark:border-zinc-800">
              {data.length.toLocaleString()} Records
            </div>
            <div className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-3 py-1 rounded-full text-xs font-medium border border-emerald-200 dark:border-emerald-800/50">
              Live Database
            </div>
          </div>
        </header>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-zinc-900 dark:border-zinc-100"></div>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                <p className="text-xs text-zinc-500 dark:text-zinc-400 uppercase font-bold tracking-wider mb-1">Latest Value</p>
                <p className="text-2xl font-bold tabular-nums">
                  {data[0]?.close.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
                <p className="text-xs text-zinc-400 mt-1">{new Date(data[0]?.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
              </div>
              <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                <p className="text-xs text-zinc-500 dark:text-zinc-400 uppercase font-bold tracking-wider mb-1">All-Time High</p>
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  {Math.max(...data.map(d => Number(d.high) || Number(d.close))).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                <p className="text-xs text-zinc-500 dark:text-zinc-400 uppercase font-bold tracking-wider mb-1">Base Value (2005)</p>
                <p className="text-2xl font-bold text-zinc-500 tabular-nums">
                  {data[data.length-1]?.close.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>

            {/* Chart Section */}
            <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold">Long-term Performance</h2>
                <span className="text-xs text-zinc-400">All data points since 2005</span>
              </div>
              <div className="h-[450px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" strokeOpacity={0.2} />
                    <XAxis 
                      dataKey="formattedDate" 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      minTickGap={80}
                      tick={{ fill: '#71717a' }}
                    />
                    <YAxis 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      domain={['auto', 'auto']}
                      tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}
                      tick={{ fill: '#71717a' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#18181b', 
                        border: 'none', 
                        borderRadius: '8px',
                        color: '#fafafa',
                        fontSize: '12px'
                      }}
                      itemStyle={{ color: '#10b981' }}
                      labelStyle={{ color: '#71717a', marginBottom: '4px' }}
                      formatter={(value: number) => [value.toLocaleString(undefined, { minimumFractionDigits: 2 }), 'Index Value']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="close" 
                      stroke="#10b981" 
                      strokeWidth={1.5}
                      fillOpacity={1} 
                      fill="url(#colorClose)" 
                      animationDuration={1500}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Table Section */}
            <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col max-h-[800px]">
              <div className="p-6 border-b border-zinc-200 dark:border-zinc-800 flex justify-between items-center shrink-0">
                <h2 className="text-lg font-semibold">Historical Records</h2>
                <p className="text-xs text-zinc-400">Total {data.length} records since 2005</p>
              </div>
              <div className="overflow-auto flex-1 scrollbar-thin scrollbar-thumb-zinc-200 dark:scrollbar-thumb-zinc-800">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs uppercase bg-zinc-50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800 sticky top-0 z-10">
                    <tr>
                      <th className="px-6 py-4 font-semibold bg-zinc-50 dark:bg-zinc-900">Date</th>
                      <th className="px-6 py-4 font-semibold text-right bg-zinc-50 dark:bg-zinc-900">Open</th>
                      <th className="px-6 py-4 font-semibold text-right bg-zinc-50 dark:bg-zinc-900">High</th>
                      <th className="px-6 py-4 font-semibold text-right bg-zinc-50 dark:bg-zinc-900">Low</th>
                      <th className="px-6 py-4 font-semibold text-right bg-zinc-50 dark:bg-zinc-900">Close</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                    {data.map((row, idx) => (
                      <tr key={idx} className="hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors">
                        <td className="px-6 py-4 font-medium">
                          {new Date(row.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </td>
                        <td className="px-6 py-4 text-right tabular-nums text-zinc-500 dark:text-zinc-400">
                          {Number(row.open) > 0 ? row.open.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-6 py-4 text-right text-emerald-600 dark:text-emerald-400 tabular-nums">
                          {Number(row.high) > 0 ? row.high.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-6 py-4 text-right text-rose-600 dark:text-rose-400 tabular-nums">
                          {Number(row.low) > 0 ? row.low.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-6 py-4 text-right font-bold tabular-nums">
                          {Number(row.close).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
                <div className="p-4 bg-zinc-50 dark:bg-zinc-900/50 text-center border-t border-zinc-200 dark:border-zinc-800 shrink-0">
                  <p className="text-xs text-zinc-500">End of records (Historical data starts from April 1, 2005)</p>
                </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
