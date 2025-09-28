'use client'

import { useState, useEffect } from 'react'
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  Pause,
  X,
  Activity
} from 'lucide-react'

interface Task {
  id: string
  name: string
  type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  priority: 'low' | 'medium' | 'high'
  created_at: string
  started_at?: string
  completed_at?: string
  progress?: number
  error?: string
}

export default function TaskQueue() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading tasks
    setTimeout(() => {
      setTasks([
        {
          id: '1',
          name: 'Search tweets about AI',
          type: 'search_tweets',
          status: 'running',
          priority: 'high',
          created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
          started_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          progress: 75
        },
        {
          id: '2',
          name: 'Analyze sentiment for Bitcoin',
          type: 'analyze_sentiment',
          status: 'pending',
          priority: 'medium',
          created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString()
        },
        {
          id: '3',
          name: 'Monitor @elonmusk timeline',
          type: 'monitor_user',
          status: 'completed',
          priority: 'low',
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          started_at: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
          completed_at: new Date(Date.now() - 5 * 60 * 1000).toISOString()
        },
        {
          id: '4',
          name: 'Create trending report',
          type: 'generate_report',
          status: 'failed',
          priority: 'high',
          created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
          started_at: new Date(Date.now() - 40 * 60 * 1000).toISOString(),
          error: 'API rate limit exceeded'
        }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return CheckCircle
      case 'failed':
        return AlertCircle
      case 'running':
        return Activity
      default:
        return Clock
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      case 'running':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-yellow-600 bg-yellow-100'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600'
      case 'medium':
        return 'text-yellow-600'
      case 'low':
        return 'text-green-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  }

  const handleStartTask = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, status: 'running', started_at: new Date().toISOString() }
        : task
    ))
  }

  const handlePauseTask = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, status: 'pending' }
        : task
    ))
  }

  const handleCancelTask = (taskId: string) => {
    setTasks(tasks.filter(task => task.id !== taskId))
  }

  if (isLoading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Queue</h3>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center space-x-3 animate-pulse">
              <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Task Queue</h3>
        <div className="flex space-x-2">
          <button className="btn btn-primary btn-sm">
            <Play className="w-4 h-4 mr-1" />
            Start All
          </button>
          <button className="btn btn-secondary btn-sm">
            <Pause className="w-4 h-4 mr-1" />
            Pause All
          </button>
        </div>
      </div>
      
      <div className="space-y-4">
        {tasks.map((task) => {
          const StatusIcon = getStatusIcon(task.status)
          return (
            <div key={task.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStatusColor(task.status)}`}>
                <StatusIcon className="w-4 h-4" />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <p className="text-sm font-medium text-gray-900 truncate">{task.name}</p>
                  <span className={`text-xs font-medium ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                </div>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(task.created_at)}
                  </span>
                  <span className="text-xs text-gray-400">•</span>
                  <span className="text-xs text-gray-500">{task.type}</span>
                </div>
                {task.progress && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span>{task.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${task.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {task.error && (
                  <p className="text-xs text-red-600 mt-1">{task.error}</p>
                )}
              </div>
              
              <div className="flex space-x-1">
                {task.status === 'pending' && (
                  <button
                    onClick={() => handleStartTask(task.id)}
                    className="p-1 text-green-600 hover:bg-green-100 rounded"
                    title="Start task"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                )}
                {task.status === 'running' && (
                  <button
                    onClick={() => handlePauseTask(task.id)}
                    className="p-1 text-yellow-600 hover:bg-yellow-100 rounded"
                    title="Pause task"
                  >
                    <Pause className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleCancelTask(task.id)}
                  className="p-1 text-red-600 hover:bg-red-100 rounded"
                  title="Cancel task"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>
      
      {tasks.length === 0 && (
        <div className="text-center py-8">
          <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No tasks in queue</p>
        </div>
      )}
    </div>
  )
}
