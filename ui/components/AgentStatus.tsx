'use client'

import { useAgentStore } from '../store/agentStore'
import { Play, Pause, AlertCircle, CheckCircle } from 'lucide-react'

export default function AgentStatus() {
  const { agentStatus, isLoading, startAgent, stopAgent } = useAgentStore()

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-green-600 bg-green-100'
      case 'stopped':
        return 'text-gray-600 bg-gray-100'
      case 'error':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return CheckCircle
      case 'stopped':
        return Pause
      case 'error':
        return AlertCircle
      default:
        return Pause
    }
  }

  const StatusIcon = agentStatus ? getStatusIcon(agentStatus.status) : Pause

  return (
    <div className="flex items-center space-x-3">
      <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(agentStatus?.status || 'stopped')}`}>
        <StatusIcon className="w-4 h-4 mr-1" />
        {agentStatus?.status || 'Unknown'}
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={startAgent}
          disabled={isLoading || agentStatus?.status === 'running'}
          className="btn btn-primary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4 mr-1" />
          Start
        </button>
        
        <button
          onClick={stopAgent}
          disabled={isLoading || agentStatus?.status === 'stopped'}
          className="btn btn-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Pause className="w-4 h-4 mr-1" />
          Stop
        </button>
      </div>
    </div>
  )
}
