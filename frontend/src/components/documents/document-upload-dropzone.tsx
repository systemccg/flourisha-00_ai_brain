'use client'

import { Box, Flex, Text, VStack, Badge } from '@chakra-ui/react'
import { useState, useCallback, useRef, type DragEvent, type ChangeEvent } from 'react'

/**
 * Supported file types for document upload
 */
export const SUPPORTED_FILE_TYPES = {
  // Documents
  'application/pdf': { ext: '.pdf', label: 'PDF', color: 'red' },
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { ext: '.docx', label: 'DOCX', color: 'blue' },
  'application/msword': { ext: '.doc', label: 'DOC', color: 'blue' },
  'text/plain': { ext: '.txt', label: 'TXT', color: 'gray' },
  'text/markdown': { ext: '.md', label: 'MD', color: 'gray' },
  // Spreadsheets
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { ext: '.xlsx', label: 'XLSX', color: 'green' },
  'application/vnd.ms-excel': { ext: '.xls', label: 'XLS', color: 'green' },
  'text/csv': { ext: '.csv', label: 'CSV', color: 'green' },
  // Images
  'image/png': { ext: '.png', label: 'PNG', color: 'purple' },
  'image/jpeg': { ext: '.jpg', label: 'JPG', color: 'purple' },
  'image/gif': { ext: '.gif', label: 'GIF', color: 'purple' },
  'image/webp': { ext: '.webp', label: 'WEBP', color: 'purple' },
} as const

export type SupportedMimeType = keyof typeof SUPPORTED_FILE_TYPES

/**
 * File with upload metadata
 */
export interface UploadFile {
  id: string
  file: File
  name: string
  size: number
  type: SupportedMimeType | string
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error'
  progress: number
  error?: string
}

/**
 * Upload icon
 */
const UploadIcon = () => (
  <svg
    width="48"
    height="48"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
)

/**
 * File icon based on type
 */
const FileIcon = ({ type }: { type: string }) => {
  const isImage = type.startsWith('image/')
  const isPdf = type === 'application/pdf'

  if (isImage) {
    return (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
    )
  }

  if (isPdf) {
    return (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    )
  }

  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
      <polyline points="13 2 13 9 20 9" />
    </svg>
  )
}

/**
 * Format file size to human readable
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/**
 * Generate unique ID for files
 */
