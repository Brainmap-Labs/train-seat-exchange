import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, Image, FileText, Loader2, CheckCircle, AlertCircle, Search, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { ticketApi } from '@/services/api'

type UploadStep = 'input' | 'processing' | 'verify' | 'complete'
type InputMethod = 'pnr' | 'image'

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
  const navigate = useNavigate()
  const [step, setStep] = useState<UploadStep>('input')
  const [inputMethod, setInputMethod] = useState<InputMethod>('pnr')
  const [pnr, setPnr] = useState('')
  // Removed unused uploadedFile
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
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

  const processPnr = async () => {
    if (!pnr || pnr.length !== 10 || !/^\d{10}$/.test(pnr)) {
      setError('Please enter a valid 10-digit PNR number')
      return
    }

    setError(null)
    setStep('processing')
    setIsProcessing(true)

    try {
      const response = await ticketApi.lookupPnr(pnr)
      const data = response.data.data
      
      // Removed unused boardingCode, boardingNameParts, destCode, destNameParts
      
      setExtractedData({
        pnr: data.pnr,
        trainNumber: data.train_number,
        trainName: data.train_name,
        travelDate: data.travel_date,
        boardingStation: data.boarding_station,
        destinationStation: data.destination_station,
        classType: data.class_type,
        passengers: data.passengers.map((p: any) => ({
          name: p.name || 'Unknown',
          age: p.age || 0,
          gender: p.gender || 'M',
          coach: p.coach,
          seatNumber: p.seat_number,
          berthType: p.berth_type,
        })),
      })

      setIsProcessing(false)
      setStep('verify')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch PNR details. Please try again or use image upload.')
      setIsProcessing(false)
      setStep('input')
    }
  }

  const processTicket = async (file: File) => {
    setError(null)
    setStep('processing')
    setIsProcessing(true)

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

      setIsProcessing(false)
      setStep('verify')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process image. Please try again.')
      setIsProcessing(false)
      setStep('input')
    }
  }

  const handleConfirm = async () => {
    if (!extractedData) return
    
    setIsProcessing(true)
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
      setIsProcessing(false)
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
          {/* Method Selection Tabs */}
          <div className="flex gap-2 border-b border-slate-200">
            <button
              onClick={() => setInputMethod('pnr')}
              className={`
                px-6 py-3 font-medium text-sm border-b-2 transition-colors
                ${inputMethod === 'pnr' 
                  ? 'border-railway-blue text-railway-blue' 
                  : 'border-transparent text-slate-500 hover:text-slate-700'}
              `}
            >
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                PNR Number
                <span className="ml-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">Recommended</span>
              </div>
            </button>
            <button
              onClick={() => setInputMethod('image')}
              className={`
                px-6 py-3 font-medium text-sm border-b-2 transition-colors
                ${inputMethod === 'image' 
                  ? 'border-railway-blue text-railway-blue' 
                  : 'border-transparent text-slate-500 hover:text-slate-700'}
              `}
            >
              <div className="flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Upload Image
              </div>
            </button>
          </div>

          {/* PNR Input */}
          {inputMethod === 'pnr' && (
            <Card>
              <CardContent className="p-8">
                <div className="max-w-md mx-auto space-y-4">
                  <div className="flex items-center gap-2 text-green-600 mb-4">
                    <Sparkles className="w-5 h-5" />
                    <p className="text-sm font-medium">Faster and more accurate than OCR</p>
                  </div>
                  
                  <Input
                    label="PNR Number"
                    type="text"
                    placeholder="Enter 10-digit PNR number"
                    value={pnr}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '').slice(0, 10)
                      setPnr(value)
                      setError(null)
                    }}
                    maxLength={10}
                  />
                  
                  {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  )}
                  
                  <Button 
                    onClick={processPnr} 
                    disabled={pnr.length !== 10 || isProcessing}
                    className="w-full"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Fetching Details...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Fetch Ticket Details
                      </>
                    )}
                  </Button>
                  
                  <p className="text-xs text-slate-500 text-center">
                    Your PNR number is on your e-ticket or SMS from IRCTC
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Image Upload */}
          {inputMethod === 'image' && (
            <Card>
              <CardContent className="p-8">
                <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="text-sm text-amber-800">
                    <strong>Tip:</strong> Using PNR number is faster and more accurate. Try the PNR method first!
                  </p>
                </div>
                
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
          )}
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
              setPnr('')
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

