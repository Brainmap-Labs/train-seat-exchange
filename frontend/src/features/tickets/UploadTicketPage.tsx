import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, Image, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'

type UploadStep = 'upload' | 'processing' | 'verify' | 'complete'

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
  const [step, setStep] = useState<UploadStep>('upload')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setUploadedFile(file)
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
    setStep('processing')
    setIsProcessing(true)

    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Mock extracted data
    setExtractedData({
      pnr: '4521678901',
      trainNumber: '12301',
      trainName: 'Howrah Rajdhani Express',
      travelDate: '2025-01-15',
      boardingStation: 'NDLS - New Delhi',
      destinationStation: 'HWH - Howrah Junction',
      classType: '3A',
      passengers: [
        { name: 'RAHUL KUMAR', age: 35, gender: 'M', coach: 'B2', seatNumber: 45, berthType: 'LB' },
        { name: 'PRIYA KUMAR', age: 32, gender: 'F', coach: 'B2', seatNumber: 47, berthType: 'MB' },
        { name: 'ARYAN KUMAR', age: 8, gender: 'M', coach: 'B3', seatNumber: 12, berthType: 'UB' },
      ],
    })

    setIsProcessing(false)
    setStep('verify')
  }

  const handleConfirm = async () => {
    // TODO: API call to save ticket
    setStep('complete')
    setTimeout(() => navigate('/dashboard'), 1500)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold text-slate-900 mb-2">
        Upload Train Ticket
      </h1>
      <p className="text-slate-600 mb-8">
        Upload your IRCTC e-ticket and we'll extract the details automatically
      </p>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-8">
        {['Upload', 'Processing', 'Verify', 'Done'].map((label, index) => {
          const stepIndex = ['upload', 'processing', 'verify', 'complete'].indexOf(step)
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

      {/* Upload Step */}
      {step === 'upload' && (
        <Card>
          <CardContent className="p-8">
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
            <Button variant="outline" onClick={() => setStep('upload')} className="flex-1">
              Upload Different Ticket
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

