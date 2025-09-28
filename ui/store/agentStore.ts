import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

interface AgentStatus {
  active_tasks: number
  completed_tasks: number
  scheduled_workflows: number
  last_activity: string | null
  status: 'running' | 'stopped' | 'error'
}

interface AgentState {
  agentStatus: AgentStatus | null
  isLoading: boolean
  error: string | null
  fetchAgentStatus: () => Promise<void>
  startAgent: () => Promise<void>
  stopAgent: () => Promise<void>
}

export const useAgentStore = create<AgentState>()(
  devtools(
    (set, get) => ({
      agentStatus: null,
      isLoading: false,
      error: null,

      fetchAgentStatus: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/agent/status')
          if (!response.ok) {
            throw new Error('Failed to fetch agent status')
          }
          const data = await response.json()
          set({ agentStatus: data, isLoading: false })
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      },

      startAgent: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/agent/start', {
            method: 'POST'
          })
          if (!response.ok) {
            throw new Error('Failed to start agent')
          }
          await get().fetchAgentStatus()
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      },

      stopAgent: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/agent/stop', {
            method: 'POST'
          })
          if (!response.ok) {
            throw new Error('Failed to stop agent')
          }
          await get().fetchAgentStatus()
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      }
    }),
    {
      name: 'agent-store'
    }
  )
)
