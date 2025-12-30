'use client'

import { Box, Flex, Text, VStack, Button, Badge, Grid, GridItem } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import {
  DocumentUploadDropzone,
  UploadProgressIndicator,
  CompactUploadProgress,
  DocumentPreviewModal,
  type UploadFile,
  type ProcessingFile,
  type ProcessingStage,
  type DocumentPreviewData,
} from '@/components/documents'
import { useToast } from '@/components/ui'

/**
 * Upload icon
 */
const UploadIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
)

/**
 * Documents page - Upload and manage documents
 */
export default function DocumentsPage() {
  const toast = useToast()
  const [files, setFiles] = useState<ProcessingFile[]>([])
  const [selectedDocument, setSelectedDocument] = useState<DocumentPreviewData | null>(null)
  const [isPreviewOpen, setPreviewOpen] = useState(false)

  /**
   * Handle files added to dropzone
   */
  const handleFilesAdd = useCallback((newFiles: UploadFile[]) => {
    const processingFiles: ProcessingFile[] = newFiles.map((f) => ({
      ...f,
      stage: 'queued' as ProcessingStage,
      stageProgress: 0,
    }))
    setFiles((prev) => [...prev, ...processingFiles])

    toast.success(
      `${newFiles.length} file${newFiles.length > 1 ? 's' : ''} added`,
      'Click "Start Upload" to begin processing'
    )
  }, [toast])

  /**
   * Handle file removal
   */
  const handleFileRemove = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId))
  }, [])

  /**
   * Simulate upload and processing
   */
  const startUpload = useCallback(() => {
    const queuedFiles = files.filter((f) => f.stage === 'queued')
    if (queuedFiles.length === 0) return

    toast.info(
      'Upload started',
      `Processing ${queuedFiles.length} file${queuedFiles.length > 1 ? 's' : ''}`
    )

    // Simulate processing for each file
    queuedFiles.forEach((file, index) => {
      simulateFileProcessing(file.id, index * 2000)
    })
  }, [files, toast])

  /**
   * Simulate file processing stages
   */
  const simulateFileProcessing = useCallback((fileId: string, delay: number) => {
    const stages: ProcessingStage[] = ['uploading', 'extracting', 'analyzing', 'embedding', 'indexing', 'complete']

    setTimeout(() => {
      let currentStageIndex = 0

      const advanceStage = () => {
        if (currentStageIndex >= stages.length) return

        const currentStage = stages[currentStageIndex]

        // Update stage
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId
              ? { ...f, stage: currentStage, stageProgress: 0 }
              : f
          )
        )

        if (currentStage === 'complete') {
          // Add mock extracted data
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? {
                    ...f,
                    extractedText: 'This is sample extracted text from the document. In production, this would contain the actual content extracted using Claude or Docling backend.',
                    entities: [
                      { name: 'John Smith', type: 'person' },
                      { name: 'Acme Corp', type: 'organization' },
                      { name: 'Q1 2025', type: 'date' },
                    ],
                  }
                : f
            )
          )
          return
        }

        // Simulate progress within stage
        let progress = 0
        const progressInterval = setInterval(() => {
          progress += Math.random() * 25 + 5

          if (progress >= 100) {
            clearInterval(progressInterval)
            currentStageIndex++
            setTimeout(advanceStage, 300)
          } else {
            setFiles((prev) =>
              prev.map((f) =>
                f.id === fileId
                  ? { ...f, stageProgress: Math.min(Math.round(progress), 99) }
                  : f
              )
            )
          }
        }, 200)
      }

      advanceStage()
    }, delay)
  }, [])

  /**
   * Handle retry for failed uploads
   */
  const handleRetry = useCallback((fileId: string) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.id === fileId
          ? { ...f, stage: 'queued' as ProcessingStage, stageProgress: 0, errorDetails: undefined }
          : f
      )
    )
  }, [])

  /**
   * Clear completed files
   */
  const clearCompleted = useCallback(() => {
    setFiles((prev) => prev.filter((f) => f.stage !== 'complete' && f.stage !== 'error'))
  }, [])

  /**
   * View document preview
   */
  const viewDocument = useCallback((file: ProcessingFile) => {
    if (file.stage !== 'complete') return

    const previewData: DocumentPreviewData = {
      id: file.id,
      name: file.name,
      type: file.type.split('/').pop() || 'unknown',
      size: file.size,
      uploadedAt: new Date().toISOString(),
      extractedText: file.extractedText || 'No text extracted',
      summary: 'This document contains information about the quarterly business review. Key topics include revenue projections, team performance metrics, and strategic initiatives for the upcoming quarter.',
      entities: file.entities?.map((e) => ({ ...e, type: e.type as any })) || [],
      relationships: [
        { source: 'John Smith', target: 'Acme Corp', type: 'WORKS_AT' },
        { source: 'Q1 2025', target: 'Business Review', type: 'RELATED_TO' },
      ],
      processingDetails: {
        backend: 'claude',
        duration_ms: 2340,
        extractionMethod: 'vision',
      },
    }

    setSelectedDocument(previewData)
    setPreviewOpen(true)
  }, [])

  // Calculate stats
  const queuedCount = files.filter((f) => f.stage === 'queued').length
  const processingCount = files.filter(
    (f) => f.stage !== 'queued' && f.stage !== 'complete' && f.stage !== 'error'
  ).length
  const completedCount = files.filter((f) => f.stage === 'complete').length
  const errorCount = files.filter((f) => f.stage === 'error').length

  // Separate files by status for display
  const queuedFiles = files.filter((f) => f.stage === 'queued')
  const activeFiles = files.filter(
    (f) => f.stage !== 'queued' && f.stage !== 'complete' && f.stage !== 'error'
  )
  const completedFiles = files.filter((f) => f.stage === 'complete' || f.stage === 'error')

  return (
    <PageContainer>
      <PageHeader
        title="Document Upload"
        description="Upload documents to extract content and add to your knowledge base."
        actions={
          <Flex gap={2}>
            {completedCount > 0 && (
              <Button size="sm" variant="outline" colorPalette="gray" onClick={clearCompleted}>
                Clear Completed
              </Button>
            )}
            {queuedCount > 0 && (
              <Button size="sm" colorPalette="purple" onClick={startUpload}>
                <UploadIcon />
                <Text ml={2}>Start Upload ({queuedCount})</Text>
              </Button>
            )}
          </Flex>
        }
      />

      <Grid templateColumns={{ base: '1fr', lg: '1fr 400px' }} gap={6}>
        {/* Main content */}
        <GridItem>
          <VStack gap={6} align="stretch">
            {/* Upload dropzone */}
            <DocumentUploadDropzone
              files={queuedFiles}
              onFilesAdd={handleFilesAdd}
              onFileRemove={handleFileRemove}
              disabled={processingCount > 0}
            />

            {/* Compact progress for multiple files */}
            {activeFiles.length > 1 && (
              <CompactUploadProgress files={activeFiles} />
            )}

            {/* Individual progress indicators */}
            {activeFiles.length === 1 && (
              <UploadProgressIndicator
                file={activeFiles[0]}
                showAllStages
                showPreview={false}
                onCancel={() => handleFileRemove(activeFiles[0].id)}
              />
            )}
          </VStack>
        </GridItem>

        {/* Sidebar - Completed files */}
        <GridItem>
          <Box
            bg="gray.900"
            borderRadius="xl"
            borderWidth={1}
            borderColor="gray.700"
            overflow="hidden"
          >
            <Flex
              align="center"
              justify="space-between"
              px={4}
              py={3}
              borderBottomWidth={1}
              borderColor="gray.800"
            >
              <Text color="gray.200" fontSize="sm" fontWeight="600">
                Processed Documents
              </Text>
              <Badge colorPalette="gray" size="sm">
                {completedCount + errorCount}
              </Badge>
            </Flex>

            {completedFiles.length === 0 ? (
              <Flex
                direction="column"
                align="center"
                justify="center"
                py={12}
                px={4}
              >
                <Box color="gray.600" mb={3}>
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                  </svg>
                </Box>
                <Text color="gray.500" fontSize="sm" textAlign="center">
                  No documents processed yet
                </Text>
                <Text color="gray.600" fontSize="xs" textAlign="center" mt={1}>
                  Upload documents to get started
                </Text>
              </Flex>
            ) : (
              <VStack gap={0} align="stretch">
                {completedFiles.map((file) => (
                  <Flex
                    key={file.id}
                    align="center"
                    gap={3}
                    px={4}
                    py={3}
                    borderBottomWidth={1}
                    borderColor="gray.800"
                    cursor={file.stage === 'complete' ? 'pointer' : 'default'}
                    _hover={file.stage === 'complete' ? { bg: 'gray.800' } : undefined}
                    onClick={() => viewDocument(file)}
                  >
                    <Box color={file.stage === 'error' ? 'red.400' : 'green.400'}>
                      {file.stage === 'error' ? (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <line x1="15" y1="9" x2="9" y2="15" />
                          <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                      ) : (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                          <polyline points="22 4 12 14.01 9 11.01" />
                        </svg>
                      )}
                    </Box>

                    <Box flex={1} overflow="hidden">
                      <Text
                        color="gray.200"
                        fontSize="sm"
                        fontWeight="500"
                        overflow="hidden"
                        textOverflow="ellipsis"
                        whiteSpace="nowrap"
                      >
                        {file.name}
                      </Text>
                      {file.stage === 'error' && file.errorDetails && (
                        <Text color="red.300" fontSize="xs">
                          {file.errorDetails}
                        </Text>
                      )}
                      {file.stage === 'complete' && file.entities && (
                        <Text color="gray.500" fontSize="xs">
                          {file.entities.length} entities found
                        </Text>
                      )}
                    </Box>

                    {file.stage === 'error' && (
                      <Button
                        size="xs"
                        variant="ghost"
                        colorPalette="red"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRetry(file.id)
                        }}
                      >
                        Retry
                      </Button>
                    )}

                    {file.stage === 'complete' && (
                      <Box color="gray.500">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="9 18 15 12 9 6" />
                        </svg>
                      </Box>
                    )}
                  </Flex>
                ))}
              </VStack>
            )}
          </Box>
        </GridItem>
      </Grid>

      {/* Document preview modal */}
      <DocumentPreviewModal
        isOpen={isPreviewOpen}
        onClose={() => setPreviewOpen(false)}
        document={selectedDocument}
      />
    </PageContainer>
  )
}
