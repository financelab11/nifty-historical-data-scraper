"use client"

import { useEffect, useState, useMemo, useCallback, useRef } from "react"
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
import { motion, AnimatePresence } from "framer-motion"
import { 
  TrendingUp, 
  Calendar, 
  History, 
  Activity, 
  ChevronDown, 
  Loader2, 
  Zap,
  Info,
  ArrowUpRight,
  Monitor
} from "lucide-react"

interface IndexData {
  date: string
  index_name: string
  open: number
  high: number
  low: number
  close: number
}

const AVAILABLE_INDICES = [
  "Nifty 50",
  "Nifty Smallcap 250",
  "Nifty500 Momentum 50",
  "Nifty500 Quality 50",
  "Nifty500 Value 50",
  "Nifty500 Low Volatility 50"
]

export default function Home() {
  const [indexCache, setIndexCache] = useState<Record<string, IndexData[]>>({})
  const cacheRef = useRef<Record<string, IndexData[]>>({})
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState(0)
  const [selectedIndex, setSelectedIndex] = useState(AVAILABLE_INDICES[0])
  const [tableLimit, setTableLimit] = useState(50)

  // Sync ref with state
  useEffect(() => {
    cacheRef.current = indexCache
  }, [indexCache])

  // Memoized current data from cache for performance
  const allData = useMemo(() => indexCache[selectedIndex] || [], [indexCache, selectedIndex])

  const fetchData = useCallback(async (indexName: string, isBackground = false) => {
    // Check ref instead of state to avoid dependency loop
    if (cacheRef.current[indexName]) {
      if (!isBackground) setLoading(false)
      return
    }

    if (!isBackground) {
        setLoading(true)
        setProgress(0)
    }
    
    let offset = 0
    const limit = 1000 // Supabase default limit is 1000
    let hasMore = true
    let fetchedResults: IndexData[] = []

    try {
      while (hasMore) {
        const { data: records, error } = await supabase
          .from("nifty_indices")
          .select("*")
          .eq("index_name", indexName)
          .order("date", { ascending: false })
          .range(offset, offset + limit - 1)

        if (error) {
          throw error
        }
        
        if (records && records.length > 0) {
          fetchedResults = [...fetchedResults, ...records]
          if (!isBackground) setProgress(fetchedResults.length)
          
          if (records.length < limit) {
            hasMore = false
          } else {
            offset += limit
          }
        } else {
          hasMore = false
        }
      }
      
      if (fetchedResults.length > 0) {
        setIndexCache(prev => ({ ...prev, [indexName]: fetchedResults }))
      }
    } catch (err) {
      console.error(`Fetch failed for ${indexName}:`, err)
    } finally {
      if (!isBackground) setLoading(false)
    }
  }, []) // Removed indexCache dependency to avoid loops as we use cacheRef

  useEffect(() => {
    // Primary fetch for selected index
    fetchData(selectedIndex)
  }, [selectedIndex, fetchData])

  useEffect(() => {
    // Background prefetch for other indices after a short delay
    const timer = setTimeout(() => {
      AVAILABLE_INDICES.forEach(idx => {
        if (!cacheRef.current[idx]) {
          fetchData(idx, true)
        }
      })
    }, 3000)

    return () => clearTimeout(timer)
  }, [fetchData])

  // Performance optimization: sample chart data for smooth mobile rendering
  const chartData = useMemo(() => {
    if (allData.length === 0) return []
    
    // Target 800 points for mobile/desktop balance
    const targetPoints = 800
    const step = Math.max(1, Math.floor(allData.length / targetPoints))
    const sampled = []
    
    // Process from oldest to newest for the chart (allData is desc)
    for (let i = allData.length - 1; i >= 0; i -= step) {
      const item = allData[i]
      sampled.push({
        ...item,
        formattedDate: new Date(item.date).toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
      })
    }
    
    return sampled
  }, [allData])

  // Pre-calculate stats only when data changes
  const stats = useMemo(() => {
    if (allData.length === 0) return { latest: 0, high: 0, base: 1000, latestDate: '', count: 0, cagr: 0 }
    
    let maxHigh = 0
    for (const d of allData) {
        const h = Number(d.high) || Number(d.close)
        if (h > maxHigh) maxHigh = h
    }

    const latest = allData[0].close
    const base = allData[allData.length - 1].close || 1000
    
    // CAGR calculation (Annualized)
    // allData is descending (latest first)
    const startDate = new Date(allData[allData.length - 1].date)
    const endDate = new Date(allData[0].date)
    const diffInMs = endDate.getTime() - startDate.getTime()
    const years = diffInMs / (1000 * 60 * 60 * 24 * 365.25)
    
    // Avoid division by zero and handle initial growth correctly
    const cagr = years > 0.1 ? (Math.pow(latest / base, 1 / years) - 1) : 0

    return {
      latest,
      latestDate: allData[0].date,
      high: maxHigh,
      base,
      count: allData.length,
      cagr
    }
  }, [allData])

  const displayData = useMemo(() => {
    return allData.slice(0, tableLimit)
  }, [allData, tableLimit])

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 font-sans text-zinc-900 dark:text-zinc-100">
      <div className="max-w-7xl mx-auto px-4 py-6 md:px-8 md:py-10">
        
        {/* Mobile-First Header */}
        <header className="mb-8 md:mb-12">
          <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
            <div className="space-y-2">
              <motion.div 
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="inline-flex items-center gap-2 px-2 py-0.5 rounded-full bg-emerald-100/80 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-wider border border-emerald-200/50 dark:border-emerald-800/30"
              >
                <Zap className="w-3 h-3 fill-emerald-500" />
                Performance Engine 2.0
              </motion.div>
              <h1 className="text-3xl md:text-5xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-500 dark:from-white dark:via-zinc-200 dark:to-zinc-500">
                Strategy Hub
              </h1>
                <p className="text-zinc-500 dark:text-zinc-400 text-sm md:text-base max-w-xl font-medium leading-relaxed">
                  Seamless real-time analysis of Nifty 50, Smallcap 250, and factor indices. 
                  Experience 20+ years of institutional-grade data.
                </p>
            </div>
            
            <div className="relative group w-full md:w-auto">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
              <div className="relative flex flex-col gap-2">
                <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 ml-1">Strategy Selection</label>
                <div className="relative">
                  <select 
                    value={selectedIndex}
                    onChange={(e) => setSelectedIndex(e.target.value)}
                    className="appearance-none w-full md:min-w-[280px] bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl px-5 py-3.5 text-sm font-bold shadow-sm focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all cursor-pointer pr-12 hover:border-emerald-500/50"
                  >
                    {AVAILABLE_INDICES.map(idx => (
                      <option key={idx} value={idx}>{idx}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>
          
          {/* Quick Metrics Bar */}
          <div className="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-3">
             {[
               { label: 'Total Years', value: (stats.count / 252).toFixed(1), icon: Calendar },
               { label: 'Trading Days', value: stats.count.toLocaleString(), icon: History },
               { label: 'Base Date', value: 'Apr 2005', icon: Activity },
               { label: 'Live Sync', value: 'Active', icon: TrendingUp, color: 'text-emerald-500' }
             ].map((m, i) => (
               <div key={i} className="bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm p-3.5 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400">
                    <m.icon className="w-3.5 h-3.5" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-tighter">{m.label}</span>
                    <span className={`text-xs md:text-sm font-bold ${m.color || ''}`}>{m.value}</span>
                  </div>
               </div>
             ))}
          </div>
        </header>

        {loading && allData.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col justify-center items-center py-24 md:py-40 gap-6 bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-xl shadow-zinc-200/50 dark:shadow-none"
          >
            <div className="relative">
              <div className="h-20 w-20 rounded-full border-4 border-zinc-100 dark:border-zinc-800"></div>
              <div className="absolute top-0 left-0 h-20 w-20 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                 <Zap className="w-6 h-6 text-emerald-500 animate-pulse" />
              </div>
            </div>
            <div className="text-center space-y-2">
              <h3 className="text-xl font-bold tracking-tight">Syncing Market Data</h3>
              <p className="text-zinc-500 text-sm font-medium">Crunching {progress.toLocaleString()} institutional records...</p>
            </div>
          </motion.div>
        ) : (
          <div className="space-y-6 md:space-y-10">
            
            {/* Core Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
              <motion.div 
                whileHover={{ y: -4 }}
                className="bg-white dark:bg-zinc-900 p-6 md:p-8 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-sm relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-6 opacity-[0.03] dark:opacity-[0.05]">
                   <Monitor className="w-24 h-24" />
                </div>
                <div className="flex items-center gap-2 mb-3">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <p className="text-[10px] text-zinc-400 uppercase font-black tracking-[0.2em]">Latest Index Value</p>
                </div>
                <p className="text-4xl md:text-5xl font-black tabular-nums tracking-tighter mb-4">
                  {stats.latest.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-zinc-100 dark:bg-zinc-800 w-fit rounded-lg">
                    <Calendar className="w-3 h-3 text-zinc-400" />
                    <span className="text-[10px] font-bold text-zinc-500 dark:text-zinc-400">
                        {stats.latestDate ? new Date(stats.latestDate).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'}
                    </span>
                </div>
              </motion.div>
              
              <motion.div 
                whileHover={{ y: -4 }}
                className="bg-emerald-600 p-6 md:p-8 rounded-3xl border border-emerald-500 shadow-lg shadow-emerald-500/20 relative overflow-hidden"
              >
                <div className="absolute -right-4 -bottom-4 opacity-20">
                    <TrendingUp className="w-32 h-32 text-white" />
                </div>
                <p className="text-[10px] text-emerald-100/60 uppercase font-black tracking-[0.2em] mb-3">Historical Peak</p>
                <p className="text-4xl md:text-5xl font-black text-white tabular-nums tracking-tighter mb-4">
                  {stats.high.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
                <p className="text-xs font-bold text-emerald-100 flex items-center gap-1.5">
                  <ArrowUpRight className="w-4 h-4" /> 
                  All-time maximum recorded
                </p>
              </motion.div>

              <motion.div 
                whileHover={{ y: -4 }}
                className="bg-zinc-900 dark:bg-white p-6 md:p-8 rounded-3xl border border-zinc-800 dark:border-zinc-100 shadow-xl relative overflow-hidden"
              >
                <p className="text-[10px] text-zinc-500 dark:text-zinc-400 uppercase font-black tracking-[0.2em] mb-3">Annualized Returns (CAGR)</p>
                <p className="text-4xl md:text-5xl font-black text-white dark:text-zinc-900 tabular-nums tracking-tighter mb-4">
                  {(stats.cagr * 100).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%
                </p>
                <p className="text-xs font-bold text-zinc-400 dark:text-zinc-500 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Since Apr 2005 inception
                </p>
              </motion.div>
            </div>

            {/* Optimized Chart Section */}
            <div className="bg-white dark:bg-zinc-900 p-6 md:p-10 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 md:mb-12 gap-6">
                <div className="space-y-1">
                  <h2 className="text-2xl md:text-3xl font-black tracking-tight">Growth Trajectory</h2>
                  <p className="text-zinc-500 text-sm font-medium">Visualizing capital appreciation over 21 years</p>
                </div>
                <div className="flex flex-wrap gap-2">
                   <div className="px-3 py-1.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 text-[10px] font-black text-zinc-500 flex items-center gap-2">
                     <Monitor className="w-3 h-3" /> SAMPLED
                   </div>
                   <div className="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-[10px] font-black text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                     <Zap className="w-3 h-3" /> REAL-TIME
                   </div>
                </div>
              </div>
              <div className="h-[350px] md:h-[500px] w-full ml-[-24px] md:ml-[-20px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#e4e4e7" strokeOpacity={0.1} />
                    <XAxis 
                      dataKey="formattedDate" 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      minTickGap={60}
                      tick={{ fill: '#71717a', fontWeight: 700 }}
                    />
                    <YAxis 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      domain={['auto', 'auto']}
                      tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}
                      tick={{ fill: '#71717a', fontWeight: 700 }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#18181b', 
                        border: 'none', 
                        borderRadius: '16px',
                        color: '#fafafa',
                        fontSize: '12px',
                        padding: '16px',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                      }}
                      itemStyle={{ color: '#10b981', fontWeight: '800' }}
                      labelStyle={{ color: '#a1a1aa', marginBottom: '8px', fontSize: '10px', fontWeight: '900', textTransform: 'uppercase' }}
                      formatter={(value: number) => [`₹${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`, 'Index Value']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="close" 
                      stroke="#10b981" 
                      strokeWidth={3}
                      fillOpacity={1} 
                      fill="url(#colorClose)" 
                      animationDuration={1000}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Optimized Ledger Section */}
            <div className="bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden flex flex-col">
              <div className="p-6 md:p-10 border-b border-zinc-200 dark:border-zinc-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
                <div>
                  <h2 className="text-2xl font-black tracking-tight">Market Ledger</h2>
                  <p className="text-sm text-zinc-500 font-medium">Immutable historical records</p>
                </div>
                <div className="flex items-center gap-4 bg-zinc-50 dark:bg-zinc-800/50 p-1.5 rounded-xl border border-zinc-200/50 dark:border-zinc-800/50">
                   <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest pl-3">Limit</span>
                   <select 
                    value={tableLimit}
                    onChange={(e) => setTableLimit(Number(e.target.value))}
                    className="bg-white dark:bg-zinc-900 border-none rounded-lg px-4 py-2 text-xs font-black shadow-sm outline-none cursor-pointer hover:bg-zinc-50"
                   >
                     {[25, 50, 100, 250, 500].map(v => (
                       <option key={v} value={v}>{v}</option>
                     ))}
                   </select>
                </div>
              </div>
              
              <div className="overflow-x-auto scrollbar-hide">
                <table className="w-full text-sm text-left border-collapse min-w-[600px]">
                  <thead>
                    <tr className="bg-zinc-50/50 dark:bg-zinc-900/50 text-zinc-400 border-b border-zinc-200 dark:border-zinc-800">
                      <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em]">Date</th>
                      <th className="px-8 py-6 text-right text-[10px] font-black uppercase tracking-[0.2em]">Open</th>
                      <th className="px-8 py-6 text-right text-[10px] font-black uppercase tracking-[0.2em]">High</th>
                      <th className="px-8 py-6 text-right text-[10px] font-black uppercase tracking-[0.2em]">Low</th>
                      <th className="px-8 py-6 text-right text-[10px] font-black uppercase tracking-[0.2em]">Close</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/50">
                    <AnimatePresence mode="popLayout">
                      {displayData.map((row, idx) => (
                        <motion.tr 
                          layout
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          key={`${row.date}-${idx}`} 
                          className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/30 transition-colors group"
                        >
                          <td className="px-8 py-5 font-bold text-zinc-800 dark:text-zinc-200">
                            {new Date(row.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                          </td>
                          <td className="px-8 py-5 text-right tabular-nums text-zinc-500 font-medium">
                            {Number(row.open) > 0 ? row.open.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                          </td>
                          <td className="px-8 py-5 text-right text-emerald-600/70 dark:text-emerald-500/70 tabular-nums font-bold">
                            {Number(row.high) > 0 ? row.high.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                          </td>
                          <td className="px-8 py-5 text-right text-rose-500/70 dark:text-rose-400/70 tabular-nums font-bold">
                            {Number(row.low) > 0 ? row.low.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-'}
                          </td>
                          <td className="px-8 py-5 text-right font-black tabular-nums text-zinc-900 dark:text-white group-hover:text-emerald-500 transition-colors">
                            {Number(row.close).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </td>
                        </motion.tr>
                      ))}
                    </AnimatePresence>
                  </tbody>
                </table>
              </div>
              
              {allData.length > tableLimit && (
                <div className="p-8 bg-zinc-50/50 dark:bg-zinc-900/50 text-center border-t border-zinc-200 dark:border-zinc-800">
                  <button 
                    onClick={() => setTableLimit(prev => Math.min(prev + 250, allData.length))}
                    className="px-6 py-3 rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-[10px] font-black text-zinc-900 dark:text-white hover:border-emerald-500 transition-all uppercase tracking-widest shadow-sm"
                  >
                    Load More Records ({allData.length - tableLimit} Remaining)
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Mobile Navigation Indicator */}
        <footer className="mt-12 text-center pb-8 opacity-20 hidden md:block">
            <p className="text-[10px] font-black uppercase tracking-[0.5em] text-zinc-400">Institutional Factor Analysis Engine v2.4.0</p>
        </footer>
      </div>
    </div>
  )
}
