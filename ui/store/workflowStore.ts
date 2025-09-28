import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

interface Workflow {
  name: string
  description: string
  type: string
  version: string
  status?: 'active' | 'inactive' | 'error'
  last_run?: string
  next_run?: string
  run_count?: number
}

interface WorkflowState {
  workflows: Workflow[]
  isLoading: boolean
  error: string | null
  fetchWorkflows: () => Promise<void>
  executeWorkflow: (workflowName: string, parameters?: Record<string, any>) => Promise<void>
  scheduleWorkflow: (workflowName: string, parameters?: Record<string, any>, scheduleConfig?: Record<string, any>) => Promise<void>
  cancelWorkflow: (taskId: string) => Promise<void>
}

export const useWorkflowStore = create<WorkflowState>()(
  devtools(
    (set, get) => ({
      workflows: [],
      isLoading: false,
      error: null,

      fetchWorkflows: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/workflows')
          if (!response.ok) {
            throw new Error('Failed to fetch workflows')
          }
          const data = await response.json()
          set({ workflows: data, isLoading: false })
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      },

      executeWorkflow: async (workflowName: string, parameters = {}) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/workflows/execute', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              workflow_name: workflowName,
              parameters
            })
          })
          if (!response.ok) {
            throw new Error('Failed to execute workflow')
          }
          const data = await response.json()
          // Refresh workflows to get updated status
          await get().fetchWorkflows()
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      },

      scheduleWorkflow: async (workflowName: string, parameters = {}, scheduleConfig = {}) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch('/api/workflows/schedule', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              workflow_name: workflowName,
              parameters,
              schedule_config: scheduleConfig
            })
          })
          if (!response.ok) {
            throw new Error('Failed to schedule workflow')
          }
          const data = await response.json()
          // Refresh workflows to get updated status
          await get().fetchWorkflows()
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      },

      cancelWorkflow: async (taskId: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch(`/api/workflows/cancel/${taskId}`, {
            method: 'POST'
          })
          if (!response.ok) {
            throw new Error('Failed to cancel workflow')
          }
          // Refresh workflows to get updated status
          await get().fetchWorkflows()
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Unknown error',
            isLoading: false 
          })
        }
      }
    }),
    {
      name: 'workflow-store'
    }
  )
)
