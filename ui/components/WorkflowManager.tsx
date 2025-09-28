'use client'

import { useState } from 'react'
import { useWorkflowStore } from '../store/workflowStore'
import { 
  Play, 
  Pause, 
  Settings, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Bot,
  TrendingUp,
  Users,
  MessageSquare
} from 'lucide-react'

export default function WorkflowManager() {
  const { workflows, isLoading, executeWorkflow, scheduleWorkflow, cancelWorkflow } = useWorkflowStore()
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [showParameters, setShowParameters] = useState(false)

  const getWorkflowIcon = (type: string) => {
    switch (type) {
      case 'trend_monitor':
        return TrendingUp
      case 'user_monitor':
        return Users
      case 'content_curator':
        return MessageSquare
      default:
        return Bot
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'status-success'
      case 'inactive':
        return 'status-pending'
      case 'error':
        return 'status-error'
      default:
        return 'status-pending'
    }
  }

  const handleExecuteWorkflow = async (workflowName: string) => {
    await executeWorkflow(workflowName)
  }

  const handleScheduleWorkflow = async (workflowName: string) => {
    await scheduleWorkflow(workflowName, {}, { interval: 3600 })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Workflow Manager</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full mb-4"></div>
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Workflow Manager</h2>
        <button className="btn btn-primary">
          <Bot className="w-4 h-4 mr-2" />
          Create Workflow
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => {
          const Icon = getWorkflowIcon(workflow.type)
          return (
            <div key={workflow.name} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">{workflow.name}</h3>
                    <p className="text-sm text-gray-500">v{workflow.version}</p>
                  </div>
                </div>
                <span className={`status-badge ${getStatusColor(workflow.status || 'inactive')}`}>
                  {workflow.status || 'inactive'}
                </span>
              </div>

              <p className="text-gray-600 text-sm mb-4">{workflow.description}</p>

              <div className="space-y-2 mb-4">
                {workflow.last_run && (
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="w-3 h-3 mr-1" />
                    Last run: {new Date(workflow.last_run).toLocaleString()}
                  </div>
                )}
                {workflow.next_run && (
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="w-3 h-3 mr-1" />
                    Next run: {new Date(workflow.next_run).toLocaleString()}
                  </div>
                )}
                {workflow.run_count && (
                  <div className="flex items-center text-xs text-gray-500">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Runs: {workflow.run_count}
                  </div>
                )}
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => handleExecuteWorkflow(workflow.name)}
                  className="btn btn-primary btn-sm flex-1"
                >
                  <Play className="w-4 h-4 mr-1" />
                  Run Now
                </button>
                <button
                  onClick={() => handleScheduleWorkflow(workflow.name)}
                  className="btn btn-secondary btn-sm flex-1"
                >
                  <Clock className="w-4 h-4 mr-1" />
                  Schedule
                </button>
                <button className="btn btn-secondary btn-sm">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {workflows.length === 0 && (
        <div className="text-center py-12">
          <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No workflows found</h3>
          <p className="text-gray-500 mb-4">Create your first workflow to get started with automation.</p>
          <button className="btn btn-primary">
            <Bot className="w-4 h-4 mr-2" />
            Create Workflow
          </button>
        </div>
      )}
    </div>
  )
}
