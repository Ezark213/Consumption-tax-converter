import { FC } from 'react'
import { Check, AlertCircle, Loader2 } from 'lucide-react'
import { ProcessingStep } from '../types'

interface ProgressIndicatorProps {
  steps: ProcessingStep[];
}

const ProgressIndicator: FC<ProgressIndicatorProps> = ({ steps }) => {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center space-x-4">
          <div className={`
            flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
            ${step.status === 'completed' 
              ? 'bg-green-500 text-white' 
              : step.status === 'current' 
                ? 'bg-blue-500 text-white' 
                : step.status === 'error' 
                  ? 'bg-red-500 text-white' 
                  : 'bg-gray-300 text-gray-600'
            }
          `}>
            {step.status === 'completed' ? (
              <Check className="h-4 w-4" />
            ) : step.status === 'current' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : step.status === 'error' ? (
              <AlertCircle className="h-4 w-4" />
            ) : (
              <span>{index + 1}</span>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className={`
              text-sm font-medium
              ${step.status === 'completed' 
                ? 'text-green-700' 
                : step.status === 'current' 
                  ? 'text-blue-700' 
                  : step.status === 'error' 
                    ? 'text-red-700' 
                    : 'text-gray-500'
              }
            `}>
              {step.name}
            </p>
            
            {step.status === 'current' && step.progress !== undefined && (
              <div className="mt-1">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${step.progress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{step.progress}%</p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export default ProgressIndicator