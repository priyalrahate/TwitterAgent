'use client'

import { useState, useEffect } from 'react'
import { 
  Activity, 
  Twitter, 
  Heart, 
  Repeat2, 
  MessageCircle,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react'

interface ActivityItem {
  id: string
  type: 'tweet' | 'like' | 'retweet' | 'follow' | 'workflow'
  description: string
  timestamp: string
  user?: string
  engagement?: number
  status: 'success' | 'error' | 'pending'
}

export default function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading activities
    setTimeout(() => {
      setActivities([
        {
          id: '1',
          type: 'workflow',
          description: 'Trend Monitor workflow executed successfully',
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          status: 'success'
        },
        {
          id: '2',
          type: 'tweet',
          description: 'Posted tweet about AI trends',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          user: '@twitter_agent',
          engagement: 42,
          status: 'success'
        },
        {
          id: '3',
          type: 'like',
          description: 'Liked tweet from @elonmusk',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          user: '@elonmusk',
          status: 'success'
        },
        {
          id: '4',
          type: 'retweet',
          description: 'Retweeted important news about Web3',
          timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
          user: '@web3_news',
          engagement: 128,
          status: 'success'
        },
        {
          id: '5',
          type: 'follow',
          description: 'Started following @ai_researcher',
          timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
          user: '@ai_researcher',
          status: 'success'
        },
        {
          id: '6',
          type: 'workflow',
          description: 'User Monitor workflow failed',
          timestamp: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
          status: 'error'
        }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'tweet':
        return Twitter
      case 'like':
        return Heart
      case 'retweet':
        return Repeat2
      case 'follow':
        return Users
      case 'workflow':
        return TrendingUp
      default:
        return Activity
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600'
      case 'error':
        return 'text-red-600'
      case 'pending':
        return 'text-yellow-600'
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

  if (isLoading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
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
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <button className="text-sm text-primary-600 hover:text-primary-700">
          View All
        </button>
      </div>
      
      <div className="space-y-4">
        {activities.map((activity) => {
          const Icon = getActivityIcon(activity.type)
          return (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                activity.status === 'success' ? 'bg-green-100' : 
                activity.status === 'error' ? 'bg-red-100' : 'bg-yellow-100'
              }`}>
                <Icon className={`w-4 h-4 ${getStatusColor(activity.status)}`} />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900">{activity.description}</p>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs text-gray-500">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {formatTimeAgo(activity.timestamp)}
                  </span>
                  {activity.user && (
                    <span className="text-xs text-primary-600">{activity.user}</span>
                  )}
                  {activity.engagement && (
                    <span className="text-xs text-gray-500">
                      {activity.engagement} engagements
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      {activities.length === 0 && (
        <div className="text-center py-8">
          <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No recent activity</p>
        </div>
      )}
    </div>
  )
}
