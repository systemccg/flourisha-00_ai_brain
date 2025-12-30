'use client'

import {
  Box,
  Text,
  Flex,
  VStack,
} from '@chakra-ui/react'
import {
  type ReactNode,
  type InputHTMLAttributes,
  type TextareaHTMLAttributes,
  type SelectHTMLAttributes,
  forwardRef,
  useState,
  useId,
} from 'react'

/**
 * Base input styles shared across form elements
 */
const baseInputStyles = {
  width: '100%',
  padding: '10px 14px',
  fontSize: '14px',
  color: 'white',
  backgroundColor: '#1a1a2e',
  border: '1px solid #374151',
  borderRadius: '8px',
  outline: 'none',
  transition: 'border-color 0.15s, box-shadow 0.15s',
}

const focusStyles = {
  borderColor: '#8b5cf6',
  boxShadow: '0 0 0 3px rgba(139, 92, 246, 0.2)',
}

const errorStyles = {
  borderColor: '#ef4444',
  boxShadow: '0 0 0 3px rgba(239, 68, 68, 0.2)',
}

/**
 * Form field wrapper props
 */
interface FormFieldProps {
  label?: string
  error?: string
  hint?: string
  required?: boolean
  children: ReactNode
}

/**
 * FormField wrapper component
 * Provides consistent layout for form inputs with label, error, and hint
 */
export function FormField({
  label,
  error,
  hint,
  required,
  children,
}: FormFieldProps) {
  return (
    <VStack align="stretch" gap={1.5} w="full">
      {label && (
        <Flex align="center" gap={1}>
          <Text fontSize="sm" fontWeight="500" color="gray.300">
            {label}
          </Text>
          {required && (
            <Text color="red.400" fontSize="sm">
              *
            </Text>
          )}
        </Flex>
      )}
      {children}
      {error && (
        <Flex align="center" gap={1.5}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#ef4444' }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <Text fontSize="sm" color="red.400">
            {error}
          </Text>
        </Flex>
      )}
      {hint && !error && (
        <Text fontSize="sm" color="gray.500">
          {hint}
        </Text>
      )}
    </VStack>
  )
}

/**
 * Text input props
 */
interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  error?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  inputSize?: 'sm' | 'md' | 'lg'
}

/**
 * Text input component
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ error, leftIcon, rightIcon, inputSize = 'md', style, ...props }, ref) => {
    const [focused, setFocused] = useState(false)

    const sizeStyles = {
      sm: { padding: '6px 10px', fontSize: '13px' },
      md: { padding: '10px 14px', fontSize: '14px' },
      lg: { padding: '12px 16px', fontSize: '16px' },
    }

    const inputStyles = {
      ...baseInputStyles,
      ...sizeStyles[inputSize],
      ...(focused && !error ? focusStyles : {}),
      ...(error ? errorStyles : {}),
      paddingLeft: leftIcon ? '40px' : sizeStyles[inputSize].padding,
      paddingRight: rightIcon ? '40px' : sizeStyles[inputSize].padding,
      ...style,
    }

    return (
      <Box position="relative" w="full">
        {leftIcon && (
          <Box
            position="absolute"
            left={3}
            top="50%"
            transform="translateY(-50%)"
            color="gray.500"
            pointerEvents="none"
          >
            {leftIcon}
          </Box>
        )}
        <input
          ref={ref}
          style={inputStyles}
          onFocus={(e) => {
            setFocused(true)
            props.onFocus?.(e)
          }}
          onBlur={(e) => {
            setFocused(false)
            props.onBlur?.(e)
          }}
          {...props}
        />
        {rightIcon && (
          <Box
            position="absolute"
            right={3}
            top="50%"
            transform="translateY(-50%)"
            color="gray.500"
          >
            {rightIcon}
          </Box>
        )}
      </Box>
    )
  }
)
Input.displayName = 'Input'

/**
 * Textarea props
 */
interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

