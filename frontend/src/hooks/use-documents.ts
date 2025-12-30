'use client'

import { useState, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, type APIResponse, endpoints } from '@/lib/api'
import type { UploadFile } from '@/components/documents'
import type { ProcessingFile, ProcessingStage } from '@/components/documents'

/**
 * Document upload response
 */
interface DocumentUploadResponse {
  document_id: string
  name: string
  status: 'processing' | 'complete' | 'error'
  extracted_text?: string
  entities?: Array<{ name: string; type: string }>
  summary?: string
  error?: string
}

/**
 * Document processing status response
 */
interface DocumentStatusResponse {
  document_id: string
  status: ProcessingStage
  progress: number
  extracted_text?: string
  entities?: Array<{ name: string; type: string }>
  error?: string
}

/**
 * Query key factory for documents
 */
const documentKeys = {
  all: ['documents'] as const,
  list: () => [...documentKeys.all, 'list'] as const,
  detail: (id: string) => [...documentKeys.all, 'detail', id] as const,
  status: (id: string) => [...documentKeys.all, 'status', id] as const,
}

/**
 * Hook for managing document uploads
 */
export function useDocumentUpload() {
  const queryClient = useQueryClient()
  const [files, setFiles] = useState<ProcessingFile[]>([])

  /**
   * Upload mutation
   */
  const uploadMutation = useMutation({
    mutationFn: async (file: File): Promise<DocumentUploadResponse> => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post<APIResponse<DocumentUploadResponse>>(
        endpoints.documents.upload,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              updateFileProgress(file.name, 'uploading', progress)
            }
          },
        }
      )

      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Upload failed')
      }

      return response.data.data
    },
    onSuccess: (data, file) => {
      // Update file with document_id and move to processing
      setFiles((prev) =>
        prev.map((f) =>
          f.name === file.name
            ? {
                ...f,
                id: data.document_id,
                stage: data.status === 'complete' ? 'complete' : 'extracting',
                stageProgress: 0,
                extractedText: data.extracted_text,
                entities: data.entities,
              }
            : f
        )
      )

      // Invalidate document queries
      queryClient.invalidateQueries({ queryKey: documentKeys.all })
    },
    onError: (error, file) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.name === file.name
            ? {
                ...f,
                stage: 'error',
                errorDetails: error instanceof Error ? error.message : 'Upload failed',
              }
            : f
        )
      )
    },
  })

  /**
   * Update file progress
   */
  const updateFileProgress = useCallback(
    (fileName: string, stage: ProcessingStage, progress: number) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.name === fileName
            ? { ...f, stage, stageProgress: progress }
            : f
        )
      )
    },
    []
  )

  /**
   * Add files to queue
   */
  const addFiles = useCallback((newFiles: UploadFile[]) => {
    const processingFiles: ProcessingFile[] = newFiles.map((f) => ({
      ...f,
      stage: 'queued' as ProcessingStage,
      stageProgress: 0,
    }))
    setFiles((prev) => [...prev, ...processingFiles])
  }, [])

  /**
   * Remove file from queue
   */
  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId))
  }, [])

  /**
   * Start upload for all queued files
   */
  const startUpload = useCallback(() => {
    const queuedFiles = files.filter((f) => f.stage === 'queued')

    queuedFiles.forEach((processingFile) => {
      // Update to uploading state
      setFiles((prev) =>
        prev.map((f) =>
          f.id === processingFile.id
            ? { ...f, stage: 'uploading', stageProgress: 0 }
            : f
        )
      )

      // Start upload
      uploadMutation.mutate(processingFile.file)
    })
  }, [files, uploadMutation])

  /**
   * Retry failed upload
   */
  const retryUpload = useCallback(
    (fileId: string) => {
      const file = files.find((f) => f.id === fileId)
      if (!file) return

      // Reset to uploading state
      setFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? { ...f, stage: 'uploading', stageProgress: 0, errorDetails: undefined }
            : f
        )
      )

      // Restart upload
      uploadMutation.mutate(file.file)
    },
    [files, uploadMutation]
  )

  /**
   * Clear all completed/errored files
   */
  const clearCompleted = useCallback(() => {
    setFiles((prev) =>
      prev.filter((f) => f.stage !== 'complete' && f.stage !== 'error')
    )
  }, [])

  /**
   * Clear all files
   */
  const clearAll = useCallback(() => {
    setFiles([])
  }, [])

  return {
    files,
    isUploading: uploadMutation.isPending,
    addFiles,
    removeFile,
    startUpload,
    retryUpload,
    clearCompleted,
    clearAll,
    // Computed
    hasQueuedFiles: files.some((f) => f.stage === 'queued'),
    hasProcessingFiles: files.some(
      (f) => f.stage !== 'complete' && f.stage !== 'error' && f.stage !== 'queued'
    ),
    completedCount: files.filter((f) => f.stage === 'complete').length,
    errorCount: files.filter((f) => f.stage === 'error').length,
  }
}

/**
 * Hook for polling document processing status
 */
export function useDocumentStatus(documentId: string | null, enabled = true) {
  return useQuery({
    queryKey: documentKeys.status(documentId ?? ''),
    queryFn: async (): Promise<DocumentStatusResponse> => {
      if (!documentId) throw new Error('No document ID')

      const response = await api.get<APIResponse<DocumentStatusResponse>>(
        `${endpoints.documents.upload}/${documentId}/status`
      )

      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to get status')
      }

      return response.data.data
    },
    enabled: !!documentId && enabled,
    refetchInterval: (query) => {
      // Stop polling when complete or error
      const status = query.state.data?.status
      if (status === 'complete' || status === 'error') return false
      return 2000 // Poll every 2 seconds
    },
  })
}

/**
 * Simulated processing stages for demo
 * In production, this would be replaced by actual server status polling
 */
export function useSimulatedProcessing() {
  const [processingFile, setProcessingFile] = useState<ProcessingFile | null>(null)

  const simulateProcessing = useCallback((file: ProcessingFile) => {
    setProcessingFile(file)

    const stages: ProcessingStage[] = ['uploading', 'extracting', 'analyzing', 'embedding', 'indexing', 'complete']
    let currentStageIndex = 0

    const advanceStage = () => {
      if (currentStageIndex >= stages.length - 1) {
        setProcessingFile((prev) =>
          prev ? { ...prev, stage: 'complete', stageProgress: 100 } : null
        )
        return
      }

      // Simulate progress within stage
      let progress = 0
      const progressInterval = setInterval(() => {
        progress += Math.random() * 30
        if (progress >= 100) {
          clearInterval(progressInterval)
          currentStageIndex++
          setProcessingFile((prev) =>
            prev
              ? {
                  ...prev,
                  stage: stages[currentStageIndex],
                  stageProgress: 0,
                }
              : null
          )
          setTimeout(advanceStage, 500)
        } else {
          setProcessingFile((prev) =>
            prev ? { ...prev, stageProgress: Math.min(progress, 99) } : null
          )
        }
      }, 300)
    }

    advanceStage()
  }, [])

  return {
    processingFile,
    simulateProcessing,
    reset: () => setProcessingFile(null),
  }
}
