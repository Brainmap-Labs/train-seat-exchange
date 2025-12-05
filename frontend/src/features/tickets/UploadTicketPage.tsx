import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, Image, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { ticketApi } from '@/services/api'

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

    try {
      // Create form data and upload to backend for OCR processing
      const formData = new FormData()
      formData.append('file', file)

      const response = await ticketApi.uploadImage(formData)
      const data = response.data.data

      // Map backend response to frontend format
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
    } catch (error: any) {
      console.error('Failed to process ticket:', error)
      // Fall back to upload step on error
      setStep('upload')
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Failed to process ticket: ${errorMessage}`)
    } finally {
      setIsProcessing(false)
    }
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
          {/* Warning for sample data */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-blue-800">Edit your ticket details below</p>
              <p className="text-sm text-blue-700">
                The OCR system may have extracted sample data. Please update the fields with your actual ticket information.
              </p>
            </div>
          </div>

          <Card>
            <CardHeader>
              <h3 className="font-display text-lg font-bold text-slate-900">
                Verify Ticket Details
              </h3>
              <p className="text-sm text-slate-600">
                Please verify and correct the information as needed
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <Input 
                  label="PNR Number" 
                  value={extractedData.pnr} 
                  onChange={(e) => setExtractedData({...extractedData, pnr: e.target.value})}
                  placeholder="Enter 10-digit PNR"
                />
                <Input 
                  label="Train Number" 
                  value={extractedData.trainNumber}
                  onChange={(e) => setExtractedData({...extractedData, trainNumber: e.target.value})}
                  placeholder="e.g., 12301"
                />
                <Input 
                  label="Train Name" 
                  value={extractedData.trainName}
                  onChange={(e) => setExtractedData({...extractedData, trainName: e.target.value})}
                  placeholder="e.g., Rajdhani Express"
                />
                <Input 
                  label="Travel Date" 
                  value={extractedData.travelDate}
                  onChange={(e) => setExtractedData({...extractedData, travelDate: e.target.value})}
                  placeholder="YYYY-MM-DD"
                  type="date"
                />
                <Input 
                  label="Class" 
                  value={extractedData.classType}
                  onChange={(e) => setExtractedData({...extractedData, classType: e.target.value})}
                  placeholder="e.g., 3A, SL, 2A"
                />
                <Input 
                  label="From Station" 
                  value={extractedData.boardingStation}
                  onChange={(e) => setExtractedData({...extractedData, boardingStation: e.target.value})}
                  placeholder="e.g., NDLS - New Delhi"
                />
                <Input 
                  label="To Station" 
                  value={extractedData.destinationStation}
                  onChange={(e) => setExtractedData({...extractedData, destinationStation: e.target.value})}
                  placeholder="e.g., HWH - Howrah"
                />
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
              <div className="space-y-4">
                {extractedData.passengers.map((p, index) => (
                  <div key={index} className="bg-slate-50 rounded-lg p-4 space-y-3">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <Input
                        label="Name"
                        value={p.name}
                        onChange={(e) => {
                          const newPassengers = [...extractedData.passengers]
                          newPassengers[index] = {...p, name: e.target.value}
                          setExtractedData({...extractedData, passengers: newPassengers})
                        }}
                        placeholder="Passenger name"
                      />
                      <Input
                        label="Age"
                        type="number"
                        value={p.age}
                        onChange={(e) => {
                          const newPassengers = [...extractedData.passengers]
                          newPassengers[index] = {...p, age: parseInt(e.target.value) || 0}
                          setExtractedData({...extractedData, passengers: newPassengers})
                        }}
                        placeholder="Age"
                      />
                      <Input
                        label="Coach"
                        value={p.coach}
                        onChange={(e) => {
                          const newPassengers = [...extractedData.passengers]
                          newPassengers[index] = {...p, coach: e.target.value}
                          setExtractedData({...extractedData, passengers: newPassengers})
                        }}
                        placeholder="e.g., B2"
                      />
                      <Input
                        label="Seat"
                        type="number"
                        value={p.seatNumber}
                        onChange={(e) => {
                          const newPassengers = [...extractedData.passengers]
                          newPassengers[index] = {...p, seatNumber: parseInt(e.target.value) || 0}
                          setExtractedData({...extractedData, passengers: newPassengers})
                        }}
                        placeholder="e.g., 45"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Gender</label>
                        <select
                          value={p.gender}
                          onChange={(e) => {
                            const newPassengers = [...extractedData.passengers]
                            newPassengers[index] = {...p, gender: e.target.value}
                            setExtractedData({...extractedData, passengers: newPassengers})
                          }}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="M">Male</option>
                          <option value="F">Female</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Berth Type</label>
                        <select
                          value={p.berthType}
                          onChange={(e) => {
                            const newPassengers = [...extractedData.passengers]
                            newPassengers[index] = {...p, berthType: e.target.value}
                            setExtractedData({...extractedData, passengers: newPassengers})
                          }}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          <option value="LB">Lower Berth (LB)</option>
                          <option value="MB">Middle Berth (MB)</option>
                          <option value="UB">Upper Berth (UB)</option>
                          <option value="SL">Side Lower (SL)</option>
                          <option value="SU">Side Upper (SU)</option>
                        </select>
                      </div>
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

