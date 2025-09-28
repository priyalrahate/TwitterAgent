'use client'

import { useState, useEffect } from 'react'
import { 
  Twitter, 
  Bot, 
  Activity, 
  TrendingUp, 
  Users, 
  MessageSquare,
  Settings,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react'
import { useAgentStore } from '../store/agentStore'
import { useWorkflowStore } from '../store/workflowStore'
import DashboardStats from '../components/DashboardStats'
import RecentActivity from '../components/RecentActivity'
import WorkflowManager from '../components/WorkflowManager'
import TaskQueue from '../components/TaskQueue'
import AgentStatus from '../components/AgentStatus'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const { agentStatus, fetchAgentStatus } = useAgentStore()
  const { workflows, fetchWorkflows } = useWorkflowStore()

  useEffect(() => {
    fetchAgentStatus()
    fetchWorkflows()
  }, [])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'workflows', label: 'Workflows', icon: Bot },
    { id: 'tasks', label: 'Tasks', icon: MessageSquare },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <Twitter className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Twitter Agent</h1>
                <p className="text-sm text-gray-500">AI-powered Twitter automation</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <AgentStatus />
              <button className="btn btn-secondary">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-1 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stats Overview */}
            <DashboardStats />
            
            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <RecentActivity />
              <TaskQueue />
            </div>
          </div>
        )}

        {activeTab === 'workflows' && (
          <WorkflowManager />
        )}

        {activeTab === 'tasks' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Task Management</h2>
              <button className="btn btn-primary">
                <Play className="w-4 h-4 mr-2" />
                New Task
              </button>
            </div>
            <TaskQueue />
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">API Configuration</h3>
                <div className="space-y-4">
                  <div>
                    <label className="label">Twitter API Key</label>
                    <input type="password" className="input" placeholder="Enter your Twitter API key" />
                  </div>
                  <div>
                    <label className="label">OpenAI API Key</label>
                    <input type="password" className="input" placeholder="Enter your OpenAI API key" />
                  </div>
                  <div>
                    <label className="label">Fetch.ai API Key</label>
                    <input type="password" className="input" placeholder="Enter your Fetch.ai API key" />
                  </div>
                  <button className="btn btn-primary">Save Configuration</button>
                </div>
              </div>
              
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="label">Default Schedule Interval</label>
                    <select className="input">
                      <option value="900">15 minutes</option>
                      <option value="1800">30 minutes</option>
                      <option value="3600">1 hour</option>
                      <option value="7200">2 hours</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Max Tweets per Request</label>
                    <input type="number" className="input" defaultValue="100" />
                  </div>
                  <div>
                    <label className="label">Rate Limit Delay</label>
                    <input type="number" className="input" defaultValue="1.0" step="0.1" />
                  </div>
                  <button className="btn btn-primary">Update Settings</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