/**
 * Textarea component
 */
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ error, resize = 'vertical', style, ...props }, ref) => {
    const [focused, setFocused] = useState(false)

    const textareaStyles = {
      ...baseInputStyles,
      minHeight: '100px',
      resize,
      ...(focused && !error ? focusStyles : {}),
      ...(error ? errorStyles : {}),
      ...style,
    }

    return (
      <textarea
        ref={ref}
        style={textareaStyles as React.CSSProperties}
        onFocus={(e) => {
          setFocused(true)
          props.onFocus?.(e)
        }}
        onBlur={(e) => {
          setFocused(false)
          props.onBlur?.(e)
        }}
        {...props}
      />
    )
  }
)
Textarea.displayName = 'Textarea'

/**
 * Select option type
 */
export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

/**
 * Select props
 */
interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  error?: boolean
  options: SelectOption[]
  placeholder?: string
  inputSize?: 'sm' | 'md' | 'lg'
}

/**
 * Select component
 */
export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ error, options, placeholder, inputSize = 'md', style, ...props }, ref) => {
    const [focused, setFocused] = useState(false)

    const sizeStyles = {
      sm: { padding: '6px 32px 6px 10px', fontSize: '13px' },
      md: { padding: '10px 36px 10px 14px', fontSize: '14px' },
      lg: { padding: '12px 40px 12px 16px', fontSize: '16px' },
    }

    const selectStyles = {
      ...baseInputStyles,
      ...sizeStyles[inputSize],
      appearance: 'none' as const,
      backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
      backgroundRepeat: 'no-repeat',
      backgroundPosition: 'right 12px center',
      ...(focused && !error ? focusStyles : {}),
      ...(error ? errorStyles : {}),
      ...style,
    }

    return (
      <select
        ref={ref}
        style={selectStyles}
        onFocus={(e) => {
          setFocused(true)
          props.onFocus?.(e)
        }}
        onBlur={(e) => {
          setFocused(false)
          props.onBlur?.(e)
        }}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
    )
  }
)
Select.displayName = 'Select'

/**
 * Checkbox props
 */
interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'size'> {
  label?: string
  error?: boolean
  inputSize?: 'sm' | 'md' | 'lg'
}

/**
 * Checkbox component
 */
export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, error, inputSize = 'md', ...props }, ref) => {
    const id = useId()

    const sizeMap = {
      sm: { box: 16, icon: 10 },
      md: { box: 20, icon: 12 },
      lg: { box: 24, icon: 14 },
    }

    const size = sizeMap[inputSize]

    return (
      <label
        htmlFor={props.id || id}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          cursor: props.disabled ? 'not-allowed' : 'pointer',
          opacity: props.disabled ? 0.5 : 1,
        }}
      >
        <Box position="relative">
          <input
            ref={ref}
            type="checkbox"
            id={props.id || id}
            style={{
              position: 'absolute',
              opacity: 0,
              width: size.box,
              height: size.box,
              cursor: props.disabled ? 'not-allowed' : 'pointer',
            }}
            {...props}
          />
          <Box
            w={`${size.box}px`}
            h={`${size.box}px`}
            borderRadius="md"
            borderWidth={2}
            borderColor={error ? 'red.500' : props.checked ? 'purple.500' : 'gray.600'}
            bg={props.checked ? 'purple.500' : 'transparent'}
            display="flex"
            alignItems="center"
            justifyContent="center"
            transition="all 0.15s"
          >
            {props.checked && (
              <svg
                width={size.icon}
                height={size.icon}
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            )}
          </Box>
        </Box>
        {label && (
          <Text
            fontSize={inputSize === 'sm' ? 'sm' : inputSize === 'lg' ? 'md' : 'sm'}
            color="gray.300"
          >
            {label}
          </Text>
        )}
      </label>
    )
  }
)
Checkbox.displayName = 'Checkbox'

/**
 * Radio group props
 */
interface RadioOption {
  value: string
  label: string
  disabled?: boolean
}

interface RadioGroupProps {
  name: string
  options: RadioOption[]
  value?: string
  onChange?: (value: string) => void
  error?: boolean
  orientation?: 'horizontal' | 'vertical'
  inputSize?: 'sm' | 'md' | 'lg'
}