function generateFileId(): string {
  return `file_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Check if file type is supported
 */
function isFileTypeSupported(mimeType: string): boolean {
  return mimeType in SUPPORTED_FILE_TYPES
}

/**
 * Props for DocumentUploadDropzone
 */
interface DocumentUploadDropzoneProps {
  /** Maximum file size in bytes (default: 50MB) */
  maxFileSize?: number
  /** Maximum number of files (default: 10) */
  maxFiles?: number
  /** Whether multiple files are allowed */
  multiple?: boolean
  /** Called when files are added */
  onFilesAdd?: (files: UploadFile[]) => void
  /** Called when a file is removed */
  onFileRemove?: (fileId: string) => void
  /** List of files currently in the dropzone */
  files?: UploadFile[]
  /** Whether the dropzone is disabled */
  disabled?: boolean
}

export function DocumentUploadDropzone({
  maxFileSize = 50 * 1024 * 1024, // 50MB
  maxFiles = 10,
  multiple = true,
  onFilesAdd,
  onFileRemove,
  files = [],
  disabled = false,
}: DocumentUploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  /**
   * Validate and process files
   */
  const processFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return

      setError(null)
      const newFiles: UploadFile[] = []
      const errors: string[] = []

      // Check max files limit
      const remainingSlots = maxFiles - files.length
      if (remainingSlots <= 0) {
        setError(`Maximum ${maxFiles} files allowed`)
        return
      }

      const filesToProcess = Math.min(fileList.length, remainingSlots)

      for (let i = 0; i < filesToProcess; i++) {
        const file = fileList[i]

        // Check file type
        if (!isFileTypeSupported(file.type)) {
          errors.push(`${file.name}: Unsupported file type`)
          continue
        }

        // Check file size
        if (file.size > maxFileSize) {
          errors.push(`${file.name}: File too large (max ${formatFileSize(maxFileSize)})`)
          continue
        }

        // Check for duplicates
        if (files.some((f) => f.name === file.name && f.size === file.size)) {
          errors.push(`${file.name}: File already added`)
          continue
        }

        newFiles.push({
          id: generateFileId(),
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          status: 'pending',
          progress: 0,
        })
      }

      if (errors.length > 0) {
        setError(errors.join('. '))
      }

      if (newFiles.length > 0) {
        onFilesAdd?.(newFiles)
      }
    },
    [files, maxFiles, maxFileSize, onFilesAdd]
  )

  /**
   * Handle drag events
   */
  const handleDragEnter = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      if (!disabled) {
        setIsDragging(true)
      }
    },
    [disabled]
  )

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      if (!disabled) {
        setIsDragging(true)
      }
    },
    [disabled]
  )

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      if (disabled) return

      const { files: droppedFiles } = e.dataTransfer
      processFiles(droppedFiles)
    },
    [disabled, processFiles]
  )

  /**
   * Handle file input change
   */
  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      processFiles(e.target.files)
      // Reset input value to allow selecting same file again
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    },
    [processFiles]
  )

  /**
   * Open file dialog
   */
  const openFileDialog = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click()
    }
  }, [disabled])

  /**
   * Get accepted file types for input
   */
  const acceptedTypes = Object.keys(SUPPORTED_FILE_TYPES).join(',')

  return (
    <VStack gap={4} w="full">
      {/* Dropzone area */}
      <Box
        w="full"
        minH="200px"
        borderWidth={2}
        borderStyle="dashed"
        borderColor={isDragging ? 'purple.400' : error ? 'red.400' : 'gray.600'}
        borderRadius="xl"
        bg={isDragging ? 'purple.900' : 'gray.900'}
        cursor={disabled ? 'not-allowed' : 'pointer'}
        opacity={disabled ? 0.5 : 1}
        transition="all 0.2s"
        _hover={
          disabled
            ? undefined
            : {
                borderColor: 'purple.500',
                bg: 'gray.800',
              }
        }
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <Flex
          direction="column"
          align="center"
          justify="center"
          h="full"
          minH="200px"
          px={6}
          py={8}
        >
          <Box color={isDragging ? 'purple.400' : 'gray.500'} mb={4}>
            <UploadIcon />
          </Box>

          <Text color="gray.300" fontSize="md" fontWeight="500" textAlign="center" mb={2}>
            {isDragging ? 'Drop files here' : 'Drag & drop files here'}
          </Text>

          <Text color="gray.500" fontSize="sm" textAlign="center" mb={4}>
            or click to browse
          </Text>

          <Flex gap={2} flexWrap="wrap" justify="center">
            <Badge colorPalette="red" size="sm">
              PDF
            </Badge>
            <Badge colorPalette="blue" size="sm">
              DOCX
            </Badge>
            <Badge colorPalette="green" size="sm">
              XLSX
            </Badge>
            <Badge colorPalette="gray" size="sm">
              TXT
            </Badge>
            <Badge colorPalette="purple" size="sm">
              Images
            </Badge>
          </Flex>

          <Text color="gray.600" fontSize="xs" mt={4}>
            Max {formatFileSize(maxFileSize)} per file{' '}
            {multiple && `(up to ${maxFiles} files)`}
          </Text>
        </Flex>
      </Box>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes}
        multiple={multiple}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />

      {/* Error message */}
      {error && (
        <Box w="full" px={4} py={3} bg="red.900" borderRadius="lg">
          <Text color="red.200" fontSize="sm">
            {error}
          </Text>
        </Box>
      )}

      {/* File list */}
      {files.length > 0 && (
        <VStack w="full" gap={2}>
          {files.map((file) => (
            <FileListItem
              key={file.id}
              file={file}
              onRemove={onFileRemove}
            />
          ))}
        </VStack>
      )}
    </VStack>
  )
}

/**
 * File list item component
 */
interface FileListItemProps {
  file: UploadFile
  onRemove?: (fileId: string) => void
}

function FileListItem({ file, onRemove }: FileListItemProps) {
  const typeMeta = SUPPORTED_FILE_TYPES[file.type as SupportedMimeType]

  const getStatusColor = () => {
    switch (file.status) {
      case 'complete':
        return 'green'
      case 'error':
        return 'red'
      case 'uploading':
      case 'processing':
        return 'purple'
      default:
        return 'gray'
    }
  }

  const getStatusLabel = () => {
    switch (file.status) {
      case 'pending':
        return 'Ready'
      case 'uploading':
        return `Uploading ${file.progress}%`
      case 'processing':
        return 'Processing...'
      case 'complete':
        return 'Complete'
      case 'error':
        return file.error || 'Error'
      default:
        return 'Unknown'
    }
  }

  return (
    <Flex
      w="full"
      align="center"
      gap={3}
      px={4}
      py={3}
      bg="gray.850"
      borderRadius="lg"
      borderWidth={1}
      borderColor="gray.700"
    >
      {/* File icon */}
      <Box color={`${typeMeta?.color || 'gray'}.400`}>
        <FileIcon type={file.type} />
      </Box>

      {/* File info */}
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
        <Flex align="center" gap={2}>
          <Text color="gray.500" fontSize="xs">
            {formatFileSize(file.size)}
          </Text>
          {typeMeta && (
            <Badge colorPalette={typeMeta.color as any} size="sm" variant="subtle">
              {typeMeta.label}
            </Badge>
          )}
        </Flex>
      </Box>

      {/* Progress bar (when uploading) */}
      {(file.status === 'uploading' || file.status === 'processing') && (
        <Box w="100px">
          <Box h="4px" bg="gray.700" borderRadius="full" overflow="hidden">
            <Box
              h="full"
              w={`${file.progress}%`}
              bg="purple.500"
              transition="width 0.2s"
            />
          </Box>
        </Box>
      )}

      {/* Status badge */}
      <Badge
        colorPalette={getStatusColor() as any}
        size="sm"
        variant={file.status === 'complete' ? 'solid' : 'subtle'}
      >
        {getStatusLabel()}
      </Badge>

      {/* Remove button */}
      {file.status !== 'uploading' && file.status !== 'processing' && onRemove && (
        <Box
          as="button"
          color="gray.500"
          _hover={{ color: 'red.400' }}
          transition="color 0.15s"
          onClick={(e: React.MouseEvent) => {
            e.stopPropagation()
            onRemove(file.id)
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </Box>
      )}
    </Flex>
  )
}
