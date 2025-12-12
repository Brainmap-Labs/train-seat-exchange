import { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useDropzone } from 'react-dropzone'
import { Image, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { ticketApi } from '@/services/api'



type UploadStep = 'input' | 'processing' | 'verify' | 'complete'

interface ExtractedData {
  pnr: string
  trainNumber: string
  trainName: string
  travelDate: string
  boardingStation: string
  destinationStation: string
  classType: string
  passengers: Array<{
    name: string
    age: number
    gender: string
    coach: string
    seatNumber: number
    berthType: string
  }>
}

export function UploadTicketPage() {
    const { isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { replace: true })
    }
  }, [isAuthenticated, navigate])
  const [step, setStep] = useState<UploadStep>('input')
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      processTicket(file)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })



  const processTicket = async (file: File) => {
    setError(null)
    setStep('processing')


    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await ticketApi.uploadImage(formData)
      const data = response.data.data
      
      setExtractedData({
        pnr: data.pnr || '',
        trainNumber: data.train_number || '',
        trainName: data.train_name || '',
        travelDate: data.travel_date || '',
        boardingStation: data.boarding_station || '',
        destinationStation: data.destination_station || '',
        classType: data.class_type || '',
        passengers: (data.passengers || []).map((p: any) => ({
          name: p.name || 'Unknown',
          age: p.age || 0,
          gender: p.gender || 'M',
          coach: p.coach || '',
          seatNumber: p.seat_number || 0,
          berthType: p.berth_type || '',
        })),
      })


      setStep('verify')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process image. Please try again.')

      setStep('input')
    }
  }

  const handleConfirm = async () => {
    if (!extractedData) return
    

    setError(null)
    
    try {
      // Parse stations
      const [boardingCode, ...boardingNameParts] = (extractedData.boardingStation || '').split(' - ')
      const [destCode, ...destNameParts] = (extractedData.destinationStation || '').split(' - ')
      
      // Parse and format travel date
      let travelDate: string
      if (extractedData.travelDate) {
        // Try to parse the date string and convert to ISO format
        const date = new Date(extractedData.travelDate)
        if (isNaN(date.getTime())) {
          // If parsing fails, try common Indian date formats
          // Format: "26-Apr-2024" or "26/04/2024"
          const dateStr = extractedData.travelDate.trim()
          const parts = dateStr.split(/[-/]/)
          if (parts.length === 3) {
            const day = parseInt(parts[0])
            const monthStr = parts[1]
            const year = parseInt(parts[2])
            
            // Map month names to numbers
            const monthMap: { [key: string]: number } = {
              'jan': 0, 'feb': 1, 'mar': 2, 'apr': 3, 'may': 4, 'jun': 5,
              'jul': 6, 'aug': 7, 'sep': 8, 'oct': 9, 'nov': 10, 'dec': 11
            }
            
            let month: number
            if (isNaN(parseInt(monthStr))) {
              month = monthMap[monthStr.toLowerCase().slice(0, 3)] ?? 0
            } else {
              month = parseInt(monthStr) - 1
            }
            
            const parsedDate = new Date(year, month, day)
            travelDate = parsedDate.toISOString()
          } else {
            throw new Error('Invalid date format')
          }
        } else {
          travelDate = date.toISOString()
        }
      } else {
        throw new Error('Travel date is required')
      }
      
      // Create ticket payload
      const ticketPayload = {
        pnr: extractedData.pnr || '',
        train_number: extractedData.trainNumber || '',
        train_name: extractedData.trainName || '',
        travel_date: travelDate,
        boarding_station_code: boardingCode || '',
        boarding_station_name: boardingNameParts.join(' - ') || boardingCode || '',
        destination_station_code: destCode || '',
        destination_station_name: destNameParts.join(' - ') || destCode || '',
        class_type: extractedData.classType || '2S',
        quota: 'GN',
        passengers: extractedData.passengers.map(p => ({
          name: p.name || 'Unknown',
          age: p.age || 0,
          gender: p.gender || 'M',
          coach: p.coach || 'UNKNOWN',
          seat_number: p.seatNumber || 0,
          berth_type: p.berthType || 'LB',
          booking_status: 'CNF',
          current_status: 'CNF',
        })),
      }
      
      console.log('Sending ticket payload:', ticketPayload)
      await ticketApi.create(ticketPayload)
      setStep('complete')
      setTimeout(() => navigate('/dashboard'), 1500)
    } catch (err: any) {
      console.error('Error saving ticket:', err)
      console.error('Error response:', err.response?.data)
      
      // Handle validation errors (422)
      let errorMessage = 'Failed to save ticket. Please try again.'
      if (err.response?.data) {
        if (err.response.data.detail) {
          if (Array.isArray(err.response.data.detail)) {
            // Pydantic validation errors
            errorMessage = err.response.data.detail
              .map((e: any) => `${e.loc?.join('.')}: ${e.msg}`)
              .join(', ')
          } else {
            errorMessage = err.response.data.detail
          }
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)

    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold text-slate-900 mb-2">
        Add Train Ticket
      </h1>
      <p className="text-slate-600 mb-8">
        Enter your PNR number or upload ticket image to get started
      </p>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-8">
        {['Input', 'Processing', 'Verify', 'Done'].map((label, index) => {
          const stepIndex = ['input', 'processing', 'verify', 'complete'].indexOf(step)
          const isActive = index === stepIndex
          const isComplete = index < stepIndex

          return (
            <div key={label} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                ${isComplete ? 'bg-green-500 text-white' : 
                  isActive ? 'bg-railway-blue text-white' : 
                  'bg-slate-200 text-slate-500'}
              `}>
                {isComplete ? <CheckCircle className="w-5 h-5" /> : index + 1}
              </div>
              <span className={`ml-2 text-sm ${isActive ? 'text-slate-900 font-medium' : 'text-slate-500'}`}>
                {label}
              </span>
              {index < 3 && <div className="w-8 h-0.5 bg-slate-200 mx-2" />}
            </div>
          )
        })}
      </div>

      {/* Input Step */}
      {step === 'input' && (
        <div className="space-y-6">
          {/* Only show image upload method */}
          <Card>
            <CardContent className="p-8">
              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors
                  ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-slate-300 hover:border-primary-400'}
                `}
              >
                <input {...getInputProps()} />
                <div className="flex justify-center gap-4 mb-4">
                  <Image className="w-12 h-12 text-slate-400" />
                  <FileText className="w-12 h-12 text-slate-400" />
                </div>
                <h3 className="font-semibold text-lg text-slate-900 mb-2">
                  {isDragActive ? 'Drop your ticket here' : 'Drag & drop your ticket'}
                </h3>
                <p className="text-slate-600 mb-4">
                  or click to browse from your device
                </p>
                <p className="text-sm text-slate-500">
                  Supports: JPEG, PNG, PDF (max 10MB)
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Processing Step */}
      {step === 'processing' && (
        <Card>
          <CardContent className="p-12 text-center">
            <Loader2 className="w-16 h-16 text-railway-blue animate-spin mx-auto mb-4" />
            <h3 className="font-display text-xl font-bold text-slate-900 mb-2">
              Processing Your Ticket
            </h3>
            <p className="text-slate-600">
              Extracting details using AI... This may take a few seconds.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Verify Step */}
      {step === 'verify' && extractedData && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h3 className="font-display text-lg font-bold text-slate-900">
                Verify Ticket Details
              </h3>
              <p className="text-sm text-slate-600">
                Please verify the extracted information and correct if needed
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <Input label="PNR Number" value={extractedData.pnr} readOnly />
                <Input label="Train" value={`${extractedData.trainNumber} - ${extractedData.trainName}`} readOnly />
                <Input label="Travel Date" value={extractedData.travelDate} readOnly />
                <Input label="Class" value={extractedData.classType} readOnly />
                <Input label="From" value={extractedData.boardingStation} readOnly />
                <Input label="To" value={extractedData.destinationStation} readOnly />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="font-display text-lg font-bold text-slate-900">
                Passengers ({extractedData.passengers.length})
              </h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {extractedData.passengers.map((p, index) => (
                  <div key={index} className="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3">
                    <div>
                      <p className="font-medium">{p.name}</p>
                      <p className="text-sm text-slate-500">{p.age}yrs • {p.gender === 'M' ? 'Male' : 'Female'}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-mono font-bold">{p.coach}/{p.seatNumber}</p>
                      <p className="text-sm text-slate-500">{p.berthType}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Alert for scattered seats */}
              {new Set(extractedData.passengers.map(p => p.coach)).size > 1 && (
                <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3">
                  <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-amber-800">Seats are scattered!</p>
                    <p className="text-sm text-amber-700">
                      Your family members are in different coaches. We'll help you find exchanges.
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex gap-4">
            <Button variant="outline" onClick={() => {
              setStep('input')
              setExtractedData(null)

              // setUploadedFile(null) removed
              setError(null)
            }} className="flex-1">
              Start Over
            </Button>
            <Button onClick={handleConfirm} className="flex-1">
              Confirm & Save
            </Button>
          </div>
        </div>
      )}

      {/* Complete Step */}
      {step === 'complete' && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h3 className="font-display text-xl font-bold text-slate-900 mb-2">
              Ticket Added Successfully!
            </h3>
            <p className="text-slate-600">
              Redirecting to your dashboard...
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