/**
 * RadioGroup component
 */
export function RadioGroup({
  name,
  options,
  value,
  onChange,
  error,
  orientation = 'vertical',
  inputSize = 'md',
}: RadioGroupProps) {
  const sizeMap = {
    sm: { box: 16, dot: 8 },
    md: { box: 20, dot: 10 },
    lg: { box: 24, dot: 12 },
  }

  const size = sizeMap[inputSize]

  return (
    <Flex
      flexDirection={orientation === 'horizontal' ? 'row' : 'column'}
      gap={orientation === 'horizontal' ? 4 : 2}
    >
      {options.map((option) => {
        const isSelected = value === option.value
        const id = `${name}-${option.value}`

        return (
          <label
            key={option.value}
            htmlFor={id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: option.disabled ? 'not-allowed' : 'pointer',
              opacity: option.disabled ? 0.5 : 1,
            }}
          >
            <Box position="relative">
              <input
                type="radio"
                id={id}
                name={name}
                value={option.value}
                checked={isSelected}
                disabled={option.disabled}
                onChange={(e) => onChange?.(e.target.value)}
                style={{
                  position: 'absolute',
                  opacity: 0,
                  width: size.box,
                  height: size.box,
                  cursor: option.disabled ? 'not-allowed' : 'pointer',
                }}
              />
              <Box
                w={`${size.box}px`}
                h={`${size.box}px`}
                borderRadius="full"
                borderWidth={2}
                borderColor={error ? 'red.500' : isSelected ? 'purple.500' : 'gray.600'}
                display="flex"
                alignItems="center"
                justifyContent="center"
                transition="all 0.15s"
              >
                {isSelected && (
                  <Box
                    w={`${size.dot}px`}
                    h={`${size.dot}px`}
                    borderRadius="full"
                    bg="purple.500"
                  />
                )}
              </Box>
            </Box>
            <Text
              fontSize={inputSize === 'sm' ? 'sm' : inputSize === 'lg' ? 'md' : 'sm'}
              color="gray.300"
            >
              {option.label}
            </Text>
          </label>
        )
      })}
    </Flex>
  )
}

/**
 * Switch props
 */
interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'size'> {
  label?: string
  inputSize?: 'sm' | 'md' | 'lg'
}

/**
 * Switch toggle component
 */
export const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  ({ label, inputSize = 'md', ...props }, ref) => {
    const id = useId()

    const sizeMap = {
      sm: { track: { w: 32, h: 18 }, thumb: 14 },
      md: { track: { w: 40, h: 22 }, thumb: 18 },
      lg: { track: { w: 48, h: 26 }, thumb: 22 },
    }

    const size = sizeMap[inputSize]

    return (
      <label
        htmlFor={props.id || id}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          cursor: props.disabled ? 'not-allowed' : 'pointer',
          opacity: props.disabled ? 0.5 : 1,
        }}
      >
        <Box position="relative">
          <input
            ref={ref}
            type="checkbox"
            id={props.id || id}
            style={{
              position: 'absolute',
              opacity: 0,
              width: size.track.w,
              height: size.track.h,
              cursor: props.disabled ? 'not-allowed' : 'pointer',
            }}
            {...props}
          />
          <Box
            w={`${size.track.w}px`}
            h={`${size.track.h}px`}
            borderRadius="full"
            bg={props.checked ? 'purple.500' : 'gray.700'}
            transition="all 0.2s"
            position="relative"
          >
            <Box
              position="absolute"
              top="50%"
              left={props.checked ? `${size.track.w - size.thumb - 2}px` : '2px'}
              transform="translateY(-50%)"
              w={`${size.thumb}px`}
              h={`${size.thumb}px`}
              borderRadius="full"
              bg="white"
              transition="all 0.2s"
              shadow="sm"
            />
          </Box>
        </Box>
        {label && (
          <Text
            fontSize={inputSize === 'sm' ? 'sm' : inputSize === 'lg' ? 'md' : 'sm'}
            color="gray.300"
          >
            {label}
          </Text>
        )}
      </label>
    )
  }
)
Switch.displayName = 'Switch'
