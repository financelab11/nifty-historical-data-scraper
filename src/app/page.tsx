"use client"

import { useEffect, useState, useMemo } from "react"
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

const AVAILABLE_INDICES = [
  "Nifty500 Momentum 50",
  "Nifty500 Quality 50"
]

export default function Home() {
  const [allData, setAllData] = useState<IndexData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedIndex, setSelectedIndex] = useState(AVAILABLE_INDICES[0])
  const [tableLimit, setTableLimit] = useState(100)

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      setAllData([])
      let offset = 0
      const limit = 1000
      let hasMore = true
      let fetchedResults: IndexData[] = []

      console.log(`Starting data fetch for ${selectedIndex}...`)

      try {
        while (hasMore) {
          const { data: records, error } = await supabase
            .from("nifty_indices")
            .select("*")
            .eq("index_name", selectedIndex)
            .order("date", { ascending: false })
            .range(offset, offset + limit - 1)

          if (error) {
            console.error("Error fetching data:", error)
            hasMore = false
          } else if (records && records.length > 0) {
            fetchedResults = [...fetchedResults, ...records]
            if (records.length < limit) {
              hasMore = false
            } else {
              offset += limit
            }
            // Intermediate update for large datasets so user sees progress
            if (fetchedResults.length % 2000 === 0) {
               setAllData([...fetchedResults])
            }
          } else {
            hasMore = false
          }
        }
        setAllData(fetchedResults)
      } catch (err) {
        console.error("Fetch failed:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [selectedIndex])

  // Performance optimization: sample chart data if it's too large
  const chartData = useMemo(() => {
    if (allData.length === 0) return []
    
    // We want about 1000-1500 points max for smooth chart performance
    const step = Math.max(1, Math.floor(allData.length / 1500))
    const sampled = []
    
    // Process from oldest to newest for the chart
    for (let i = allData.length - 1; i >= 0; i -= step) {
      const item = allData[i]
      sampled.push({
        ...item,
        formattedDate: new Date(item.date).toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
      })
    }
    
    return sampled
  }, [allData])

  // Summary statistics
  const stats = useMemo(() => {
    if (allData.length === 0) return { latest: 0, high: 0, base: 0, latestDate: '', count: 0 }
    
    return {
      latest: allData[0].close,
      latestDate: allData[0].date,
      high: Math.max(...allData.map(d => Number(d.high) || Number(d.close))),
      base: allData[allData.length - 1].close,
      count: allData.length
    }
  }, [allData])

  const displayData = useMemo(() => {
    return allData.slice(0, tableLimit)
  }, [allData, tableLimit])

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-4 md:p-8 font-sans text-zinc-900 dark:text-zinc-100">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 space-y-6">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div className="flex-1">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-3 border border-emerald-200 dark:border-emerald-800/50">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                Live Performance Engine
              </div>
              <h1 className="text-4xl font-extrabold tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-zinc-900 to-zinc-500 dark:from-white dark:to-zinc-500">
                Strategy Analyzer
              </h1>
              <p className="text-zinc-500 dark:text-zinc-400 max-w-lg">
                High-fidelity backtesting data for Nifty500 specialized indices. 
                Full history from April 2005 onwards.
              </p>
            </div>
            
            <div className="flex flex-col gap-3">
              <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 ml-1">Select Strategy</label>
              <select 
                value={selectedIndex}
                onChange={(e) => setSelectedIndex(e.target.value)}
                className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-2.5 text-sm font-semibold shadow-sm focus:ring-2 focus:ring-emerald-500 outline-none transition-all cursor-pointer min-w-[240px]"
              >
                {AVAILABLE_INDICES.map(idx => (
                  <option key={idx} value={idx}>{idx}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
             <div className="bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 flex flex-col items-center justify-center text-center">
                <span className="text-[10px] text-zinc-400 font-bold uppercase mb-1">Total History</span>
                <span className="text-sm font-bold">{(stats.count / 252).toFixed(1)} Years</span>
             </div>
             <div className="bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 flex flex-col items-center justify-center text-center">
                <span className="text-[10px] text-zinc-400 font-bold uppercase mb-1">Trading Days</span>
                <span className="text-sm font-bold">{stats.count.toLocaleString()}</span>
             </div>
             <div className="bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 flex flex-col items-center justify-center text-center">
                <span className="text-[10px] text-zinc-400 font-bold uppercase mb-1">Inception</span>
                <span className="text-sm font-bold">Apr 2005</span>
             </div>
             <div className="bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 flex flex-col items-center justify-center text-center">
                <span className="text-[10px] text-zinc-400 font-bold uppercase mb-1">Status</span>
                <span className="text-sm font-bold text-emerald-500">Synced</span>
             </div>
          </div>
        </header>

        {loading && allData.length === 0 ? (
          <div className="flex flex-col justify-center items-center py-32 gap-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
            <div className="relative">
              <div className="h-16 w-16 rounded-full border-4 border-zinc-100 dark:border-zinc-800"></div>
              <div className="absolute top-0 left-0 h-16 w-16 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin"></div>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold">Crunching 20 years of data...</p>
              <p className="text-zinc-500 text-sm mt-1">Fetching records from Supabase cloud</p>
            </div>
          </div>
        ) : (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                   <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
                </div>
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400 uppercase font-extrabold tracking-widest mb-2">Latest Index Value</p>
                <p className="text-4xl font-black tabular-nums tracking-tight">
                  {stats.latest.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
                <p className="text-xs font-medium text-zinc-400 mt-2 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  As of {stats.latestDate ? new Date(stats.latestDate).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'}
                </p>
              </div>
              
              <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm group">
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400 uppercase font-extrabold tracking-widest mb-2">Historical High</p>
                <p className="text-4xl font-black text-emerald-600 dark:text-emerald-500 tabular-nums tracking-tight">
                  {stats.high.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
                <p className="text-xs font-medium text-emerald-600/60 dark:text-emerald-500/60 mt-2">
                  Peak performance recorded
                </p>
              </div>

              <div className="bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm group">
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400 uppercase font-extrabold tracking-widest mb-2">Total Return</p>
                <p className="text-4xl font-black text-zinc-900 dark:text-zinc-100 tabular-nums tracking-tight">
                  {((stats.latest / stats.base) * 100 - 100).toLocaleString(undefined, { maximumFractionDigits: 0 })}%
                </p>
                <p className="text-xs font-medium text-zinc-400 mt-2">
                  Since Apr 2005 (Base: {stats.base.toLocaleString()})
                </p>
              </div>
            </div>

            {/* Chart Section */}
            <div className="bg-white dark:bg-zinc-900 p-8 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden relative">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-10 gap-4">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight">Cumulative Growth</h2>
                  <p className="text-zinc-500 text-sm">Visualizing the 20-year performance trajectory</p>
                </div>
                <div className="flex gap-2">
                   <div className="px-3 py-1 rounded-full bg-zinc-100 dark:bg-zinc-800 text-[10px] font-bold text-zinc-500">OHLC SAMPLED</div>
                   <div className="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950 text-[10px] font-bold text-emerald-600 dark:text-emerald-400">LOGARITHMIC VIEW</div>
                </div>
              </div>
              <div className="h-[500px] w-full ml-[-20px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" strokeOpacity={0.2} />
                    <XAxis 
                      dataKey="formattedDate" 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      minTickGap={100}
                      tick={{ fill: '#71717a', fontWeight: 600 }}
                    />
                    <YAxis 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      domain={['auto', 'auto']}
                      tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}
                      tick={{ fill: '#71717a', fontWeight: 600 }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#18181b', 
                        border: 'none', 
                        borderRadius: '12px',
                        color: '#fafafa',
                        fontSize: '12px',
                        padding: '12px',
                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                      }}
                      itemStyle={{ color: '#10b981', fontWeight: 'bold' }}
                      labelStyle={{ color: '#71717a', marginBottom: '8px', fontSize: '10px', fontWeight: 'bold' }}
                      formatter={(value: number) => [value.toLocaleString(undefined, { minimumFractionDigits: 2 }), 'Index Value']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="close" 
                      stroke="#10b981" 
                      strokeWidth={2.5}
                      fillOpacity={1} 
                      fill="url(#colorClose)" 
                      animationDuration={1500}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Table Section */}
            <div className="bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
              <div className="p-8 border-b border-zinc-200 dark:border-zinc-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shrink-0">
                <div>
                  <h2 className="text-xl font-bold tracking-tight">Detailed Ledger</h2>
                  <p className="text-sm text-zinc-500">Latest market activity records</p>
                </div>
                <div className="flex items-center gap-2">
                   <span className="text-xs font-medium text-zinc-400">Show rows:</span>
                   <select 
                    value={tableLimit}
                    onChange={(e) => setTableLimit(Number(e.target.value))}
                    className="bg-zinc-100 dark:bg-zinc-800 border-none rounded-md px-2 py-1 text-xs font-bold outline-none cursor-pointer"
                   >
                     <option value={50}>50</option>
                     <option value={100}>100</option>
                     <option value={250}>250</option>
                     <option value={500}>500</option>
                   </select>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left border-collapse">
                  <thead className="text-[10px] uppercase font-black tracking-widest bg-zinc-50/50 dark:bg-zinc-900/50 text-zinc-400 border-b border-zinc-200 dark:border-zinc-800">
                    <tr>
                      <th className="px-8 py-5">Date</th>
                      <th className="px-8 py-5 text-right">Open</th>
                      <th className="px-8 py-5 text-right">High</th>
                      <th className="px-8 py-5 text-right">Low</th>
                      <th className="px-8 py-5 text-right">Close</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/50">
                    {displayData.map((row, idx) => (
                      <tr key={`${row.date}-${idx}`} className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/30 transition-colors group">
                        <td className="px-8 py-4 font-bold text-zinc-700 dark:text-zinc-300">
                          {new Date(row.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </td>
                        <td className="px-8 py-4 text-right tabular-nums text-zinc-400 font-medium">
                          {Number(row.open) > 0 ? row.open.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-8 py-4 text-right text-emerald-600/80 dark:text-emerald-500/80 tabular-nums font-semibold">
                          {Number(row.high) > 0 ? row.high.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-8 py-4 text-right text-rose-600/80 dark:text-rose-500/80 tabular-nums font-semibold">
                          {Number(row.low) > 0 ? row.low.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                        </td>
                        <td className="px-8 py-4 text-right font-black tabular-nums text-zinc-900 dark:text-white group-hover:text-emerald-500 transition-colors">
                          {Number(row.close).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {allData.length > tableLimit && (
                <div className="p-6 bg-zinc-50/50 dark:bg-zinc-900/50 text-center border-t border-zinc-200 dark:border-zinc-800 shrink-0">
                  <button 
                    onClick={() => setTableLimit(prev => Math.min(prev + 500, allData.length))}
                    className="text-xs font-bold text-emerald-600 dark:text-emerald-400 hover:underline"
                  >
                    LOAD MORE DATA ({allData.length - tableLimit} RECORDS REMAINING)
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
